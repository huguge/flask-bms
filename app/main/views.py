# -*- coding:utf-8 -*- 
from flask import render_template, session, redirect, url_for,flash,current_app,request,send_file,abort
from flask_login import login_required,current_user
from werkzeug.utils import secure_filename
import urllib
import os

# from manage import config
from app.main import main 
from app import db
from app.models import User, Ebook, Comment, Permission
from app.lib import super_admin_require
from app.main.forms import EditProfileForm, UploadEbookForm, CommentForm
from config import config

from app.works import getImageFromPdf

@main.route('/')
def index():
    return render_template('index.html',
        app_name = 'Flask-BMS',
        username = session.get('username'))

@main.route('/ebooks',methods=['GET','POST'])
@login_required
def ebooks():
    page = request.args.get('page', 1, type=int)
    pagination = Ebook.query.order_by(Ebook.created_at.desc()).paginate(page,per_page=current_app.config['FLASK_BMS_MAX_PER_PAGE'])
    ebooks = pagination.items
    return render_template('book/ebooks.html', app_name='Flask-BMS',ebooks = ebooks,pagination = pagination)

@main.route('/books')
@login_required
def books():
    return render_template('book/books.html', app_name='Flask-BMS')


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
    return render_template('user/profile.html', user=u)

@main.route('/edit_profile', methods=['POST','GET'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('更新信息成功')
        return redirect(url_for('main.edit_profile', username = current_user.username))
    form.name.data = current_user.name
    form.about_me.data = current_user.about_me
    return render_template('user/edit_profile.html', form=form,)

    upload_ebooks
@main.route('/upload', methods=['POST', 'GET'])
@login_required
def upload_ebooks():
    form = UploadEbookForm()
    book = Ebook(uploader_id=current_user.id)
    if form.validate_on_submit():
        f = form.ebook_file.data
        file_name = f.filename
        file_path = os.path.join(config['default'].UPLOAD_PATH, file_name)
        f.save(file_path)
        book.name = file_name
        book.author = form.author.data
        book.description = form.description.data or u'暂无介绍'
        book.category_id = form.category.data
        book.upload_user = current_user._get_current_object()
        _, file_type = os.path.splitext(file_name)
        book.file_type = file_type
        book.file_size = os.path.getsize(file_path)
        book.file_path = url_for('static', filename='uploads/' + file_name)
        # 执行电子书页面生成如果是pdf提取第一页，如果是word则使用默认的图片
        if file_type.upper() == '.PDF':
            image_path = file_path+'.jpg'
            getImageFromPdf(file_path, image_path)
            book.image_path = url_for('static', filename='uploads/'+file_name+'.jpg')
        else:
            book.image_path = url_for('static.', filename='images/ebooks_default.png')
        db.session.add(book)
        flash('上传电子书成功')
        print book
        return redirect(url_for('main.upload_ebooks'))
    return render_template('book/upload_ebook.html', form=form)

@main.route('/ebook/<int:id>', methods=['GET', 'POST'])
def ebook(id):
    ebook = Ebook.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data, ebook=ebook, author=current_user._get_current_object())
        db.session.add(comment)
        flash('评论信息成功创建')
        return redirect(url_for('main.ebook', id=ebook.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (ebook.comments.count() -1)/current_app.config['FLASK_BMS_MAX_PER_PAGE'] +1
    pagination = ebook.comments.order_by(Comment.timestamp.asc()).paginate(
        page,
        per_page=current_app.config['FLASK_BMS_MAX_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    can_write_comment = current_user.can(Permission.WRITE_COMMENT)
    print can_write_comment
    return render_template('book/ebook.html',
                           pagination=pagination,
                           can_write_comment=can_write_comment,
                           ebook=ebook,
                           form=form,
                           comments=comments)

@main.route('/download/<string:file_type>/<int:id>/', methods=['GET'])
def download(file_type, id):
    if file_type == 'ebook':
        ebook = Ebook.query.get_or_404(id)
        file_path = urllib.unquote_plus(os.path.join(current_app.root_path, '.' + ebook.file_path))
        try:
            # 由于编码问题，可以直接提取路径加上原始的文件名字
            path = os.path.dirname(file_path)+'/'+ebook.name
            return send_file(filename_or_fp=path,as_attachment=True)
        except Exception as e:
            raise e
            abort(500)
    else:
        abort(404)
