from flask import Flask
from flask_mongoengine import MongoEngine#, Document
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
import os

app = Flask(__name__)

app.config['MONGODB_SETTINGS'] = {
    'db' : 'FYPDatabase.db',
    'host': 'mongodb://localhost:27017/FYPDatabase'
}

app.config['SECRET_KEY'] = '99d5a8a07ee30c0074b6b3ccfcaf7116'
bcrypt = Bcrypt(app)
db = MongoEngine(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = "chuzu26@gmail.com"
app.config['MAIL_PASSWORD'] = "uilrcmknoouqknnm"
mail = Mail(app)

#client = pymongo.MongoClient("mongodb://localhost:27017/")
#print(client)
#db = client["FYPDatabase"]
#collection = db['UserData']

from JournalRecommendationSystem import routes