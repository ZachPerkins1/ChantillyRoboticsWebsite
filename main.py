import sys
import re
import os
import math

sys.modules['_elementtree'] = None

from flask import Flask, render_template
import flask
import xml.etree.ElementTree as et
import redis
from os import listdir

app = Flask(__name__)
r = redis.StrictRedis(host="barreleye.redistogo.com", port=11422, db=0, password="8fb344199bbb94235135457306928ef0")

app.jinja_env.autoescape = False

r.delete("about-us:lists:mentors:mentor_name:data")
r.delete("about-us:lists:mentors:mentor_desc:data")

r.lpush("about-us:lists:mentors:mentor_name:data", "joe")
r.lpush("about-us:lists:mentors:mentor_name:data", "dave")

r.lpush("about-us:lists:mentors:mentor_desc:data", "good mentor")
r.lpush("about-us:lists:mentors:mentor_desc:data", "bad mentor")



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

        # parses each editable tag and replaces with Jinja equivalents
        for e in editables:
            type = e.get("type")
            name = e.get("name")
            cname = "data[\"" + name + "\"]"

            top = e._start_line_number - 1
            bottom = e._end_line_number - 1

            d = dict(e.attrib)

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

    for name in names:
        name_data = r.hgetall(page + ":names:" + name)
        if name_data["type"] == "text":
            texts.append(name_data)
        elif name_data["type"] == "list":
            name_data["data"] = []
            min_count = sys.maxint
            for var in r.smembers(page + ":list_index:" + name):
                list = r.hgetall(page + ":lists:" + name + ":" + var)
                list["data"] = r.lrange(page + ":lists:" + name + ":" + var + ":data", 0, -1)
                name_data["data"].append(list)
                min_count = min(min_count, len(list["data"]))
            
            name_data["count"] = min_count
            lists.append(name_data)
            print name_data

    page_data = {
        "lists": lists,
        "texts": texts
    }

    return render_template("admin/edit-page.html", data=page_data)


@app.route("/")
def home():
    """Renders the home page"""
    return default("index")


@app.route("/<path:path>")
def default(path):
    """The render function used for normal web pages on the site (such as the home page, About page, etc.)"""
    if r.sismember("pages", path):
        return render_template("gen/" + path + ".html", data={}, pg=path)

print "Server Starting..."
gen_site()
app.run(debug=True, port=int(os.getenv('PORT', '8080')), host=os.getenv('IP', '0.0.0.0'))
