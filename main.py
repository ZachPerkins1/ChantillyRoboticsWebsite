import sys
import re
import os
import math
import json
import hashlib

sys.modules['_elementtree'] = None

from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import flask
import xml.etree.ElementTree as et
import redis
from os import listdir
from os.path import splitext

app = Flask(__name__)
r = redis.StrictRedis(host="barreleye.redistogo.com", port=11422, db=0, password="8fb344199bbb94235135457306928ef0")

app.config['SECRET_KEY'] = "hard to guess string"
app.config['UPLOAD_FOLDER'] = "images/"

ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif"]

app.jinja_env.autoescape = False

class LineNumberingParser(et.XMLParser):
    def _start_list(self, *args, **kwargs):
        # Here we assume the default XML parser which is expat
        # and copy its element position attributes into output Elements
        element = super(self.__class__, self)._start_list(*args, **kwargs)
        element._start_line_number = self.parser.CurrentLineNumber
        element._start_column_number = self.parser.CurrentColumnNumber
        element._start_byte_index = self.parser.CurrentByteIndex
        return element

    def _end(self, *args, **kwargs):
        element = super(self.__class__, self)._end(*args, **kwargs)
        element._end_line_number = self.parser.CurrentLineNumber
        element._end_column_number = self.parser.CurrentColumnNumber
        element._end_byte_index = self.parser.CurrentByteIndex
        return element


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
    
    
def gen_file_name(filename):
    i = 0
    name, ext = splitext(filename)
    
    filename = name + "_" + str(i) + ext
    while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
        i += 1
        filename = name + "_" + str(i) + ext
    
    return filename
    
    
def allowed_file(filename):
    for ext in ALLOWED_EXTENSIONS:
        if ext in filename:
            return True
    return False
    
    

def replace_tag(tag, line, replacement):
    """Replaces an HTML tag (such as <editable> or <var/>) in the given content with the given replacement.

    Params:
        tag - the HTML tag to replace
        line - the content in which to replace the tag
        replacement - the replacement string
    Returns:
        The replacement tag as a string (?).
    """
    r = re.compile("<" + tag + "[^<]*(/>|>)")
    return re.sub(r, replacement, line)


def gen_image_tag(attr, cname):
    """Generates an <img/> HTML tag from the given attribute, which is an image <editable> tag.

    Params:
        attr - the image <editable> attribute
        cname - a string version of the attribute name, in the form data["name"]
    Returns:
        The new <img/> tag as a string.
    """
    text = "<img src=\"{{ " + cname + " }}\""
    r = dict(attr)
    del r["name"]
    del r["type"]
    del r["display"]

    if "alt" not in r:
        r["alt"] = attr["display"]

    for key in r:
        text += " " + key + "=\"" + r[key] + "\""

    text += ">"
    return text
    

def getData(page, name):
    name_data = r.hgetall(page + ":names:" + name)

    if name_data["type"] == "list":
        name_data["data"] = []
        min_count = sys.maxint
        for var in r.smembers(page + ":list_index:" + name):
            list = r.hgetall(page + ":lists:" + name + ":" + var)
            list["data"] = r.lrange(page + ":lists:" + name + ":" + var + ":data", 0, -1)
            for i in range(len(list["data"])):
                list["data"][i] = list["data"][i].decode("UTF-8")
            if "display" in list:
                list["display"] = list["display"].decode("UTF-8")
            name_data["data"].append(list)
            min_count = min(min_count, len(list["data"]))
        
        name_data["count"] = min_count
    elif name_data["type"] == "text":
        name_data["data"] = name_data["data"].decode("UTF-8")
    name_data["display"] = name_data["display"].decode("UTF-8")
        
    return name_data


def process_list(content, e):
    """Processes a list. (Clarify!!).
        This method replaces <var type="text"/> tags in the list with the appropriate Jinja expressions.
        For some reason, images and lists are not supported.
    """
    vars = e.findall(".//var")
    for var in e.findall(".//var"):
        type = var.get("type")
        name = var.get("name")
        if type == "text":
            line = var._start_line_number - 1
            content[line] = replace_tag("var", content[line], "{{ item[\"" + name + "\"] }}")

    return vars


