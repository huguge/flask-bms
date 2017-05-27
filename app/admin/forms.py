# -*- coding:utf-8 -*- 
from flask_wtf import FlaskForm
from wtforms.validators import Required,Email,Length,Regexp,EqualTo,DataRequired
from wtforms import StringField,SubmitField,BooleanField,TextAreaField,SelectField,IntegerField
from wtforms import ValidationError
from flask_wtf.file import FileField,FileRequired,FileAllowed
from app.models import Role,Category,Tag,BookStatus


class ConfigForm(FlaskForm):
    FLASK_BMS_ADMIN = StringField(u'默认管理员账号', validators=[DataRequired(message="该选项不能为空"),Length(1,64)],render_kw={'placeholder':'必填项目'})
    MAIL_SERVER = StringField(u'默认邮件服务器地址', validators=[DataRequired(message="该选项不能为空"),Length(1,64)],render_kw={'placeholder':'必填项目'})
    MAIL_USERNAME = StringField(u'默认邮件服务器地址', validators=[DataRequired(message="该选项不能为空"),Length(1,64)],render_kw={'placeholder':'必填项目'})
    MAIL_PASSWORD = StringField(u'默认邮箱密码', validators=[DataRequired(message="该选项不能为空"),Length(1,64)],render_kw={'placeholder':'必填项目'})
    
    UPLOAD_PATH = StringField(u'上传路径', validators=[DataRequired(message="该选项不能为空"),Length(1,200)],render_kw={'placeholder':'必填项目'})
    WHOOSH_BASE = StringField(u'全文检索路径', validators=[DataRequired(message="该选项不能为空"),Length(1,200)],render_kw={'placeholder':'必填项目'})
    
    FLASK_BMS_MAX_PER_PAGE = IntegerField(u'列表显示最大数量',default=10)
    SQLALCHEMY_DATABASE_URI = StringField(u'数据库连接配置', validators=[DataRequired(message="该选项不能为空"),Length(1,64)],render_kw={'placeholder':'必填项目'})
    SQLALCHEMY_TRACK_MODIFICATIONS = BooleanField(u'数据库跟踪配置',default=True)
    DEBUG = BooleanField(u'DEBUG模式',default=True)