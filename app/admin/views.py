# -*- coding:utf-8 -*- 
from flask import render_template, session, redirect, url_for,flash,current_app,request,send_file,abort,jsonify
from sqlalchemy.sql import text
from flask_login import login_required,current_user


from app.admin import admin 
from app import db
from app.models import User, Ebook, Comment, Permission,Book,Tag, BookRent
from app.lib import super_admin_require
from config import config


@admin.route('/')
@login_required
@super_admin_require
def admin_dashboard():
    return render_template('admin/index.html', app_name='Flask-BMS')


@admin.route('/user')
@login_required
@super_admin_require
def admin_user():
    return render_template('admin/user.html', app_name='Flask-BMS')

@admin.route('/config')
@login_required
@super_admin_require
def admin_config():
    return render_template('admin/config.html', app_name='Flask-BMS')

@admin.route('/about')
@login_required
@super_admin_require
def admin_about():
    return render_template('admin/about.html', app_name='Flask-BMS')