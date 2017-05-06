from flask_mail import Message, Mail
from flask import render_template
from threading import Thread
from app import mail
from manage import app

def send_email(to,subject,template,**kwargs):
    msg = Message(app.config['FLASK_BMS_EMAIL_PREFIX']+subject,
        sender=app.config['FLASK_BMS_EMAIL_SENDER'],
        recipients = [to])
    msg.body = render_template(template+'.txt',**kwargs)
    msg.html = render_template(template+'.html',**kwargs)
    print msg
    t = Thread(target = send_async_email,args = [app,msg])
    t.start()
    return t

def send_async_email(app,msg):
    with app.app_context():
        mail.send(msg)



