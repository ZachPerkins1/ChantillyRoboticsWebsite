import redis
import os
import hashlib

from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif"]
_folder = ""
_db = None

def init(upload_folder, database):
    set_db(database)
    set_upload_folder(upload_folder)


def set_upload_folder(folder):
    global _folder
    _folder = folder
    
    
def set_db(db):
    global _db
    _db = db
    

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
    
    
def gen_file_name(filename):
    i = 0
    name, ext = os.path.splitext(filename)
    
    filename = name + "_" + str(i) + ext
    while os.path.exists(os.path.join(_folder, filename)):
        i += 1
        filename = name + "_" + str(i) + ext
    
    return filename
    
    
def allowed_file(filename):
    for ext in ALLOWED_EXTENSIONS:
        if ext in filename:
            return True
    return False

def upload(file):
    uploaded_file_path = None
    result = {}

    if file:
        filename = secure_filename(file.filename)
        filename = gen_file_name(filename)
        mime_type = file.content_type

        if not allowed_file(file.filename):
            pass

        else:
            # save file to disk
            name, ext = os.path.splitext(filename)
            temp_name = "temp" + ext
            uploaded_file_path = os.path.join(_folder, temp_name)
            file.save(uploaded_file_path)
            
            hash_new = md5(uploaded_file_path)
            
            found = False
            images = _db.smembers("image_index")
            for image in images:
                if _db.get("images:" + image) == hash_new:
                    filename = image + ext
                    os.remove(uploaded_file_path)
                    found = True
                    break
            
            temp_file_path = uploaded_file_path
            uploaded_file_path = os.path.join(_folder, filename)
            
            if not found:
                os.rename(temp_file_path, uploaded_file_path)
                _db.sadd("image_index", name)
                _db.set("images:" + name, hash_new)
                
        result["filename"] = filename
    else:
        result["filename"] = ""
    
    return result