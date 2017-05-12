import os
# basedir = os.path.abspath(ps.path.dirname(__file__))
DATABASE_URI = os.environ.get('FLASK_BMS_MYSQL_URL') or 'mysql://root:123456@172.17.0.2/'
class Config(object):
    SECRET_KEY = os.environ.get('FLASK_BMS_SECRET') or 'IWILLNOTTELLYOU'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    UPLOAD_PATH = os.path.dirname(os.path.realpath(__file__))+'/uploads'
    FLASK_BMS_EMAIL_PREFIX = '[BMS]'
    FLASK_BMS_EMAIL_SENDER = os.environ.get('FLASK_BMS_EMAIL_USERNAME')
    FLASK_BMS_ADMIN = os.environ.get('FLASK_BMS_ADMIN') or 'admin@bms.com'
    MAIL_SERVER = os.environ.get('FLASK_BMS_EMAIL_SERVER')
    MAIL_USERNAME = os.environ.get('FLASK_BMS_EMAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('FLASK_BMS_EMAIL_PASSWORD')
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