def gen_site():
    """Generates Jinja template files from front-end files in the home directory.
        This method is called before server startup.
    """
    print "Regenerating Templates..."
    files = listdir("templates")
    files = [fn for fn in files if fn.endswith(".html")]

    r.delete("name_index")

    if r.exists("pages"):
        r.delete("pages")

    for fn in files:
        print "Generating " + fn
        page_name = fn[:-5]
        r.sadd("pages", fn[:-5])
        tree = et.parse("templates/" + fn, parser=LineNumberingParser())
        root = tree.getroot()
        editables = root.findall(".//editable")

        content = None

        with open("templates/" + fn) as f:
            content = f.readlines()
            
        names = []

        # parses each editable tag and replaces with Jinja equivalents
        for e in editables:
            type = e.get("type")
            name = e.get("name")
            cname = "data[\"" + name + "\"]"

            top = e._start_line_number - 1
            bottom = e._end_line_number - 1

            d = dict(e.attrib)
            
            names.append(name)
            r.sadd(page_name + ":name_index", name)
            vars = None

            if type == "text":
                content[top] = replace_tag("editable", content[top], "{{ " + cname + " }}")
            elif type == "list":
                content[top] = replace_tag("editable", content[top], "{% for item in " + cname + " %}")
                vars = process_list(content, e)
                content[bottom] = replace_tag("/editable", content[bottom], "{% endfor %}")
            elif type == "image":
                line = gen_image_tag(e.attrib, cname)
                content[top] = replace_tag("editable", content[top], line)

            r.hmset(page_name + ":names:" + name, d)

            if type == "list":
                for var in vars:
                    r.sadd(page_name + ":list_index:" + name, var.get("name"))
                    r.hmset(page_name + ":lists:" + name + ":" + var.get("name"), var.attrib)
        
        for name in r.smembers(page_name + ":name_index"):
            if name not in names:
                r.srem(page_name + ":name_index", name)
        
        path = "templates/gen/" + fn

        if os.path.isfile(path):
            os.remove(path)

        del content[0]
        content[-1] = "{% endblock %}"

        top_text = [
            "{% extends \"blocks/layout.html\" %}\n",
            "{% set page_name = \"" + root.get("name") + "\" %}\n",
            "{% block content %}\n"
        ]

        content = top_text + content

        with open(path, "w") as f:
            for line in content:
                f.write(line)


@app.route("/admin/edit-page/<page>")
def edit_page(page):
    """Generates and returns an "edit page" page for the given page.
        Admins use these pages to add content to the website.
    """
    names = r.smembers(page + ":name_index")
    lists = []
    texts = []
    images = []

    for name in names:
        name_data = getData(page, name)
        if name_data["type"] == "text":
            texts.append(name_data)
        elif name_data["type"] == "list":
            lists.append(name_data)
        elif name_data["type"] == "image":
            images.append(name_data)            

    page_data = {
        "lists": lists,
        "texts": texts,
        "images": images,
        "page_name": page
    }

    return render_template("admin/edit-page.html", data=page_data)
    
@app.route("/admin/save-data", methods=['POST'])
def save():
    lists = json.loads(request.form.get("list"))
    texts = json.loads(request.form.get("text"))
    images = json.loads(request.form.get("image"))
    page = request.form.get("page_name")
    print lists
    #test = request.form.get("test", "", type=str)
    
   # print test

    print page
    

    for name in texts:
        r.hmset(page + ":names:" + name, texts[name])
    for name in images:
        r.hmset(page + ":names:" + name, images[name])         
    for name in lists:
        for var in lists[name]:
            r.delete(page + ":lists:" + name + ":" + var + ":data")
            for item in lists[name][var]["data"]:
                r.rpush(page + ":lists:" + name + ":" + var + ":data", item)
                
    return jsonify(name="Hello")


@app.route("/")
def home():
    """Renders the home page"""
    return default("index")


@app.route("/<path:path>")
def default(path):
    """The render function used for normal web pages on the site (such as the home page, About page, etc.)"""
    if r.sismember("pages", path):
        data = {}
        names = r.smembers(path+ ":name_index")
        for name in names:
            name_data = getData(path, name)
            if name_data["type"] == "text" or name_data["type"] == "image":
                data[name] = name_data["data"]
            if name_data["type"] == "list":
                lists = []
                for i in range(name_data["count"]):
                    item = {}
                    x = 0
                    for var in name_data["data"]:
                        print name_data["data"][x]
                        item[var["name"]] = name_data["data"][x]["data"][i]
                        x += 1
                        
                    lists.append(item)
                    
                data[name] = lists
                    
           
        data["page"] = path
        
        print data
            
        return render_template("gen/" + path + ".html", data=data)
        
@app.route("/admin/upload-image", methods=['POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        
        uploaded_file_path = None

        if file:
            filename = secure_filename(file.filename)
            filename = gen_file_name(filename)
            mime_type = file.content_type

            if not allowed_file(file.filename):
                #result = uploadfile(name=filename, type=mime_type, size=0, not_allowed_msg="File type not allowed")
                pass

            else:
                # save file to disk
                name, ext = splitext(filename)
                temp_name = "temp" + ext
                uploaded_file_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_name)
                file.save(uploaded_file_path)
                
                hash_new = md5(uploaded_file_path)
                
                found = False
                images = r.smembers("image_index")
                for image in images:
                    if r.get("images:" + image) == hash_new:
                        filename = image + ext
                        os.remove(uploaded_file_path)
                        found = True
                        break
                
                temp_file_path = uploaded_file_path
                uploaded_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                if not found:
                    os.rename(temp_file_path, uploaded_file_path)
                    r.sadd("image_index", name)
                    r.set("images:" + name, hash_new)
                    
            
            return jsonify(name=uploaded_file_path)

print "Server Starting..."
gen_site()
app.run(debug=True, port=int(os.getenv('PORT', '8080')), host=os.getenv('IP', '0.0.0.0'))
