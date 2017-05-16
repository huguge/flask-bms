from flask import render_template
from app.main import main

@main.app_errorhandler(404)
def page_not_found(message=None):
    return render_template('error_pages/404.html'), 404

@main.app_errorhandler(403)
def server_403_error(message=None):
    print message
    return render_template('error_pages/403.html'), 403

@main.app_errorhandler(500)
def server_500_error(message=None):
    return render_template('error_pages/500.html'), 404
    