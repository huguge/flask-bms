# -*- coding:utf-8 -*- 
from flask import render_template, session, redirect, url_for,flash
from flask_login import login_required,current_user
from werkzeug.utils import secure_filename
import os
# from manage import config
from app.main import main 
from app import db
from app.models import User,Ebook
from app.lib import super_admin_require
from app.main.forms import EditProfileForm, UploadEbookForm
from config import config
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

    upload_ebooks
@main.route('/upload',methods=['POST','GET'])
@login_required
def upload_ebooks():
    form = UploadEbookForm()
    book = Ebook(uploader_id=current_user.id)
    if form.validate_on_submit():
        f = form.ebook_file.data
        file_name = secure_filename(f.filename)
        file_path = os.path.join(config['default'].UPLOAD_PATH,file_name)
        f.save(file_path)
        book.name = file_name
        book.file_path =file_path
        book.author = form.author.data
        book.description = form.description.data or u'暂无介绍'
        book.category_id = form.category.data
        book.uploader_id = current_user.id

        flash('上传电子书成功')
        print book
        return redirect(url_for('main.upload_ebooks'))
    return render_template('book/upload_ebook.html',form=form)