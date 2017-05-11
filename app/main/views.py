# -*- coding:utf-8 -*- 
from flask import render_template, session, redirect, url_for,flash
from flask_login import login_required


from app.main import main 
from app import db
from app.models import User
from app.lib import super_admin_require
@main.route('/')
def index():
    return render_template('index.html',
        app_name = 'Flask-BMS',
        username = session.get('username'))

@main.route('/ebooks')
@login_required
def ebooks():
    return render_template('ebooks.html', app_name='Flask-BMS')
@main.route('/books')
@login_required
def books():
    return render_template('books.html', app_name='Flask-BMS')


@main.route('/admin')
@login_required
@super_admin_require
def admin():
    return render_template('admin.html', app_name='Flask-BMS')