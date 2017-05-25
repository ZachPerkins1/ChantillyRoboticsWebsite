import sys
import re
import math
import json
import redis
import flask
import os
from datatypes import add_tags

from flask import Flask, render_template, request, jsonify, make_response, redirect

import data_manager as dmanager
import image_manager as imanager
import sessions as sess

sys.modules['_elementtree'] = None

app = Flask(__name__)
r = redis.StrictRedis(host="barreleye.redistogo.com", port=11422, db=0, password="8fb344199bbb94235135457306928ef0")
previews = {}

app.config['SECRET_KEY'] = "hard to guess string"
app.config['UPLOAD_FOLDER'] = "static/usr_img/"

ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif"]


app.jinja_env.autoescape = False

imanager.init(app.config['UPLOAD_FOLDER'], r)
dmanager.init(r)
sess.init(r)
add_tags()

@app.route("/admin/edit-page/<page>")
def edit_page(page):
    """Generates and returns an "edit page" page for the given page.
        Admins use these pages to add content to the website.
    """
    names = r.smembers(page + ":name_index")
    data = {}
    lists = []
    type_info = {}
    
    for key in dmanager.get_tags():
        data[key] = []
        type_info[key] = {}
        type_info[key]["display"] = dmanager._datatypes[key].return_display_name()
        type_info[key]["empty"] = dmanager._datatypes[key]._get_empty({})

    for name in names:
        name_data = dmanager.get_data(page, name)
        if name_data["type"] == "list":
            lists.append(name_data)
        else:
            data[name_data["type"]].append(name_data)
    

    page_data = {
        "static_elements": data,
        "type_info": type_info,
        "page_name": page,
        "list_elements": lists
    }
    
    return render_template("admin/edit-page.html", data=page_data)
    
@app.route("/admin/save-data", methods=['POST'])
def save():
    static = json.loads(request.form.get("static_elements"))
    lists = json.loads(request.form.get("list_elements"))
    page = request.form.get("page_name")
    
    for key in lists:
        for name in lists:
            for var in lists[name]:
                r.delete(page + ":lists:" + name + ":" + var + ":data")
                for item in lists[name][var]["data"]:
                    r.rpush(page + ":lists:" + name + ":" + var + ":data", dmanager.get_tags()[lists[name][var]["type"]].format_before_saving(item))
            
    for key in static:
        for name in static[key]["data"]:
            static[key]["data"][name]["data"] = dmanager.get_tags()[key].format_before_saving(static[key]["data"][name]["data"])
            r.hmset(page + ":names:" + name, static[key]["data"][name])

                
    return jsonify(name="Hello")
    
@app.route("/admin/preview-loading")
def preview_loading():
    return render_template("blocks/loading-preview.html")
    
@app.route("/admin/gen-preview", methods=['POST'])
def gen_preview():
    static_data = json.loads(request.form.get("static_elements"))
    list_data = json.loads(request.form.get("list_elements"))
    page = request.form.get("page_name")
    
    data = {}
    
    print previews
    
    uid = 0
    while uid in previews:
        uid += 1
        

    names = r.smembers(page + ":name_index")
    for name in names:
        if name in list_data:
            name_data = list_data[name]
            lists = []
            for i in range(len(name_data[name_data.keys()[0]]["data"])):
                item = {}
                for var in name_data:
                    item[var] = name_data[var]["data"][i]

                    
                lists.append(item)
                
            data[name] = lists
        else:
            for key in static_data:
                if name in static_data[key]["data"]:
                    data[name] = static_data[key]["data"][name]["data"]
                    
    previews[uid] = {
        "page": page,
        "data": data
    }
    
    return jsonify(uid=uid)
    
@app.route("/admin/rm-preview", methods=['POST'])
def rm_preview():
    uid = int(request.form.get("uid"))
    try:
        del previews[uid]
    except:
        pass
    
    return "success"
    
    
@app.route("/admin/preview/<int:uid>")
def preview(uid):
    try:
        path = previews[uid]["page"]
        data = previews[uid]["data"]
        return render_template("gen/" + path + ".html", data=data, uid=uid, layout="blocks/preview-layout.html")
    except:
        return render_template("blocks/not-found.html"), 404



@app.route("/")
def home():
    """Renders the home page"""
    return default("index")



@app.route("/<path:path>")
def default(path):
    """The render function used for normal web pages on the site (such as the home page, About page, etc.)"""
    if r.sismember("page_index", path):
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
                        item[var["name"]] = json.loads(name_data["data"][x]["data"][i])
                        x += 1

                        
                    lists.append(item)
                    
                data[name] = lists
            else:
                data[name] = json.loads(name_data["data"])
                    
        data["page"] = path
        
        return render_template("gen/" + path + ".html", data=data, layout="blocks/layout.html")
        
    else:
        return render_template("blocks/not-found.html"), 404


@app.route("/admin/upload-image", methods=['POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        res = imanager.upload(file)
        return jsonify(res)
        
        
@app.route("/admin/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("admin/login.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        
        errs, session = sess.login_user(username, password)

        resp = None
        
        if errs.any():
            resp = make_response(render_template("admin/login.html", errors=errs.get_formatted(), cached_data=request.form))
        else:
            resp = make_response(redirect("admin/home"))
            resp.set_cookie("s_id", str(session.get_id()))
            resp.set_cookie("s_key", session.get_key())
    
    return resp
    
    
@app.route("/admin/register", methods=['GET', 'POST'])
def register():
    if request.method == "GET":
        return render_template("admin/register.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        confirm = request.form.get("confirm")
        
        print username
        
        errs, session = sess.create_session_user(username, email, password, confirm)

        resp = None
        
        if errs.any():
            resp = make_response(render_template("admin/register.html", errors=errs.get_formatted(), cached_data=request.form))
        else:
            resp = make_response(redirect("admin/home"))
            resp.set_cookie("s_id", str(session.get_id()))
            resp.set_cookie("s_key", session.get_key())
            
        return resp
    


print "Server Starting..."
dmanager.gen_site()
app.run(debug=True, port=int(os.getenv('PORT', '8080')), host=os.getenv('IP', '0.0.0.0'))
