from flask import request
import redis
import hashlib
import binascii
import os
import re
import time

error_codes = {
     0: "No Error",
     1: "User already exists",
     2: "Session does not exist",
     3: "Invalid session code",
     4: "Passwords do not match",
     5: "Must be a valid email",
     6: "Password must be at least 8 characters",
     7: "User does not exist",
     8: "Incorrect password",
     9: "Password must contain at least one number",
    10: "Username cannot contain spaces",
    11: "Username can be up to 20 characters",
    12: "Registration code is expired",
    13: "Registration code does not exist"
}

user_attributes = [
    "first-name",
    "last-name",
    "email"
]

SECRET_KEY_SHHHH = "#85)yc5*u%w2eppddrgk6muu5#i8x+*ljfm9l(kkhysqfu^bex_prostate_cancer"

sessions = {}
registrations = {}

_db = None

def init(database):
    global _db
    _db = database
    
    
class Session(object):
    def __init__(self, user, key, id):
        self._user = user
        self._key = key
        self._id = id
        self._set_timestamp()
        
    def _set_timestamp(self):
        self._timestamp = time.time()

    def get_user(self, passive=False):
        if not passive:
            self._set_timestamp()
        return self._user
    
    def get_key(self, passive=False):
        if not passive:
            self._set_timestamp()
        return self._key
        
    def get_id(self, passive=False):
        if not passive:
            self._set_timestamp()
        return self._id
        
    def delete(self):
        del sessions[self._id]
        
    def last_active(self):
        return self._timestamp
        
    @classmethod
    def create(cls, user):
        salt = user.get('salt')
        rand = binascii.hexlify(os.urandom(32))
        key = hashlib.sha256(rand + salt + SECRET_KEY_SHHHH)
        hash = key.hexdigest()
        
        id = Session.get_new_id()
        
        session = cls(user, hash, id)
        sessions[id] = session
        return session
    
    @classmethod
    def get(cls, id):
        return sessions[id]
        
        
    @classmethod
    def get_new_id(cls):
        i = 0
        while i in sessions:
            i += 1
            
            
        return i
        
        
class Registration(object):
    def __init__(self, email, level, expiration, code):
        self._email = email
        self._level = level
        self._expiration = expiration + time.time()
        self._code = code
        
    def get_reg_code(self):
        return self._code
    
    def get_email(self):
        return self._email
    
    def get_level(self):
        return self._level
        
    def is_expired(self):
        return time.time() > self._expiration
        
    @classmethod
    def create_new(cls, email, level, expiration):
        reg_code = binascii.hexlify(os.urandom(16))
        while reg_code in registrations:
            reg_code = binascii.hexlify(os.urandom(16))
            
        reg = cls(email, level, expiration, reg_code)
        registrations[reg_code] = reg
        return reg
        
    @classmethod
    def get(cls, reg_code):
        if reg_code in registrations:
            return True, registrations[reg_code]
        else:
            return False, None
    

class User(object):
    def __init__(self, name, data={}):
        data["access-level"] = 2
        for key in user_attributes:
            if key not in data:
                data[key] = ""
                
        self._data = data
        self._name = name
        
    def get(self, key, default=""):
        val = ""
        try:
            val = self._data[key]
        except:
            val = default
        
        if val == "":
            val = default
            
        return val
        
    def get_all(self):
        return self._data
    
    def set(self, key, data):
        self._data[key] = data
        
    def get_level(self):
        return self.get("access-level", 2)
        
    def get_email(self):
        return self.get("email")
        
    def get_name(self):
        return self._name
        
    def pull_data(self):
        remote = _db.hgetall("users:" + self._name)
        for key in remote:
            self._data[key] = remote[key]

    def push_data(self):
        _db.hmset("users:" + self._name, self._data)
        
    @classmethod
    def create_new(cls, data):
        s, p = cls._hash_password(data["password"])
        _db.sadd("user_index", data["username"].lower())

        t_dict = { key:data[key] for key in data }
        del t_dict["confirm"]
        t_dict["password"] = p
        t_dict["salt"] = s
    
        n_user = cls(data["username"].lower(), t_dict)
        n_user.push_data()
        return n_user

    @classmethod
    def from_existing(cls, user):
        n_user = cls(user)
        n_user.pull_data()
        return n_user

    @classmethod
    def _hash_password(cls, password):
        salt = binascii.hexlify(os.urandom(16))
        password = hashlib.sha256(salt + SECRET_KEY_SHHHH + password).hexdigest()
        return salt, password
        

