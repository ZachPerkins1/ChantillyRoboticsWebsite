import hashlib
import os
from os.path import splitext
from env import app

ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif"]


def md5(fname):
    """Computes an MD5 hash for the given file.

    Params:
        fname - the name of the file to hash
    Returns:
        A hexadecimal string containing the value of the hash
    """
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
    
    
def gen_file_name(filename):
    """Generates a server name for the given file name.
        This prevents name conflicts between files.

    Params:
        filename - the original name of the file
    Retuns:
        The new file name
    """
    i = 0
    name, ext = splitext(filename)
    
    filename = name + "_" + str(i) + ext
    while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
        i += 1
        filename = name + "_" + str(i) + ext
    
    return filename
    
    
def allowed_file(filename):
    """Determines whether a file has a valid name.
        This function checks the name for a valid extension.

    Params:
        filename - the name to validate
    Returns:
        Whether the file name is valid
    """
    # please please more validation
    for ext in ALLOWED_EXTENSIONS:
        if ext in filename:
            return True
    return False