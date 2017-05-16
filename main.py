import sys
import re
import math
import json
import redis
import flask
import os
from datatypes import add_tags

from flask import Flask, render_template, request, jsonify

import data_manager as dmanager
import image_manager as imanager

sys.modules['_elementtree'] = None


app = Flask(__name__)
r = redis.StrictRedis(host="barreleye.redistogo.com", port=11422, db=0, password="8fb344199bbb94235135457306928ef0")

app.config['SECRET_KEY'] = "hard to guess string"
app.config['UPLOAD_FOLDER'] = "static/usr_img/"

ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif"]


app.jinja_env.autoescape = False

imanager.init(app.config['UPLOAD_FOLDER'], r)
dmanager.init(r)
add_tags()

@app.route("/admin/edit-page/<page>")
def edit_page(page):
    """Generates and returns an "edit page" page for the given page.
        Admins use these pages to add content to the website.
    """
    names = r.smembers(page + ":name_index")
    data = {}
    lists = []
    displays = {}
    
    for key in dmanager.get_tags():
        data[key] = []
        displays[key] = dmanager._datatypes[key].return_display_name()

    for name in names:
        name_data = dmanager.get_data(page, name)
        if name_data["type"] == "list":
            lists.append(name_data)
            print name_data
        else:
            data[name_data["type"]].append(name_data)

    page_data = {
        "data": data,
        "display_names": displays,
        "page_name": page,
        "list_elements": lists
    }
    
    return render_template("admin/edit-page.html", data=page_data)
    
@app.route("/admin/save-data", methods=['POST'])
def save():
    static = json.loads(request.form.get("static_elements"))
    lists = json.loads(request.form.get("list_elements"))
    page = request.form.get("page_name")
    
    print lists
    print static
    
    for key in lists:
        for name in lists:
            for var in lists[name]:
                r.delete(page + ":lists:" + name + ":" + var + ":data")
                for item in lists[name][var]["data"]:
                    r.rpush(page + ":lists:" + name + ":" + var + ":data", item)
            
    for key in static:
        for name in static[key]["data"]:
            print name
            r.hmset(page + ":names:" + name, static[key]["data"][name])

                
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
            name_data = dmanager.get_data(path, name)
            
            if name_data["type"] == "list":
                lists = []
                for i in range(name_data["count"]):
                    item = {}
                    x = 0
                    for var in name_data["data"]:
                        item[var["name"]] = name_data["data"][x]["data"][i]
                        x += 1
                        
                    lists.append(item)
                    
                data[name] = lists
            else:
                data[name] = name_data["data"]
                    
        data["page"] = path
        
        return render_template("gen/" + path + ".html", data=data)
        
    else:
        return render_template("blocks/not-found.html"), 404


@app.route("/admin/upload-image", methods=['POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        res = imanager.upload(file)
        return jsonify(res)


print "Server Starting..."
dmanager.gen_site()
app.run(debug=True, port=int(os.getenv('PORT', '8080')), host=os.getenv('IP', '0.0.0.0'))