class ErrorList:
    def __init__(self):
        self._errs = []

    def add(self, code):
        if code not in self._errs:
            self._errs.append(code)
    
    def rm(self, code):
       self._errs.remove(code)
    
    def get(self):
        return self._errs
    
    def get_formatted(self):
        f_errs = [error_codes[n] for n in self._errs]
        return f_errs
        
    def get_count(self):
        return len(self._errs)
        
    def any(self):
        return self.get_count() > 0
    

def gen_rand(bytes):
    num = os.urandom(bytes)


def create_user(data):
    errs = verify_user(data)
    if errs.any():
        return errs, None
    else:
        errs, registration = get_registration(data["reg_code"])
        if errs.any():
            return errs, None
             
        data["access-level"] = registration.get_level()
        data["email"] = registration.get_email()
        
        user = User.create_new(data)
        return errs, user
    
    return errs, user
    

def update_user(session, data):
    errs = verify_user(data)
    if errs.any():
        return errs
    
    for item in data:
        if item == "password":
            salt, pw = User._hash_password(data["password"])
            session.get_user().set("password", pw)
            session.get_user().set("salt", salt)
        elif item in user_attributes:   
            session.get_user().set(item, data[item])
    
    session.get_user().push_data()
    
    return errs

def verify_user(data):
    errs = ErrorList()

    if "email" in data:
        e = data["email"].lower()
        r = re.compile("[\w.]+@[a-z]+(\.[a-z]+)+")
        if not r.match(e):
            errs.add(5)
    
    if "password" in data:
        p = data["password"]
        c = data["confirm"]
        
        if len(p) < 8:
            errs.add(6)
            
        r = re.compile("\d")
        if not r.search(p):
            errs.add(9)

        if p != c:
            errs.add(4)
    
    if "username" in data:
        u = data["username"].lower()
        if _db.sismember("user_index", u):
            errs.add(1)
            
        if len(u) > 20:
            errs.add(11)
            
        if " " in u:
            errs.add(10)
            
        
    return errs


def get_registration(reg_code):
    errs = ErrorList()
    success, registration = Registration.get(reg_code)
    
    if success:
        if registration.is_expired():
            errs.add(12)
        
    else:
        errs.add(13)
    
    for code in registrations:
        if registrations[code].is_expired():
            del registrations[code]
        
    return errs, registration
            
        
    

def login_user(u, p):
    errs = ErrorList()
    u = u.lower()

    if not _db.sismember("user_index", u):
        errs.add(7)
        return errs, None

    user = User.from_existing(u)

    salt = user.get('salt')
    password = hashlib.sha256(salt + SECRET_KEY_SHHHH + p).hexdigest()

    if password != user.get('password'):
        errs.add(8)
        
    if errs.any():
        return errs, None

    errs, res = create_session(user)

    return errs, res


# assumes user has already been created
def create_session(user):
    return ErrorList(), Session.create(user)

def create_session_user(data):
    errs, user = create_user(data)

    if errs.any():
        return errs, None

    errs, session = create_session(user)

    return errs, session


def get_session(sid, s_key):
    errs = ErrorList()
    if sid not in sessions:
        errs.add(2)
        return errs, None
        
    session = Session.get(sid)

    if session.get_key() != s_key:
        errs.add(3), session

    return errs, session
    

def check_session_quick(request, level=2):
    sid = int(request.cookies.get("s_id", "-1"))
    s_key = request.cookies.get("s_key", "")
    errs, session = get_session(sid, s_key)

    if errs.any():
        return False, None
    else:
        user_level = session.get_user().get_level()
        if user_level < level:
            return False, session
        else:
            return True, session
            
def create_registration(attr):
    errs = verify_user(attr)
    if errs.any():
        return errs, None
    else:
        return errs, Registration.create_new(attr["email"], attr["level"], attr["expiry"])
        