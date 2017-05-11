# -*- coding:utf-8 -*- 


from flask import render_template,session,redirect,url_for,flash,request
from flask_login import login_user,login_required,logout_user,current_user
from app.auth import auth
from app.auth.forms import LoginForm,RegistationForm,ChangePasswordForm,ForgetPasswordForm,ResetForgetPasswordForm
from app.models import User
from app import db
from app import email
@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
            username=form.username.data,
            password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        email.send_email(user.email,
            u'确认邮箱账号',
            'auth/email/confirm',
            user=user,
            token=token)
        flash('激活邮件已经发送给您，请前往邮箱完成激活')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html',form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash(u'认证信息无效,请重新输入')
    return render_template('auth/login.html', app_name='Flask-BMS', form=form)
        
@auth.route('/logout',methods = ['GET'])
@login_required
def logout():
    # session.clear()
    logout_user()
    flash('您已登出系统,欢迎下次访问')
    return redirect(url_for('main.index'))

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confim_token(token):
        flash(u'您已激活账户，欢迎访问系统')
    else:
        flash(u'激活链接已失效或已过期')
    return redirect(url_for('main.index'))


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
    if current_user.is_authenticated and not current_user.confirmed and not request.endpoint.startswith('auth') and request.endpoint !='static':
        return redirect(url_for('auth.unconfirmed'))
@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html',user=current_user)

@auth.route('/resend_confirm_email')
@login_required
def resend_confirm_email():
    token = current_user.generate_confirmation_token()
    email.send_email(current_user.email,
            u'激活邮箱账号',
            'auth/email/confirm',
            user=current_user,
            token=token)
    flash(u'新的激活邮件已经发送给您，请前往邮箱完成激活')
    return redirect(url_for('main.index'))


@auth.route('/changepassword',methods = ['POST','GET'])
@login_required
def changepassword():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            current_user.password=form.new_password.data
            flash(u'密码修改成功，您可退出登入并使用新密码登入系统')
            return redirect(url_for('auth.changepassword'))
        flash(u'提交信息无效,请重新输入')
    return render_template('auth/password/changepassword.html', app_name='Flask-BMS', form=form)

@auth.route('/forgetpassword',methods = ['POST','GET'])
def forgetpassword():
    form = ForgetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None:
            token = user.generate_confirmation_token()
            email.send_email(user.email,
                    u'重置个人密码操作',
                    'auth/email/forgetpassword',
                    username=user.username,
                    token=token)
            flash(u'重置邮件已发送，请登入邮箱进行重置操作')
            return redirect(url_for('auth.forgetpassword'))
        flash(u'提交信息无效,请重新输入')
    return render_template('auth/password/forgetpassword.html', app_name='Flask-BMS', form=form)

@auth.route('/resetpassword/<username>/<token>',methods = ['POST','GET'])
def resetpassword(username,token):
    current_user = User.query.filter_by(username=username).first()
    if current_user is not None:
        form = ResetForgetPasswordForm()
        if form.validate_on_submit():
            current_user.password=form.password.data
            flash(u'密码修改成功，您可使用新密码登入系统')
            return redirect(url_for('auth.login'))
        return render_template('auth/password/resetpassword.html', app_name='Flask-BMS', form=form)
        # return redirect(url_for('auth.resetpassword',token=token)
    else:
        flash(u'激活链接无效')
        return redirect(url_for('auth.login'))