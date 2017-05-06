import sys
import re
import os
import math
import json

sys.modules['_elementtree'] = None

from flask import Flask, render_template, request
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
    r = re.compile("<" + tag + "[^<]*(/>|>)")
    return re.sub(r, replacement, line)


def gen_image_tag(attr, cname):
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
    vars = e.findall(".//var")
    for var in e.findall(".//var"):
        type = var.get("type")
        name = var.get("name")
        if type == "text":
            line = var._start_line_number - 1
            content[line] = replace_tag("var", content[line], "{{ item[\"" + name + "\"] }}")

    return vars


def gen_site():
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
            "{% extends \"layout.html\" %}\n",
            "{% set page_name = \"" + root.get("name") + "\" %}\n",
            "{% block content %}\n"
        ]

        content = top_text + content

        with open(path, "w") as f:
            for line in content:
                f.write(line)


@app.route("/admin/edit-page/<page>")
def edit_page(page):
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
        "texts": texts,
        "page_name": page
    }

    return render_template("admin/edit-page.html", data=page_data)
    
@app.route("/admin/save-data", methods=['POST'])
def save():
    lists = json.loads(request.form.get("lists"))
    texts = json.loads(request.form.get("texts"))
    page = request.form.get("page_name")
    print texts
    #test = request.form.get("test", "", type=str)
    
   # print test

    print page

    for name in texts:
        r.hmset(page + ":names:" + name, texts[name]) 
    #for name in lists:
    #    for var in lists[name]:
    #        r.delete(page + ":lists:" + name + ":" + var + ":data")
    #        for item in lists[name][var]["data"]:
    #            r.lpush(page + ":lists:" + name + ":" + var + ":data", item)
                
    return "hello";


@app.route("/<path:path>")
def default(path):
    if r.sismember("pages", path):
        return render_template(path + ".html")

print "Server Starting..."
gen_site()
app.run(debug=True, port=int(os.getenv('PORT', '8080')), host=os.getenv('IP', '0.0.0.0'))
