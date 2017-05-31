from .auth_decorators import super_admin_require, content_admin_require
from random import choice
from flask import render_template,current_app
def custom_render_template(template_name, **kw):
    category = current_app.config['MENU_CATEGORY']
    return render_template(template_name,MENU_CATEGORY=category,**kw)

def color_picker():
    return choice(['info','primary','warning','success'])