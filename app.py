from flask import Flask
from flask import redirect, render_template, request, session, flash
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")
app.debug = True

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=15)


import routes

    

