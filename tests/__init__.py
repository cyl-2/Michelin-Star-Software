from flask import Flask
from extensions import db

def create_app(database_uri="sqlite:///db.sqlite3"):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
    app.config["SECRET_KEY"] = ""

    db.init_app()