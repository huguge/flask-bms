from .auth_decorators import super_admin_require, content_admin_require
from random import choice

def color_picker():
    return choice(['info','primary','warning','success'])