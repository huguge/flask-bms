# -*- coding:utf-8 -*- 
import json
import os

from flask import render_template, session, redirect, url_for,flash,current_app,request,send_file,abort,jsonify
from sqlalchemy.sql import text
from flask_login import login_required,current_user


from app.admin import admin 
from app import db
from app.models import User, Ebook, Comment, Permission,Book,Tag, BookRent,Role,ConfigTable
from app.lib import super_admin_require
from config import config
from app.admin.forms import ConfigForm

@admin.route('/')
@login_required
@super_admin_require
def admin_dashboard():
    users_count = User.query.count()
    # select sum(total_count) as total from books;
    try:
        sql = text("select sum(total_count) as total from books")
        books_count = db.engine.execute(sql).fetchall()[0][0]
        if books_count is None:
            books_count =0
    except:
        books_count=0

    # 下载最多的图书统计 
    best_download_books = Ebook.query.order_by(Ebook.downloads.desc()).limit(10).all()
    best_download_books_name = [b.name for b in best_download_books]
    best_download_books_downloads = [b.downloads for b in best_download_books]

    # 下载最多的用户统计
    try:
        most_download_users_sql = text("select user_id,username,count(*) as downloads from ebooks_download inner join users on ebooks_download.user_id=users.id group by user_id order by downloads desc limit 10;")
        most_download_users_list = db.engine.execute(most_download_users_sql).fetchall()
        most_download_users_username = [m[1] for m in most_download_users_list]
        most_download_users_downloads = [m[2] for m in most_download_users_list]
    except Exception as e:
        most_download_users_username=[]
        most_download_users_downloads=[]
    # 最近7天的下载数据统计

    ebooks_count = Ebook.query.count()
    bookrents_count = BookRent.query.filter_by(active=1).count()

    try:
        download_statics_sql = text("select count(*) as downloads from ebooks_download;")
        download_count = db.engine.execute(download_statics_sql).fetchall()[0][0]
    except Exception:
        download_count = 0

    count = [users_count,books_count,ebooks_count,bookrents_count,download_count]
    
    try:
        each_day_download_sql = text("select date(download_time) as each_day,count(*) from ebooks_download where download_time > current_date - interval 7 day group by each_day order by each_day asc limit 7;")
        each_day_download = db.engine.execute(each_day_download_sql).fetchall()
        each_day_download_date = [str(m[0]) for m in each_day_download]
        each_day_download_count = [m[1] for m in each_day_download]
    except Exception as e:
        print e
        each_day_download_date = []
        each_day_download_count = []        

    return render_template('admin/index.html', 
                            app_name='Flask-BMS',
                            best_download_books_name=json.dumps(best_download_books_name),
                            best_download_books_downloads=json.dumps(best_download_books_downloads),
                            most_download_users_username=json.dumps(most_download_users_username),
                            most_download_users_downloads=json.dumps(most_download_users_downloads),
                            each_day_download_date=json.dumps(each_day_download_date),
                            each_day_download_count=json.dumps(each_day_download_count),
                            count=count)


@admin.route('/user')
@login_required
@super_admin_require
def admin_user():
    roles = Role.query.all()
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search','')
    if search is None or search=='':    
        pagination = User.query.order_by(User.id.asc()).paginate(page,per_page=current_app.config['FLASK_BMS_MAX_PER_PAGE'])
    else:
        pagination = User.query.whoosh_search(search).order_by(User.created_at.desc()).paginate(page,per_page=current_app.config['FLASK_BMS_MAX_PER_PAGE'])
    users_list = pagination.items    
    return render_template('admin/user.html',roles=roles,users = users_list, pagination = pagination, app_name='Flask-BMS')


@admin.route('/toggle_user_confirmed/<int:id>')
@login_required
@super_admin_require
def toggle_user_confirmed(id):
    user = User.query.get_or_404(id)
    user.confirmed = not user.confirmed
    db.session.add(user)
    db.session.commit()
    return redirect(request.referrer or url_for("admin.admin_user"))

@admin.route('/change_user_auth/<int:id>/<int:role_id>')
@login_required
@super_admin_require
def change_user_auth(id,role_id):
    user = User.query.get_or_404(id)
    user.role_id = int(role_id)
    db.session.add(user)
    db.session.commit()
    return redirect(request.referrer or url_for("admin.admin_user"))

@admin.route('/config', methods=['POST','GET'])
@login_required
@super_admin_require
def admin_config():
    form = ConfigForm()
    # 从配置config全局对象读取数据内容到表中
    config_name_list = [i for i in dir(form) if i.isupper()]
    env = os.getenv('FLASK_BMS_ENV') or 'default'
    if form.validate_on_submit():
        for c in config_name_list:
            data = ConfigTable.query.filter_by(name=c).first()
            if data is None:
                data = ConfigTable(name=c,config_value=str(form[c].data),type_name=type(form[c].data).__name__)
            else:
                data.name=c
                data.config_value = str(form[c].data)
                data.type_name = type(form[c].data).__name__
            db.session.add(data)
            setattr(config[env],c,form[c].data)
        # 保存数据库
        db.session.commit()
        return redirect(url_for('admin.admin_config'))
    else:
        # 从配置config全局对象读取数据内容到表中
        config_name_list = [i for i in dir(form) if i.isupper()]
        env = os.getenv('FLASK_BMS_ENV') or 'default'
        for c in config_name_list:
            form[c].data = getattr(config[env],c)
        return render_template('admin/config.html',form=form,app_name='Flask-BMS')

@admin.route('/about')
@login_required
@super_admin_require
def admin_about():
    return render_template('admin/about.html', app_name='Flask-BMS')