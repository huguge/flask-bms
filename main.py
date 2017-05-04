# -*- coding:utf-8 -*-  
from flask import Flask, render_template, redirect, url_for, session,flash
from flask_moment import Moment
from flask_bootstrap import Bootstrap
from flask_script import Manager
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Required
from flask_sqlalchemy import SQLAlchemy

import MySQLdb



app = Flask(__name__)
app.config['SECRET_KEY'] = 'iwillnottellyouthiskey'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@localhost/flaskbms'
db = SQLAlchemy(app)
Bootstrap(app)
moment = Moment(app)
manager = Manager(app)

# 定义登入表单

class LoginForm(FlaskForm):
    username = StringField(u'用户名', validators=[Required()])
    password = PasswordField(u'密码', validators=[Required()])
    submit = SubmitField(u'提交')



# 定义数据库

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    def __repr__(self):
        return '<User %r>'%self.username



@app.route('/')
def index():
    return render_template('index.html',
        app_name = 'Flask-BMS',
        username = session.get('username'))

@app.route('/ebooks')
def ebooks():
    return render_template('ebooks.html', app_name='Flask-BMS')
@app.route('/books')
def books():
    return render_template('books.html', app_name='Flask-BMS')
@app.route('/register', methods=['GET', 'POST'])
def register():
    pass
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    username = None
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        form.username.data = ''
        if username == password:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            flash(u'输入信息有误')
        return redirect(url_for('login'))
    return render_template('login.html',
        app_name='Flask-BMS',
        username=username,
        form=form)
@app.route('/logout',methods = ['GET'])
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found():
    return render_template('error_pages/404.html'), 404

@app.errorhandler(500)
def server_500_error():
    return render_template('error_pages/500.html'), 404

# python main.py runserver
if __name__ == '__main__':
    manager.run()