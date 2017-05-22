# -*- coding:utf-8 -*- 

from datetime import datetime
from flask import current_app,request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin,AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from markdown import markdown
import bleach

from jieba.analyse import ChineseAnalyzer

from app import db, login_manager
import hashlib

from app.errors import ResourceNotAvalibleError

# 定义数据库models


class Permission:
    FOLLOW = 0x01
    WRITE_COMMENT = 0x02
    WRITE_ARTICLES =0x04
    ADMIN_CONTENT = 0x40
    ADMIN_USER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User',backref='role',lazy='dynamic')
    default = db.Column(db.Boolean,default=False,index=True)
    permissions = db.Column(db.Integer)
    @staticmethod
    def insert_default():
        roles = {
            'User':(Permission.FOLLOW|Permission.WRITE_ARTICLES|Permission.WRITE_COMMENT,True),
            'ContentAdmin':(Permission.FOLLOW|Permission.WRITE_ARTICLES|Permission.WRITE_COMMENT|Permission.ADMIN_CONTENT,False),
            'SuperAdmin':(0xff,False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()



class User(db.Model,UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64),unique=True,index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    # 在Ebook中增加一个upload_user对象
    ebooks = db.relationship('Ebook', backref='upload_user', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    # 在Ebook中增加一个upload_user对象
    books = db.relationship('Book', backref='upload_user', lazy='dynamic')
    # 在BookRent中加入rent_user
    rents_book = db.relationship('BookRent', backref='rent_user', lazy='dynamic')


    def __init__(self,**kw):
        super(User,self).__init__(**kw)
        if self.role is None:
            if self.email == current_app.config['FLASK_BMS_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
    
    def gravatar(self,size=100,default='identicon',rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url, hash=hash, size=size, default=default, rating=rating)
    
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def generate_confirmation_token(self,expiration=3600):
        s=Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'confirm':self.id})
    def confim_token(self,token):
        s=Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True
    @property
    def password(self):
        raise AttributeError(u'Password 不可直接读取')
    @password.setter
    def password(self,password):
        """设置用户新的密码"""
        self.password_hash = generate_password_hash(password)
    def verify_password(self,password):
        """测试用户输入密码是否匹配一致"""
        return check_password_hash(self.password_hash,password)
    
    def can(self,permission):
        """User.can() 测试用户是否具有操作某些功能的能力"""
        return self.role is not None and (self.role.permissions & permission == permission)
    def is_super_admin(self):
        return self.can(Permission.ADMIN_USER)
    def is_content_admin(self):
        return self.can(Permission.ADMIN_CONTENT)

    def __repr__(self):
        return '<User %r>'%self.username

class AnonymousUser(AnonymousUserMixin):
    def can(self, permission):
        return False
    def is_super_admin(self):
        return False
    def is_content_admin(self):
        return False


# 创建一个基本的多对多的数据库表
ebooks_tags = db.Table('ebooks_tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
    db.Column('ebook_id', db.Integer, db.ForeignKey('ebooks.id'))
)

class Ebook(db.Model):
    __tablename__ = 'ebooks'
    __searchable__ = ['name', 'description','author']
    # __analyzer__ = SimpleAnalyzer()
    __analyzer__ =  ChineseAnalyzer() 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    author = db.Column(db.String(32))
    description = db.Column(db.Text(),default=u"暂无评价")
    file_type = db.Column(db.String(16))
    file_size =  db.Column(db.Integer)
    created_at = db.Column(db.DateTime(),default=datetime.utcnow)
    downloads = db.Column(db.Integer,default=0)
    file_path = db.Column(db.String(256))
    image_path = db.Column(db.String(256))
    comments = db.relationship('Comment', backref='ebook', lazy='dynamic')
    uploader_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    category_id = db.Column(db.Integer,db.ForeignKey('categories.id'))
    tags = db.relationship('Tag', secondary=ebooks_tags,backref=db.backref('ebooks', lazy=True))

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    description = db.Column(db.Text())
    ebooks = db.relationship('Ebook',backref='category',lazy='dynamic')
    books = db.relationship('Book',backref='category',lazy='dynamic')
    @staticmethod
    def insert_default(categories=None):
        if categories==None:
            categories = [
                '开发技术',
                '运维技术',
                '数据库',
                '系统架构',
                '其他'
            ]
        for r in categories:
            c = Category.query.filter_by(name=r).first()
            if c is None:
                c = Category(name=r)
            db.session.add(c)
        db.session.commit()   

class Tag(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    description = db.Column(db.Text())
    @staticmethod   
    def findOrInsert(tagName):
        tag = Tag.query.filter_by(name=tagName).first()
        if tag is not None:
            return tag
        else:
            tag = Tag(name=tagName.strip())
            db.session.add(tag)
            db.session.commit()
            return tag




class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime,index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean,default=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    ebook_id = db.Column(db.Integer, db.ForeignKey('ebooks.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

# setting comment body listener to trigge the body_html set 
db.event.listen(Comment.body, 'set', Comment.on_changed_body)

# 创建一个基本的多对多的数据库表
books_tags = db.Table('books_tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
    db.Column('book_id', db.Integer, db.ForeignKey('books.id'))
)

class BookStatus(db.Model):
    __tablename__ = 'book_status'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    description = db.Column(db.Text())
    books = db.relationship('Book',backref='status',lazy='dynamic')
    @staticmethod
    def insert_default(status_list=None):
        if status_list==None:
            status_list = [
                '可借阅',
                '已借出',
                '书籍损坏',
                '不可借阅',
                '其他'
            ]
        for r in status_list:
            c = BookStatus.query.filter_by(name=r).first()
            if c is None:
                c = BookStatus(name=r)
            db.session.add(c)
        db.session.commit()   

class Book(db.Model):
    __tablename__ = 'books'
    __searchable__ = ['name', 'description','author']
    # __analyzer__ = SimpleAnalyzer()
    __analyzer__ =  ChineseAnalyzer() 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    author = db.Column(db.String(32))
    description = db.Column(db.Text(),default=u"暂无评价")

    book_number = db.Column(db.String(50))
    isbn = db.Column(db.String(32))
    publisher = db.Column(db.String(50))

    status_id = db.Column(db.Integer,db.ForeignKey('book_status.id'))
    image_path = db.Column(db.String(256))
    comments = db.relationship('Comment', backref='book', lazy='dynamic')
    uploader_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    category_id = db.Column(db.Integer,db.ForeignKey('categories.id'))
    tags = db.relationship('Tag', secondary=books_tags,backref=db.backref('books', lazy=True))
    rent_events = db.relationship('BookRent', backref='book', lazy='dynamic')
    comments = db.relationship('Comment', backref='book', lazy='dynamic')
    
    # number of this book
    total_count = db.Column(db.Integer,default=0)
    rent_count = db.Column(db.Integer,default=0)

    def can_rent(self):
        return self.total_count-self.rent_count
    def rent_book(self):
        if self.total_count>self.rent_count:
            self.rent_count=self.rent_count+1
        else:
            raise ResourceNotAvalibleError
    def return_book(self):
        if self.rent_count>0:
            self.rent_count=self.rent_count-1
        else:
            raise ResourceNotAvalibleError


class BookRent(db.Model):
    __tablename__ = 'book_rent'
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean,default=True)
    rent_person_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    rent_book_id =  db.Column(db.Integer, db.ForeignKey('books.id'))
    rent_date = db.Column(db.DateTime(), default=datetime.utcnow)
    rent_time = db.Column(db.Integer,default=7)

login_manager.anonymous_user = AnonymousUser

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))