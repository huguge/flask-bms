# -*- coding:utf-8 -*-  

# 第三方模块
from flask import Flask, render_template
from flask_moment import Moment
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# 定义用户的登入认证

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
login_manager.login_message = u"请输入用户名和密码后点击登入进入系统"
# 用户定义模块
from config import config

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__,static_folder='static')
    
    app.config.from_object(config[config_name])
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    from app.main import main as main_blueprint
    from app.auth import auth as auth_blueprint
    from app.admin import admin as admin_blueprint
    # from app.api_1_0 import api as api_1_0_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint,url_prefix='/auth')
    app.register_blueprint(admin_blueprint,url_prefix='/admin')


    return app