import json
import os
from os.path import splitext
from flask import render_template, request, jsonify
from werkzeug.utils import secure_filename
from env import app, r
from pagelink import get_data
import image


@app.route("/admin/edit-page/<page>")
def edit_page(page):
    """Generates and returns an "edit page" page for the given page.
        Admins use these pages to add content to the website.

    Params:
        page - the name of the page to generate
    Returns:
        A page for editing the given page
    """
    names = r.smembers(page + ":name_index")
    lists = []
    texts = []
    images = []

    for name in names:
        name_data = get_data(page, name)
        if name_data["type"] == "text":
            texts.append(name_data)
        elif name_data["type"] == "list":
            lists.append(name_data)
        elif name_data["type"] == "image":
            images.append(name_data)            

    page_data = {
        "lists": lists,
        "texts": texts,
        "images": images,
        "page_name": page
    }
    
    return render_template("admin/edit-page.html", data=page_data)
    
@app.route("/admin/save-data", methods=['POST'])
def save():
    """Saves new page data to the server, which will be displayed on the website on future requests.
        This function is called when the "Save" button on editing pages is pressed.

    Returns:
        "hello" as a json string
    """
    lists = json.loads(request.form.get("list"))
    texts = json.loads(request.form.get("text"))
    images = json.loads(request.form.get("image"))
    page = request.form.get("page_name")

    for name in texts:
        r.hmset(page + ":names:" + name, texts[name])
    for name in images:
        r.hmset(page + ":names:" + name, images[name])         
    for name in lists:
        for var in lists[name]:
            r.delete(page + ":lists:" + name + ":" + var + ":data")
            for item in lists[name][var]["data"]:
                r.rpush(page + ":lists:" + name + ":" + var + ":data", item)
                
    return jsonify(name="Hello")


@app.route("/admin/upload-image", methods=['POST'])
def upload():
    """Uploads an image to the server.
        This function is called when the "Upload image" button is pressed.

    Returns:
        A json object containing the server-side file name of the image
    """
    if request.method == 'POST':
        file = request.files['file']
        
        uploaded_file_path = None

        if file:
            filename = secure_filename(file.filename)
            filename = image.gen_file_name(filename)
            mime_type = file.content_type

            if not image.allowed_file(file.filename):
                #result = uploadfile(name=filename, type=mime_type, size=0, not_allowed_msg="File type not allowed")
                pass

            else:
                # save file to disk
                name, ext = splitext(filename)
                temp_name = "temp" + ext
                uploaded_file_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_name)
                file.save(uploaded_file_path)
                
                hash_new = image.md5(uploaded_file_path)
                
                found = False
                images = r.smembers("image_index")
                for image in images:
                    if r.get("images:" + image) == hash_new:
                        filename = image + ext
                        os.remove(uploaded_file_path)
                        found = True
                        break
                
                temp_file_path = uploaded_file_path
                uploaded_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                if not found:
                    os.rename(temp_file_path, uploaded_file_path)
                    r.sadd("image_index", name)
                    r.set("images:" + name, hash_new)
                    
            
            return jsonify(filename=filename)
        else:
            return jsonify(filename="")