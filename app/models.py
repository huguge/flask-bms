# -*- coding:utf-8 -*- 

from datetime import datetime
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin,AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from app import db, login_manager
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
    def insert_roles():
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
    role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean,default=False)
    name = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    created_at = db.Column(db.DateTime(),default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(),default=datetime.utcnow)
    
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def __init__(self,**kw):
        super(User,self).__init__(**kw)
        if self.role is None:
            if self.email == current_app.config['FLASK_BMS_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
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
    def can(self,permission):
        return False
    def is_super_admin(self):
        return False
    def is_content_admin(self):
        return False


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

login_manager.anonymous_user = AnonymousUser