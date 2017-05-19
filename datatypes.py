from data_manager import Tag
from data_manager import add_tag


def add_tags():
    add_tag(Text())
    add_tag(Image())
    

class Text(Tag):
    def fill_line(self, data):
        return "{{ {name}['value'] }"
        
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
        
    def return_tag_name(self):
        return "image"
        
    def return_display_name(self):
        return "Image"
        
    def can_be_in_list(self):
        return True
        