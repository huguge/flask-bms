# -*- coding:utf-8 -*- 
from flask import render_template, session, redirect, url_for,flash,current_app,request,send_file,abort,jsonify
from sqlalchemy.sql import text
from flask_login import login_required,current_user
from werkzeug.utils import secure_filename
import urllib
import os
import time
import random
# from manage import config
from app.main import main 
from app import db
from app.models import User, Ebook, Comment, Permission,Book,Tag, BookRent
from app.lib import super_admin_require
from app.main.forms import EditProfileForm, UploadEbookForm, CommentForm, AddBookForm, EditBookForm, EditEBookForm

from config import config

from app.works import getImageFromPdf
from app.lib import color_picker
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
        if form.tag.data and len(form.tag.data.split(';'))>0:
            for i in form.tag.data.split(';'):
                tag = Tag.findOrInsert(i)
                book.tags.append(tag)
        book.status_id = form.status.data
        book.upload_user = current_user._get_current_object()
        book.isbn = form.isbn.data or u'无'
        book.total_count = int(form.total_count.data or 0)
        book.book_number = form.book_number.data or u'无'
        book.publisher = form.publisher.data or u'无'
        _, file_type = os.path.splitext(file_name)
        book.image_path = url_for('static', filename='uploads/books/' + file_name)

        db.session.add(book)
        flash('新增图书成功')
        return redirect(url_for('main.addbook'))
    return render_template('book/add_book.html', form=form)

@main.route('/book/<int:id>', methods=['GET', 'POST'])
@login_required
def book(id):
    book = Book.query.get_or_404(id)
    s = text("select users.id,users.username,users.avatar_hash from book_rent inner join users where book_rent.rent_person_id=users.id and book_rent.active=1 and book_rent.rent_book_id=:x")
    book_rent_users = db.engine.execute(s, x=id).fetchall()
    form = CommentForm()
    userlist = BookRent.query.filter_by(rent_book_id=4,active=1).first().rent_user
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
    tags = []
    for i in book.tags:
        tags.append({'name':i.name,'className':color_picker()})
    return render_template('book/book.html',
                           pagination=pagination,
                           can_write_comment=can_write_comment,
                           book=book,
                           url_point = 'main.book',
                           form=form,
                           tags=tags,
                           book_rent_users=book_rent_users,
                           comments=comments)

@main.route('/book/<int:id>/edit', methods=['POST','GET'])
@login_required
def editbook(id):
    form = EditBookForm()
    book = Book.query.get_or_404(id)
    if form.validate_on_submit():
        f = form.book_img.data
        if f is not None:
            ts = str(time.time()).split('.')[0]
            file_name = ts+'_'+f.filename
            file_path = os.path.join(config['default'].UPLOAD_PATH+'/books/', file_name)
            f.save(file_path)
            book.image_path = url_for('static', filename='uploads/books/' + file_name)
        book.name = form.name.data
        book.author = form.author.data or u'无'
        book.description = form.description.data or u'暂无介绍'
        book.tags=[]
        tag_string = form.tag.data
        if tag_string is not None and len(tag_string.split(';'))>0:
            for t in tag_string.split(';'):
                tag = Tag.findOrInsert(t)
                book.tags.append(tag)
        book.category_id = form.category.data
        book.status_id = form.status.data
        book.isbn = form.isbn.data or u'无'
        book.total_count = int(form.total_count.data or 0)
        book.book_number = form.book_number.data or '无'
        book.publisher = form.publisher.data or u'无'
        db.session.add(book)
        flash('修改图书成功')
        return redirect(url_for('main.editbook',id=book.id))
    form.name.data = book.name
    form.author.data = book.author or u'无'
    form.description.data = book.description or u'暂无介绍'
    form.category.data = book.category_id
    form.status.data = book.status_id 
    form.isbn.data = book.isbn or u'无'
    form.total_count.data = int(book.total_count)
    form.book_number.data = book.book_number or u'无'
    form.publisher.data = book.publisher or u'无'
    tags_list = []
    for tag in book.tags:
        tags_list.append(tag.name)
    return render_template('book/edit_book.html', form=form, tags=';'.join(tags_list))


