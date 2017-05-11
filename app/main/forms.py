# -*- coding:utf-8 -*- 
from flask_wtf import FlaskForm
from wtforms.validators import Required,Email,Length,Regexp,EqualTo
from wtforms import StringField,SubmitField,BooleanField,TextAreaField,SelectField
from wtforms import ValidationError

class EditProfileForm(FlaskForm):
    name = StringField(u'用户真实姓名', validators=[Length(1,64)])
    about_me = TextAreaField(u'关于我')
    submit = SubmitField(u'修改信息')

class AdminProfileForm(FlaskForm):
    name = StringField(u'用户真实姓名', validators=[Length(1,64)])
    about_me = TextAreaField(u'关于我')
    
    # 管理员编辑内容
    email = StringField('用户邮件地址',validators=[Required(),Length(1,64),Email()])
    username = StringField(u'用户名',validators=[Required(),
        Length(1,64,message='长度不得大于64位'),
        Regexp('^[a-zA-Z][a-zA-Z0-9._]*$',0,'用户名只能包含字母数字_和.')])
    
    confirmed = BooleanField('激活用户账号')
    role = SelectField('选择角色',coerce=int)

    submit = SubmitField(u'修改信息')

    def __init__(self,user,*args,**kw):
        super(EditProfileForm,self).__init__(*args,**kw)
        self.role.choices = [(role.id,role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user
    
    def validate_email(self,field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError('邮件已被占用')
    def validate_username(self,field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已被占用')