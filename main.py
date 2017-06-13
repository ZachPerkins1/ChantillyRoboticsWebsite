import sys
import re
import math
import json
import redis
import flask
import os
from datatypes import add_tags

from flask import Flask, render_template, request, jsonify, make_response, redirect, url_for
from flask_mail import Mail, Message

import data_manager as dmanager
import image_manager as imanager
import sessions as sess

sys.modules['_elementtree'] = None

app = Flask(__name__)
r = redis.StrictRedis(host="barreleye.redistogo.com", port=11422, db=0, password="8fb344199bbb94235135457306928ef0")
previews = {}

app.config['UPLOAD_FOLDER'] = "static/usr_img/"

ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif"]

ADDRESS = "http://localhost:8080/"
EMAIL = "chantillyrobotics.612.org@gmail.com"

# email configuration
# obviously temporary
app.config['MAIL_SERVER'] = "smtp.gmail.com"
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = EMAIL
app.config['MAIL_PASSWORD'] = "Hug2NXLu"
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

app.jinja_env.autoescape = False

imanager.init(app.config['UPLOAD_FOLDER'], r)
dmanager.init(r)
sess.init(r)
add_tags()

@app.route("/admin/edit-page/<page>")
def edit_page(page):
    success, session = sess.check_session_quick(request)

    if not success:
        return redirect(url_for("login", redirect="/admin/edit-page/" + page))

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

    return render_template("admin/edit-page.html", data=page_data, user_name=session.get_user().get_name())

@app.route("/admin/save-data", methods=['POST'])
def save():
    if not sess.check_session_quick(request)[0]:
        return jsonify(success=False)

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


    return jsonify(success=True)

@app.route("/admin/preview-loading")
def preview_loading():
    return render_template("blocks/loading-preview.html")

@app.route("/admin/gen-preview", methods=['POST'])
def gen_preview():
    if not sess.check_session_quick(request)[0]:
        return jsonify(success=False)

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

    return jsonify(uid=uid, success=True)

@app.route("/admin/rm-preview", methods=['POST'])
def rm_preview():
    if not sess.check_session_quick(request)[0]:
        return redirect("/admin/login")

    uid = int(request.form.get("uid"))
    try:
        del previews[uid]
    except:
        pass

    return "success"


@app.route("/admin/preview/<int:uid>")
def preview(uid):
    if not sess.check_session_quick(request)[0]:
        return redirect(url_for("login", redirect="/admin/preview/" + str(uid)))

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

@app.route("/admin")
def admin():
    return redirect("/admin/home")


@app.route("/admin/upload-image", methods=['POST'])
def upload():
    if not sess.check_session_quick(request)[0]:
        return jsonify(success=False)

    file = request.files['file']
    res = imanager.upload(file)
    res["success"] = True
    return jsonify(res)


@app.route("/admin/home")
def admin_home():
    success, session = sess.check_session_quick(request)
    if not success:
        return redirect("/admin/login")

    pages = r.smembers("page_index")
    user = session.get_user()

    return render_template("admin/home.html", pages=pages, name=user.get("first-name"), user_data=user.get_all(), user_name=user.get_name(), access_level=user.get_level())


@app.route("/admin/edit-user", methods=['POST'])
def edit_user():
    success, session = sess.check_session_quick(request)
    if success:
        errs = sess.update_user(session, request.form)
        return jsonify(errors=errs.get_formatted(), success=True)
    else:
        return jsonify(success=False)


@app.route("/admin/logout")
def logout():
    success, session = sess.check_session_quick(request)
    if success:
        session.delete()

    return redirect("/admin/login")


@app.route("/admin/login", methods=['GET', 'POST'])
def login():
    re = request.args.get("redirect", "/admin/home")

    if request.method == 'GET':
        if sess.check_session_quick(request)[0]:
            return redirect("/admin/home")
        return render_template("admin/login.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")

        errs, session = sess.login_user(username, password)

        resp = None

        if errs.any():
            resp = make_response(render_template("admin/login.html", errors=errs.get_formatted(), cached_data=request.form))
        else:
            resp = make_response(redirect(re))
            resp.set_cookie("s_id", str(session.get_id()))
            resp.set_cookie("s_key", session.get_key())

    return resp


