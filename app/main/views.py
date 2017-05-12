# -*- coding:utf-8 -*- 
from flask import render_template, session, redirect, url_for,flash
from flask_login import login_required,current_user


from app.main import main 
from app import db
from app.models import User
from app.lib import super_admin_require
from app.main.forms import EditProfileForm
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


@main.route('/user/<username>')
def user(username):
    u = User.query.filter_by(username=username).first()
    if u is None:
        abort(404)
    return render_template('user/profile.html',user=u)

@main.route('/edit_profile',methods=['POST','GET'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('更新信息成功')
        return redirect(url_for('main.edit_profile',username=current_user.username))
    form.name.data = current_user.name
    form.about_me.data = current_user.about_me
    return render_template('user/edit_profile.html',form=form,)