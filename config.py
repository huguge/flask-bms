import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# basedir = os.path.abspath(ps.path.dirname(__file__))
DATABASE_URI = os.environ.get('FLASK_BMS_MYSQL_URL')
class Config(object):
    SECRET_KEY = os.environ.get('FLASK_BMS_SECRET')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    DEBUG = os.environ.get('FLASK_BMS_DEBUG') or False
    ENV_PATH = dotenv_path
    UPLOAD_PATH = os.path.dirname(os.path.realpath(__file__))+'/app/static/uploads'
    WHOOSH_BASE = os.path.dirname(os.path.realpath(__file__))+'/whoosh'
    SQLALCHEMY_TRACK_MODIFICATIONS = True    
    FLASK_BMS_EMAIL_PREFIX = os.environ.get('FLASK_BMS_EMAIL_PREFIX')
    FLASK_BMS_EMAIL_SENDER = os.environ.get('FLASK_BMS_EMAIL_USERNAME')
    FLASK_BMS_ADMIN = os.environ.get('FLASK_BMS_ADMIN')
    MAIL_SERVER = os.environ.get('FLASK_BMS_EMAIL_SERVER')
    MAIL_USERNAME = os.environ.get('FLASK_BMS_EMAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('FLASK_BMS_EMAIL_PASSWORD')
    # max_page_number
    FLASK_BMS_MAX_PER_PAGE = int(os.environ.get('FLASK_MAX_PER_PAGE')) or 10
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = DATABASE_URI+'flaskbms_development?charset=utf8'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = DATABASE_URI+'flaskbms_production?charset=utf8'
class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = DATABASE_URI+'flaskbms_test?charset=utf8'

config = {
    'development':DevelopmentConfig,
    'test':TestConfig,
    'production':ProductionConfig,
    'default':DevelopmentConfig
}

