from flask import Flask
from os import getenv
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")
app.debug = True

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=15)


import routes

    

