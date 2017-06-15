from flask_mail import Mail, Message
from flask import render_template
import sessions as sess

_mail = None
_address = ""
_email = ""

def init(mailer, email, address):
    global _mail
    global _address
    global _email
    
    _mail = mailer
    _email = email
    _address = address
    
class Email:
    def __init__(self, subject, template, data={}):
        self._subject = subject
        self._template = template
        self._data = data
        
    def get_body(self):
        return render_template("email/" + self._template, data=self._data)
        
    def get_subject(self):
        return self._subject
        
    def add(self, key, data):
        self._data[key] = data


def send_email(recipients, email):
    email.add("address", _address)
    m = Message(email.get_subject(), sender = _email, recipients = recipients)
    print email.get_body()
    m.html = email.get_body()
    _mail.send(m)
    
    
def _add_user_info(email, user):
    user_data = user.get_all()
    email._data['user_data'] = user_data
    
    
def send_to_by_name(username, email):
    user = sess.User.from_existing(username)
    _add_user_info(user, email)
    send_to_by_user(user, email)
    
    
def send_to_by_user(user, email):
    recipient = user.get_email()
    send_email([recipient], email)
    
    
def send_to_all(email, tester=lambda _: True):
    users = sess.get_all_users()
    recipients = []
    for user in users:
        if tester(user):
            recipients.append(user.get_email())
        
    send_email(recipients, email)
    

def send_by_level(level, email):
    send_to_all(email, lambda user: user.get_level() <= level)
    
