import sys
import re
import math
import json
import redis
import flask
import os
import types

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
types.add_tags()

@app.route("/admin/edit-page/<page>")
def edit_page(page):
    """Generates and returns an "edit page" page for the given page.
        Admins use these pages to add content to the website.
    """
    names = r.smembers(page + ":name_index")
    data = {}
    
    for key in dmanager.get_tags():
        data[key] = []

    for name in names:
        name_data = dmanager.get_data(page, name)
        data[name_data["type"]].append(name_data)

    page_data = {
        "data": data,
        "page_name": page
    }
    
    return render_template("admin/edit-page.html", data=page_data)
    
@app.route("/admin/save-data", methods=['POST'])
def save():
    data = json.loads(request.form.get("data"))
    page = request.form.get("page_name")
    
    
    for key in data:
        if key == "list":
            for name in data["lists"]:
                for var in data["lists"]["name"]:
                    r.delete(page + ":lists:" + name + ":" + var + ":data")
                    for item in data["lists"][name][var]["data"]:
                        r.rpush(page + ":lists:" + name + ":" + var + ":data", item)
        else:
            for item in data[key]:
                r.hmset(page + ":names:" + name, data[key][name])

                
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
gen_site()
app.run(debug=True, port=int(os.getenv('PORT', '8080')), host=os.getenv('IP', '0.0.0.0'))