@app.route("/admin/register", methods=['GET', 'POST'])
def register():
    """
    Redirects the user to the registration page only if a valid code is present. Codes are
    generated by high level users.
    """
    if request.method == "GET":
        code = request.args.get("reg-code", "")
        if code == "":
            return redirect("/admin/login")

        return render_template("admin/register.html", reg_code=code)
    else:
        errs, session = sess.create_session_user(request.form)

        resp = None

        if errs.any():
            resp = make_response(render_template("admin/register.html", errors=errs.get_formatted(), cached_data=request.form))
        else:
            resp = make_response(redirect("admin/home"))
            resp.set_cookie("s_id", str(session.get_id()))
            resp.set_cookie("s_key", session.get_key())

        return resp


@app.route("/admin/user-manager", methods=['GET', 'POST'])
def user_manager():
    def format_user_list():
        user_index = r.smembers("user_index")

        users = {}
        for username in user_index:
            u = sess.User.from_existing(username)
            users[username] = dict(u.get_all())
            users[username]["_online"] = "No"
            for key, session in sess.sessions.iteritems():
                if session.get_user(passive=True).get_name() == username:
                    users[username]["_online"] = "Yes"
                    break

        return users

    if request.method == "GET":
        success, session = sess.check_session_quick(request, 1)

        if not success:
            return redirect(url_for("login", redirect="/admin/user-manager"))
        return render_template("admin/user-list.html", users=format_user_list(), user_name=session.get_user().get_name())
    else:
        success, session = sess.check_session_quick(request, 1)

        if not success:
            return redirect(url_for("login", redirect="/admin/user-manager"))

        user = session.get_user()


        if user.get_level() > int(request.form.get("level")):
            return render_template("admin/user-list.html",
                users=format_user_list(),
                user_name=user.get_name(),
                errors=["You cannot create users at a greater level than you"]
            )

        data = { key:request.form[key] for key in request.form }
        if data.get("time-unit") == "m":
            print data["expiry"]
            data["expiry"] = float(data["expiry"]) * 60
        else:
            data["expiry"] = float(data["expiry"]) * 60 * 60


        errs, registration = sess.create_registration(data)

        if errs.any():
            return render_template("admin/user-list.html",
                users=format_user_list(),
                user_name=user.get_name(),
                errors=errs.get_formatted()
            )

        print registration.get_reg_code()

        # send email with link embedded
        global ADDRESS
        global EMAIL
        global mail

        m = Message("User Registration Information", sender = EMAIL, recipients = [data['email']])
        # TODO: maybe load html from some template?
        m.html = """<h2>Chantilly Robotics</h2>
        <p>If you are receiving this email, you have been invited to receive super-user privileges on chantillyrobotics.org</p>
        <p>Click <a href=\"""" + ADDRESS + "admin/register?reg-code=" + str(registration.get_reg_code()) + """\">here</a></p>
        <p>If you believe this to be an error please contact a system administrator</p>
        """
        mail.send(m)

        return render_template("admin/user-list.html",
            users=format_user_list(),
            user_name=user.get_name(),
            errors=[]
        )


@app.route("/admin/user/<name>")
def user(name):
    access_text = [
        "Developer",
        "Super admin",
        "Admin"
    ]

    success, session = sess.check_session_quick(request, 1)
    if success:
        if sess.user_exists(name):
            curr_user = session.get_user()
            u = sess.User.from_existing(name)
            user_data = u.get_all()
            user_data["_f_access_level"] = access_text[u.get_level()]
            return render_template("admin/user.html", user_data=u.get_all(), user_name=curr_user.get_name())

    return render_template("blocks/not-found.html"), 404


@app.route("/admin/del-user", methods=['POST'])
def delete_user():
    success, session = sess.check_session_quick(request, 1)
    if not success:
        return jsonify(success=False, error="You do not have permission to perform this action")

    sess.remove_user(request.form.get("name", ""))

    return jsonify(success=True)

@app.route("/admin/suspend-user", methods=['POST'])
def suspend_user():
    success, session = sess.check_session_quick(request, 1)
    if not success:
        return jsonify(success=False, error="You do not have permission to perform this action")

    username = request.form.get("name", "")

    if sess.user_exists(username):
        user = sess.User.from_existing(username)
        user.suspend(int(request.form.get("time", 0)))
        user.push_data()
        print user.get_all()

    return jsonify(success=True)

@app.route("/admin/helen")
def helen():
    return "This webpage is plain, boring, and goes unoticed just like <a href='https://instagram.com/woshixiaoqing'>Helen</a>."


print "Server Starting..."
dmanager.gen_site()
app.run(debug=True, port=int(os.getenv('PORT', '8080')), host=os.getenv('IP', '0.0.0.0'))
