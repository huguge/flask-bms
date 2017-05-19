#!/usr/bin/env python
import os
import sys

from flask import request
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from app import create_app,db
from app.models import User,Role,BookStatus,Category,Book,Ebook
import flask_whooshalchemyplus as whooshalchemy

reload(sys)
sys.setdefaultencoding('utf-8')

app = create_app(os.getenv('FLASK_BMS_ENV') or 'default')
whooshalchemy.whoosh_index(app, Book)
whooshalchemy.whoosh_index(app, Ebook)
if os.getenv('FLASK_BMS_ENV') != 'production':
    @app.after_request
    def app_after_request(response):
        if request.endpoint != 'static':
            return response
        response.cache_control.max_age = 0
        return response
config = app.config
manager = Manager(app)
migrate = Migrate(app,db)
def make_shell_context():
    return dict(app=app,db=db,Role=Role,User=User,Book=Book,Ebook=Ebook)
manager.add_command("shell",Shell(make_context=make_shell_context))
manager.add_command("db",MigrateCommand)


@manager.command
def db_init_default():
    """Run the database init """
    for i in [Role,Category,BookStatus]:
        i.insert_default()
    print 'insert default data into database success'

@manager.command
def test():
    """Run the unit tests"""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

if __name__ == '__main__':
    manager.run()