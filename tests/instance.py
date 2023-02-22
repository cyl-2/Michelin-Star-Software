from flask import Flask
from flask_testing import TestCase
from flask_mysqldb import MySQL 
from flask_login import LoginManager
login_manager = LoginManager()
from . import config

class BaseTestCase(TestCase):

    def create_app(self):
        
        app = Flask(__name__)
        app.config["LOGIN_DISABLED"] = True
        app.config["SECRET_KEY"] = "MY_SECRET_KEY"
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SESSION_PROTECTION'] = None
        
        return app
    