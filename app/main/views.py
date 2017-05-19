# -*- coding:utf-8 -*- 
from flask import render_template, session, redirect, url_for,flash,current_app,request,send_file,abort,jsonify
from flask_login import login_required,current_user
from werkzeug.utils import secure_filename
import urllib
import os
import time

# from manage import config
from app.main import main 
from app import db
from app.models import User, Ebook, Comment, Permission,Book,Tag
from app.lib import super_admin_require
from app.main.forms import EditProfileForm, UploadEbookForm, CommentForm, AddBookForm
from config import config

from app.works import getImageFromPdf

@main.route('/')
def index():
    return render_template('index.html',
        app_name = 'Flask-BMS',
        username = session.get('username'))

@main.route('/admin')
@login_required
@super_admin_require
def admin():
    return render_template('admin.html', app_name='Flask-BMS')


@main.route('/user/<username>')
@login_required
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
    return render_template('user/edit_profile.html', form=form)

@main.route('/books')
@login_required
def books():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search')
    if search is None or search=='':    
        pagination = Book.query.order_by(Book.id.desc()).paginate(page,per_page=current_app.config['FLASK_BMS_MAX_PER_PAGE'])
    else:
        pagination = Book.query.whoosh_search(search).order_by(Book.id.desc()).paginate(page,per_page=current_app.config['FLASK_BMS_MAX_PER_PAGE'])
    books_list = pagination.items    
    return render_template('book/books.html', books=books_list, pagination = pagination, app_name='Flask-BMS')
        
@main.route('/addbook',methods=['GET','POST'])
@login_required
def addbook():
    form = AddBookForm()
    book = Book(uploader_id=current_user.id)
    if form.validate_on_submit():
        f = form.book_img.data
        ts = str(time.time()).split('.')[0]
        file_name = ts+'_'+f.filename
        file_path = os.path.join(config['default'].UPLOAD_PATH+'/books/', file_name)
        f.save(file_path)
        book.name = form.name.data
        book.author = form.author.data or u'无'
        book.description = form.description.data or u'暂无介绍'
        book.category_id = form.category.data
        book.status_id = form.status.data
        book.upload_user = current_user._get_current_object()
        book.isbn = form.isbn.data or u'无'
        book.total_count = int(form.total_count.data or 0)
        book.book_number = form.book_number.data or u'无'
        book.publisher = form.publisher.data or u'无'
        _, file_type = os.path.splitext(file_name)
        book.image_path = url_for('static', filename='uploads/books/' + file_name)
        # 执行电子书页面生成如果是pdf提取第一页，如果是word则使用默认的图片
        # if file_type.upper() == '.JPG' or 'PNG':
        #     resize_images(file_path, 'small_'+file_path)
        #     book.image_path = url_for('static', filename='uploads/'+file_name+'.jpg')
        # else:
        #     book.image_path = url_for('static.', filename='images/ebooks_default.png')
        db.session.add(book)
        flash('新增图书成功')
        return redirect(url_for('main.addbook'))
    return render_template('book/add_book.html', form=form)

@main.route('/book/<int:id>', methods=['GET', 'POST'])
@login_required
def book(id):
    book = Book.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data, book=book, author=current_user._get_current_object())
        db.session.add(comment)
        return redirect(url_for('main.book', id=book.id, page=1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (book.comments.count() -1)/current_app.config['FLASK_BMS_MAX_PER_PAGE'] +1
    pagination = book.comments.order_by(Comment.timestamp.desc()).paginate(
        page,
        per_page=current_app.config['FLASK_BMS_MAX_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    can_write_comment = current_user.can(Permission.WRITE_COMMENT)
    print can_write_comment
    return render_template('book/book.html',
                           pagination=pagination,
                           can_write_comment=can_write_comment,
                           book=book,
                           url_point = 'main.book',
                           form=form,
                           comments=comments)

@main.route('/ebooks',methods=['GET','POST'])
@login_required
def ebooks():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search','')
    if search is None or search=='':    
        pagination = Ebook.query.order_by(Ebook.created_at.desc()).paginate(page,per_page=current_app.config['FLASK_BMS_MAX_PER_PAGE'])
    else:
        pagination = Ebook.query.whoosh_search(search).order_by(Ebook.created_at.desc()).paginate(page,per_page=current_app.config['FLASK_BMS_MAX_PER_PAGE'])
    books_list = pagination.items    
    return render_template('book/ebooks.html',ebooks = books_list, pagination = pagination, app_name='Flask-BMS')


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
@login_required
def ebook(id):
    ebook = Ebook.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data, ebook=ebook, author=current_user._get_current_object())
        db.session.add(comment)
        # flash('评论信息成功创建')
        return redirect(url_for('main.ebook', id=ebook.id, page=1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (ebook.comments.count() -1)/current_app.config['FLASK_BMS_MAX_PER_PAGE'] +1
    pagination = ebook.comments.order_by(Comment.timestamp.desc()).paginate(
        page,
        per_page=current_app.config['FLASK_BMS_MAX_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    can_write_comment = current_user.can(Permission.WRITE_COMMENT)
    return render_template('book/ebook.html',
                           pagination=pagination,
                           url_point = 'main.ebook',
                           can_write_comment=can_write_comment,
                           book=ebook,
                           form=form,
                           comments=comments)

@main.route('/download/<string:file_type>/<int:id>/', methods=['GET'])
@login_required
def download(file_type, id):
    if file_type == 'ebook':
        ebook = Ebook.query.get_or_404(id)
        file_path = urllib.unquote_plus(os.path.join(current_app.root_path, '.' + ebook.file_path))
        try:
            # 由于编码问题，可以直接提取路径加上原始的文件名字
            path = os.path.dirname(file_path)+'/'+ebook.name
            ebook.downloads = ebook.downloads+1
            db.session.add(ebook)
            return send_file(filename_or_fp=path,as_attachment=True)
        except Exception as e:
            raise e
            abort(500)
    else:
        abort(404)
@main.route('/ebook/tag/<int:id>', methods=['POST'])
# @login_required
def ebook_add_tag(id):
    tag = request.args.get('tag','')
    if tag=='' or tag == None:
        return jsonify({'error':'Tag名称为空'}),400
    else:
        ebook = Ebook.query.get(id)
        if ebook is None:
            return jsonify({'error':'查询书籍不存在'}),404
        for t in ebook.tags:
            if t.name == tag:
                return jsonify({'error':'标签已存在'}),400
        Tag.query.filter_by(name=tag).all()