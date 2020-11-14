from flask import Flask
from flask import redirect, render_template, request, session
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")
app.debug = True
db = SQLAlchemy(app)
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signin",methods=["POST"])
def signin():
    username = request.form["username"]
    password = request.form["password"]
    hash_value = generate_password_hash(password)
    sql = "INSERT INTO users (username,password) VALUES (:username,:password)"
    db.session.execute(sql, {"username":username,"password":hash_value})
    db.session.commit()
    session["newuser"] = 1
    return redirect("/")

@app.route("/newuser",methods=["POST"])
def newuser():
    return render_template("newuser.html")
    
@app.route("/login",methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    hash_value = generate_password_hash(password)
    sql = "SELECT password FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()    
    if user == None:
    	return redirect("/")
    else:
    	hash_value = user[0]
    	
    if check_password_hash(hash_value,password):
        session["username"] = username
        session["newuser"] = 1
        session["wrong"] = 1
        return render_template("result.html")
    else:
        session["wrong"] = 1
        return redirect("/")
        
    session["username"] = username
    return redirect("/")


@app.route("/logout")
def logout():
    del session["newuser"]
    del session["wrong"]   
    del session["username"]
    return redirect("/")

@app.route("/result")
def result():
    query = request.form["query"]
    

