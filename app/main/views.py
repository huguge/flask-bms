# -*- coding:utf-8 -*- 
from flask import render_template, session, redirect, url_for,flash
from app.main import main 
from app.main.forms import LoginForm
from app import db
from app.models import User
@main.route('/')
def index():
    return render_template('index.html',
        app_name = 'Flask-BMS',
        username = session.get('username'))

@main.route('/ebooks')
def ebooks():
    return render_template('ebooks.html', app_name='Flask-BMS')
@main.route('/books')
def books():
    return render_template('books.html', app_name='Flask-BMS')
@main.route('/register', methods=['GET', 'POST'])
def register():
    pass
@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    username = None
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        form.username.data = ''
        if username == password:
            session['username'] = username
            return redirect(url_for('.index'))
        else:
            flash(u'输入信息有误')
        return redirect(url_for('.login'))
    return render_template('login.html',
        app_name='Flask-BMS',
        username=username,
        form=form)
@main.route('/logout',methods = ['GET'])
def logout():
    session.clear()
    return redirect(url_for('.index'))