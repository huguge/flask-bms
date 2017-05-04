# -*- coding:utf-8 -*- 
from flask_wtf import FlaskForm
from wtforms.validators import Required
from wtforms import StringField,SubmitField,PasswordField
# 定义登入表单

class LoginForm(FlaskForm):
    username = StringField(u'用户名', validators=[Required()])
    password = PasswordField(u'密码', validators=[Required()])
    submit = SubmitField(u'提交')