@main.route('/ebook/<int:id>/edit', methods=['POST','GET'])
@login_required
def editebook(id):
    form = EditEBookForm()
    book = Ebook.query.get_or_404(id)
    tag_string = form.tag.data
    if form.validate_on_submit():
        f = form.ebook_file.data
        if f is not None:
            f = form.ebook_file.data
            file_name = f.filename
            file_path = os.path.join(config['default'].UPLOAD_PATH, file_name)
            f.save(file_path)
            book.name = file_name
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
        book.tags=[]
        if tag_string is not None and len(tag_string.split(';'))>0:
            for t in tag_string.split(';'):
                tag = Tag.findOrInsert(t)
                book.tags.append(tag)
        book.name = form.name.data
        book.author = form.author.data
        book.description = form.description.data or u'暂无介绍'
        book.category_id = form.category.data
        db.session.add(book)
        flash('修改电子书成功')
        return redirect(url_for('main.editebook',id=book.id))
    form.name.data = book.name
    form.author.data = book.author or u'无'
    form.description.data = book.description or u'暂无介绍'
    form.category.data = book.category_id
    tags_list = []
    for tag in book.tags:
        tags_list.append(tag.name)
    return render_template('book/edit_ebook.html', form=form, tags=';'.join(tags_list))

@main.route('/book/<int:id>/delete', methods=['GET'])
@login_required
def deletebook(id):
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for('main.books'))

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

@main.route('/ebook/<int:id>/delete', methods=['GET'])
@login_required
def deleteebook(id):
    book = Ebook.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for('main.books'))

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
    tags = []
    for i in ebook.tags:
        tags.append({'name':i.name,'className':color_picker()})
    comments = pagination.items
    can_write_comment = current_user.can(Permission.WRITE_COMMENT)
    return render_template('book/ebook.html',
                           pagination=pagination,
                           url_point = 'main.ebook',
                           can_write_comment=can_write_comment,
                           book=ebook,
                           tags=tags,
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

@main.route('/ebook/tag/<string:name>', methods=['GET'])
@login_required
def ebook_tag(name):
    page = request.args.get('page', 1, type=int)
    pagination =  Tag.query.filter_by(name=name).first().ebooks.order_by(Ebook.created_at.desc()).paginate(page,per_page=current_app.config['FLASK_BMS_MAX_PER_PAGE'])
    books_list = pagination.items
    return render_template('book/ebooks.html', ebooks=books_list, pagination = pagination, app_name='Flask-BMS',tag_name=name)

@main.route('/book/tag/<string:name>', methods=['GET'])
@login_required
def book_tag(name):
    page = request.args.get('page', 1, type=int)
    pagination = Tag.query.filter_by(name=name).first().books.order_by(Book.id.desc()).paginate(page,per_page=current_app.config['FLASK_BMS_MAX_PER_PAGE'])
    books_list = pagination.items    
    return render_template('book/books.html', books=books_list, pagination = pagination, app_name='Flask-BMS',tag_name=name)

@main.route('/book/rent/<int:id>',methods=['GET'])
@login_required
def rent_book(id):
    book = Book.query.get_or_404(id)
    book.rent_count=book.rent_count+1
    if book.rent_count>book.total_count:
        flash('图书借阅失败,库存数量暂时不够')
        return redirect(url_for('main.book',id=book.id))
    db.session.add(book)

    # 发送邮件通知图书管理员
    # 更新book-rent表
    bookrent = BookRent()
    bookrent.rent_user = current_user._get_current_object()
    bookrent.book = book
    db.session.add(bookrent)
    db.session.commit()
    flash('图书借阅申请已成功提交')
    return redirect(url_for('main.book',id=book.id))


@main.route('/book/return/<int:id>/<int:user_id>',methods=['GET'])
@login_required
def return_book(id,user_id):
    if current_user.id == user_id or current_user.can(Permission.ADMIN_CONTENT):
        try:
            bookrent = BookRent.query.filter_by(rent_person_id=user_id,rent_book_id=id,active=1).first()
            bookrent.active =0
            db.session.add(bookrent)
            db.session.commit()
            flash('图书归还申请已成功提交')
        except expression as identifier:
            flash('服务器暂时无法提交信息，请稍后再试')
    return redirect(url_for('main.book',id=id))