import unittest
from app.models import User,Role,Permission,AnonymousUser
from app import create_app,db

class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('test')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()


    def test_password_setter(self):
        u = User(password='cat')
        self.assertTrue(u.password_hash is not None)
    def test_no_password_getter(self):
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            u.password
    def test_password_verifycation(self):
        u = User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('cat2'))
    def test_password_salts_are_random(self):
        u = User(password='cat')
        u2 = User(password='cat')
        self.assertTrue(u.password_hash!=u2.password_hash)

    def test_user_roles_and_permissions(self):
        Role.insert_roles()
        u = User(email='test@email.com', password='test')
        self.assertTrue(u.can(Permission.WRITE_ARTICLES))
        self.assertTrue(u.can(Permission.WRITE_COMMENT))
    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.WRITE_ARTICLES))
        self.assertFalse(u.can(Permission.WRITE_COMMENT))
        self.assertFalse(u.can(Permission.ADMIN_CONTENT))
        self.assertFalse(u.can(Permission.ADMIN_USER))