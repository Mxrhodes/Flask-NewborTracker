import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

from environs import Env
env = Env()
env.read_env()

app=Flask(__name__)
app.config['SECRET_KEY'] = '224JDKJSIJ4I6JDFDCF99WNDNKD9'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///babydata.db'
db=SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.loginview = 'login'
login_manager.login_message_category = 'info' 

# Creating the email connection
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = env.str('GMAIL_USER')
app.config['MAIL_PASSWORD'] = env.str("GMAIL_PASS")

mail = Mail(app)

from parenthelper import routes