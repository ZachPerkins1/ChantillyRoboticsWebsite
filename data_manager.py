import xml.etree.ElementTree as et
import re
import os
import sys
import json

from flask import jsonify

_datatypes = {}
_db = None


def init(database):
    global _db
    _db = database
    
    
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
    

class Tag(object):
    def __init__(self):
        pass
    
    def format_before_sending(self, data):
        return data
        
    def format_before_saving(self, data):
        n_data = json.dumps(data)
        return n_data
        
    def _get_empty(self):
        d = {}
        d["_admin"] = {}
        d["value"] = ""
        self.get_empty(d)
        return d

    def get_empty(self, data):
        pass
    
    def fill_line(self, data):
        raise NotImplementedError("Must implement fill line for datatype")
        
    def return_tag_name(self):
        raise NotImplementedError("Must implement return tag name for datatype")
        
    def return_display_name(self):
        raise NotImplementedError("Must implement return display name for datatype")
    
    def can_be_in_list(self):
        raise NotImplementedError("Must implement can be in list for datatype")
        
        
def add_tag(tag):
    global datatypes
    name = tag.return_tag_name()
    _datatypes[name] = tag
    
    
def get_tags():
    return _datatypes
    
    
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
    

def gen_site():
    """Generates Jinja template files from front-end files in the home directory.
        This method is called before server startup.
    """
    print "Regenerating Templates..."
    files = os.listdir("templates")
    files = [fn for fn in files if fn.endswith(".html")]

    if _db.exists("page_index"):
        _db.delete("page_index")

    for fn in files:
        print "Generating " + fn
        page_name = fn[:-5]
        _db.sadd("page_index", fn[:-5])
        tree = et.parse("templates/" + fn, parser=LineNumberingParser())
        root = tree.getroot()
        editables = root.findall(".//editable")
        
        old_index = None
        
        if _db.exists(page_name + ":name_index"):
            old_index = _db.smembers(page_name + ":name_index")
            _db.delete(page_name + ":name_index")

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
            _db.sadd(page_name + ":name_index", name)
            vars = None
            
            if type == "list":
                content[top] = replace_tag("editable", content[top], "{% for item in " + cname + " %}")
                vars = process_list(page_name, content, e)
                content[bottom] = replace_tag("/editable", content[bottom], "{% endfor %}")
            elif type in _datatypes:
                name_info = dict(page=page_name, name=cname, attr=e.attrib)
                content[top] = replace_tag("editable", content[top], _datatypes[type].fill_line(name_info).replace("{name}", cname))
            
                if not _db.hexists(page_name + ":names:" + name, "data"):
                    create_blank_data(d)
                    
            _db.hmset(page_name + ":names:" + name, d)

            if type == "list":
                for var in vars:
                    _db.sadd(page_name + ":list_index:" + name, var.get("name"))
                    
                    v = dict(var.attrib)
                    
                    if not _db.hexists(page_name + ":lists:" + name + ":" + var.get("name"), "data"):
                        create_blank_data(v)
                    
                    _db.hmset(page_name + ":lists:" + name + ":" + var.get("name"), v)
        
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


def get_data(page, name):
    name_data = _db.hgetall(page + ":names:" + name)
    print name_data

    if name_data["type"] == "list":
        name_data["data"] = []
        min_count = sys.maxint
        for var in _db.smembers(page + ":list_index:" + name):
            list = _db.hgetall(page + ":lists:" + name + ":" + var)
            raw_data = _db.lrange(page + ":lists:" + name + ":" + var + ":data", 0, -1)
            list["data"] = []
            for val in raw_data:
                list["data"].append(_datatypes[list["type"]].format_before_sending(val))
            if "display" in list:
                list["display"] = list["display"].decode("UTF-8")
            if "type" in list:
                list["type"] = list["type"].decode("UTF-8")
            name_data["data"].append(list)
            min_count = min(min_count, len(list["data"]))
        
        name_data["count"] = min_count
    else:
        name_data["data"] = _datatypes[name_data["type"]].format_before_sending(name_data["data"])
        
    name_data["display"] = name_data["display"].decode("UTF-8")
        
    return name_data
    
    
def create_blank_data(curr):
    curr["data"] = json.dumps(_datatypes[curr["type"]]._get_empty()).decode("UTF-8")


def process_list(page_name, content, e):
    """Processes a list. (Clarify!!).
        This method replaces <var type="text"/> tags in the list with the appropriate Jinja expressions.
        For some reason, images and lists are not supported.
    """
    vars = e.findall(".//var")
    for var in vars:
        type = var.get("type")
        name = var.get("name")
        cname = "item['" + name + "']"
        
        line = var._start_line_number - 1
        if type in _datatypes and _datatypes[type].can_be_in_list():
            name_info = dict(page=page_name, name=cname, attr=var.attrib)
            content[line] = replace_tag("var", content[line], _datatypes[type].fill_line(name_info)).replace("{name}", cname)
            

    return vars