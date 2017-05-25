from flask import request
import redis
import hashlib
import binascii
import os
import re

error_codes = {
    0: "No Error",
    1: "User already exists",
    2: "Session does not exist",
    3: "Invalid session code",
    4: "Passwords do not match",
    5: "Must be a valid email",
    6: "Password must be at least 4 characters",
    7: "User does not exist",
    8: "Incorrect password"
}

SECRET_KEY_SHHHH = "#85)yc5*u%w2eppddrgk6muu5#i8x+*ljfm9l(kkhysqfu^bex_prostate_cancer"

sessions = {}
_db = None

def init(database):
    global _db
    _db = database
    
    
class Session(object):
    def __init__(self, user, key, id):
        self._user = user
        self._key = key
        self._id = id

    def get_user(self):
        return self._user
    
    def get_key(self):
        return self._key
        
    def get_id(self):
        return self._id
        
    @classmethod
    def create(cls, user):
        salt = user.get('salt')
        rand = binascii.hexlify(os.urandom(32))
        key = hashlib.sha256(rand + salt + SECRET_KEY_SHHHH)
        hash = key.hexdigest()
        
        id = Session.get_new_id()
        
        session = cls(user, hash, id)
        sessions[id] = session
        print id
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


class User(object):
    def __init__(self, name, data={}):
        self._data = data
        self._name = name
        
    def get(self, key):
        return self._data[key]
    
    def set(self, key, data):
        self._data[key] = data
        
    def get_email(self):
        return self.get("email")
        
    def pull_data(self):
        self._data = _db.hgetall("users" + self._name)
        
    def push_data(self):
        _db.hmset("users" + self._name, self._data)
        
    @classmethod
    def create_new(cls, user, email, password):
        s, p = cls._hash_password(password)
        _db.sadd("user_index", user.lower())
        data = {
            'email': email,
            'password': p,
            'salt': s
        }
        
        n_user = cls(user, data)
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


def create_user(name, email, password, confirm):
    errs = verify_user(name, email, password, confirm)
    if errs.any():
        return errs, None
    else:
        user = User.create_new(name, email, password)
        return errs, user
    
    return errs, user


def verify_user(u, e, p, c):
    errs = ErrorList()
    e = e.lower()
    u = u.lower()

    r = re.compile("[\w.]+@[a-z]+(\.[a-z]+)+")
    if not r.match(e):
        errs.add(5)

    if len(p) < 4:
        errs.add(6)

    if p != c:
        errs.add(4)
        
    if _db.sismember("user_index", u):
        errs.add(1)
        
    print errs.get()

    return errs


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

def create_session_user(name, email, password, confirm):
    errs, user = create_user(name, email, password, confirm)

    if errs.any():
        return errs, None

    errs, session = create_session(user)

    return errs, session



def get_session(sid, s_key, db):
    errs = ErrorList()
    if sid not in sessions:
        errs.add(2)
        return errs, None
        
    session = Session.get(sid)

    if session.get_key() != s_key:
        errs.add(3), session

    return errs, session