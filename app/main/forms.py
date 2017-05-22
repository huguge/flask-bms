# -*- coding:utf-8 -*- 
from flask_wtf import FlaskForm
from wtforms.validators import Required,Email,Length,Regexp,EqualTo,DataRequired
from wtforms import StringField,SubmitField,BooleanField,TextAreaField,SelectField,IntegerField
from wtforms import ValidationError
from flask_wtf.file import FileField,FileRequired,FileAllowed
from app.models import Role,Category,Tag,BookStatus

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

# 上传图书表单
class UploadEbookForm(FlaskForm):
    name = StringField(u'名称', validators=[Length(1,64)])
    author = StringField(u'作者', validators=[Length(1,32)])
    category = SelectField('选择类别',coerce=int)
    tag = StringField(u'图书标签',render_kw={'placeholder':'请使用;分割'})
    description = TextAreaField(u'简短介绍')
    ebook_file = FileField('上传电子书',validators=[FileRequired(),FileAllowed(['pdf','doc','docx'],'暂时仅支持pdf与word文档')])
    submit = SubmitField(u'点击创建')
    def __init__(self,*args,**kw):
        super(UploadEbookForm,self).__init__(*args,**kw)
        self.category.choices = [(c.id,c.name) for c in Category.query.order_by(Category.name).all()]
# 上传图书表单
class EditEBookForm(FlaskForm):
    name = StringField(u'名称', validators=[Length(1,64)])
    author = StringField(u'作者', validators=[Length(1,32)])
    category = SelectField('选择类别',coerce=int)
    tag = StringField(u'图书标签',render_kw={'placeholder':'请使用;分割'})
    description = TextAreaField(u'简短介绍')
    ebook_file = FileField('上传电子书',validators=[FileAllowed(['pdf','doc','docx'],'暂时仅支持pdf与word文档')])
    submit = SubmitField(u'点击修改')
    def __init__(self,*args,**kw):
        super(EditEBookForm,self).__init__(*args,**kw)
        self.category.choices = [(c.id,c.name) for c in Category.query.order_by(Category.name).all()]
class BookForm(FlaskForm):
    name = StringField(u'名称', validators=[DataRequired(message="该选项不能为空"),Length(1,64)],render_kw={'placeholder':'必填项目'})
    author = StringField(u'作者', validators=[Length(1,32)],render_kw={'placeholder':'必填项目'})
    publisher = StringField(u'出版社',render_kw={'placeholder':'无'})
    book_number = StringField(u'编号',render_kw={'placeholder':'无'})
    isbn = StringField(u'图书ISBN',render_kw={'placeholder':'无'})
    tag = StringField(u'图书标签',render_kw={'placeholder':'请使用;分割'})
    total_count = IntegerField(u'图书数量',default=0)
    category = SelectField('选择类别',coerce=int)
    status = SelectField(u'选择图书状态',coerce=int)
    description = TextAreaField(u'简短介绍',render_kw={'placeholder':'无'})
    book_img = FileField('上传封面',validators=[FileRequired(),FileAllowed(['jpg','png'],'暂时仅支持jpg与png文档')])
    def __init__(self,*args,**kw):
        super(BookForm,self).__init__(*args,**kw)
        self.status.choices = [(c.id,c.name) for c in BookStatus.query.order_by(BookStatus.name).all()] 
        self.category.choices = [(c.id,c.name) for c in Category.query.order_by(Category.name).all()]   
class AddBookForm(BookForm):
    # book_img = FileField('上传封面',validators=[FileRequired(),FileAllowed(['jpg','png'],'暂时仅支持jpg与png文档')])
    submit = SubmitField(u'点击创建')
    def __init__(self,*args,**kw):
        super(AddBookForm,self).__init__(*args,**kw)

class EditBookForm(BookForm):
    book_img = FileField('上传封面',validators=[FileAllowed(['jpg','png'],'暂时仅支持jpg与png文档')])
    submit = SubmitField(u'点击修改')
    def __init__(self,*args,**kw):
        super(EditBookForm,self).__init__(*args,**kw)



class CommentForm(FlaskForm):
    body = TextAreaField('',validators=[Required()])
    submit = SubmitField('提交评论')

