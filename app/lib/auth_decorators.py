from functools import wraps
from flask import abort
from flask_login import current_user

from app.models import Permission


def permission_require(permission):
    def wrapper(f):
        @wraps(f)
        def decorator_func(*args,**kw):
            if not current_user.can(permission):
                # print '403'
                abort(403)
            return f(*args,**kw)
        return decorator_func
    return wrapper

def super_admin_require(f):
    return permission_require(Permission.ADMIN_USER)(f)
def content_admin_require(f):
    return permission_require(Permission.ADMIN_CONTENT)(f)

