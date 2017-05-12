import sys

sys.modules['_elementtree'] = None

from flask import Flask
import redis

app = Flask(__name__)
r = redis.StrictRedis(host="barreleye.redistogo.com", port=11422, db=0, password="8fb344199bbb94235135457306928ef0")

app.config['SECRET_KEY'] = "hard to guess string"
app.config['UPLOAD_FOLDER'] = "static/usr_img/"

app.jinja_env.autoescape = False
