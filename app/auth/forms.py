# -*- coding:utf-8 -*- 
from flask_wtf import FlaskForm
from wtforms.validators import Required,Email,Length,Regexp,EqualTo
from wtforms import StringField,SubmitField,PasswordField,BooleanField
from wtforms import ValidationError
from app.models import User
# 定义登入表单

class LoginForm(FlaskForm):
    email = StringField(u'用户邮箱', validators=[Required(),Length(1,64),Email()])
    password = PasswordField(u'登入密码', validators=[Required()])
    remember_me = BooleanField('记住登入状态')
    submit = SubmitField(u'登入系统')

class RegistationForm(FlaskForm):
    email = StringField(u'用户邮箱', validators=[Required(),Length(1,64),Email()])
    username = StringField(u'用户名',validators=[Required(),
        Length(1,64),
        Regexp('^[a-zA-Z][a-zA-Z0-9._]*$',0,'用户名只能包含字母数字_和.')])
    password = PasswordField(u'输入密码',validators=[Required(),
        Length(6,40),
        EqualTo('password_confirm',message='密码两次输入不匹配')])
    password_confirm = PasswordField(u'再次输入密码', validators=[Required()])
    submit = SubmitField(u'点击注册')
    
    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(u'输入邮箱账号已被占用')
    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(u'输入用户名已被占用')

