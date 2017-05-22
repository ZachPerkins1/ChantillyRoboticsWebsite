from data_manager import Tag
from data_manager import add_tag


def add_tags():
    add_tag(Text())
    add_tag(Image())
    add_tag(Variable())
    

class Text(Tag):
    def fill_line(self, data):
        return "{{ {name}['value'] }}"
        
    def return_tag_name(self):
        return "text"
        
    def return_display_name(self):
        return "Text"
        
    def can_be_in_list(self):
        return True
        

class Image(Tag):
    def fill_line(self, data):
        attr = data["attr"]
        text = "<img src=\"{{ url_for('static', filename='usr_img/' + {name}['value']) }}\""
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
        
    def get_empty(self, data, attr):
        data["value"] = "fruits_0.jpg"
        
    def return_tag_name(self):
        return "image"
        
    def return_display_name(self):
        return "Image"
        
    def can_be_in_list(self):
        return True

class Variable(Tag):
    def fill_line(self, data):
        fill_text = "{{ {name}['value'] }}"
        var_type = "string"
        if "var-type" in data["attr"]:
            var_type = data["attr"]["var-type"].lower()
            
        if var_type == "string":
            fill_text = "\"" + fill_text + "\""
        elif var_type == "date":
            fill_text = "new Date(\"" + fill_text + "\")"
    
        return "<script>var " + data["attr"]["name"] + " = " + fill_text + ";</script>"
        
    def get_empty(self, data, attr):
        var_type = "string"
        if "var-type" in attr:
            var_type = attr["var-type"].lower()
            
        if var_type == "int":
            data["value"] = "0"
        elif var_type == "date":
            data["value"] = "Sat, 01 Jan 2000 00:00:00 GMT"
        
    def return_tag_name(self):
        return "variable"
        
    def return_display_name(self):
        return "Variable"
        
    def can_be_in_list(self):
        return False
