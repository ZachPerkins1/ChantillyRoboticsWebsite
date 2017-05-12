import sys
from flask import render_template
from env import app, r
    

def get_data(page, name):
    """Retrieves a data object from the server for rendering to the client.

    Params:
        page - the name of the page to render
        name - the data object to retrieve data for
    Returns:
        The named data object
    """
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
            else:
                list["display"] = list["name"]
            name_data["data"].append(list)
            min_count = min(min_count, len(list["data"]))
        
        name_data["count"] = min_count
    elif name_data["type"] == "text":
        name_data["data"] = name_data["data"].decode("UTF-8")
    if "display" in name_data:
        name_data["display"] = name_data["display"].decode("UTF-8")
    else:
        name_data["display"] = name_data["name"]
        
    return name_data


@app.route("/")
def home():
    """Renders the home page"""
    return default("index")


@app.route("/<path:path>")
def default(path):
    """The render function used for normal web pages on the site (such as the home page, About page, etc.)

    Params:
        path - the name of the page to render
    Returns:
        If the page is valid: HTTP 200 with the page
        Else: HTTP 404 with the 404 page
    """
    if r.sismember("pages", path):
        data = {}
        names = r.smembers(path+ ":name_index")
        for name in names:
            name_data = get_data(path, name)
            if name_data["type"] == "text" or name_data["type"] == "image":
                data[name] = name_data["data"]
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
                    
           
        data["page"] = path
        
        return render_template("gen/" + path + ".html", data=data)
    else:
        return render_template("blocks/not-found.html"), 404