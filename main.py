from flask import Flask, render_template
from xml.dom import minidom
import xml.etree.ElementTree
import redis
from os import listdir

app = Flask(__name__)
r = redis.StrictRedis(host="barreleye.redistogo.com", port=11422, db=0, password="8fb344199bbb94235135457306928ef0")
print r.get("test")
r.delete("querty")
r.hmset("querty", {"label": "value", "label2": "value2"})
print r.hgetall("querty")

def gen_site():
    files = listdir("templates/originals")



@app.route("/")
def home():
    return render_template("index.html")


@app.route("/about-us")
def about_us():
    return render_template("about-us.html")


@app.route("/about-first")
def about_first():
    return render_template("about-first.html")


@app.route("/outreach")
def outreach():
    return render_template("outreach.html")


@app.route("/resources")
def resources():
    return render_template("resources.html")


@app.route("/sponsors")
def sponsors():
    return render_template("sponsors.html")

gen_site()
app.run(debug=True)
