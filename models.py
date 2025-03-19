
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# create the app
app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
# initialize the database
db = SQLAlchemy(app)
# initialize the app with the extension

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String)
    
    def __init__(self, username, email):
        self.username = username
        self.email = email

with app.app_context():
    user_1 = User('John_001', 'johnny@gmail.com')
    db.session.add(user_1)
    db.session.commit()
    # users = db.session.query().first()
    # print(users)
    # db.create_all()