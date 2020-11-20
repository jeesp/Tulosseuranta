from flask import Flask
from flask import redirect, render_template, request, session, flash
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from db import db
from app import app
import kirjautuminen, joukkueet, ottelut, highscore

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signin",methods=["GET","POST"])
def signin():
    if request.method == "GET":
        return render_template("newuser.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if kirjautuminen.uusikayttaja(username,password):
            return redirect("/")
        else:
            return render_template("newuser.html")
    
@app.route("/newuser",methods=["GET","POST"])
def newuser():
    return render_template("newuser.html")

@app.route("/etusivu",methods=["GET","POST"])
def etusivu():
    return render_template("index.html")

@app.route("/newteam",methods=["GET", "POST"])
def newteam():
        if kirjautuminen.user_id == 0:
            redirect("/")
        return render_template("newteam.html")

@app.route("/newmatch",methods=["GET","POST"])
def newmatch():
    return render_template("newmatch.html")

@app.route("/creatematch",methods=["GET","POST"])
def creatematch():
    if request.method == "GET":
        return render_template("index.html")
    if request.method == "POST":
        joukkue1 = request.form["team1"]
        joukkue2 = request.form["team2"]
        pisteet1 = request.form["team1points"]
        pisteet2 = request.form["team2points"]
        if joukkue1 is "" or joukkue2 is "" or pisteet1 is "" or pisteet2 is "":
            flash("Jokin kenttä oli tyhjä.")
            return render_template("newmatch.html") 
        if int(pisteet1) < 0 or int(pisteet1) > 10 or int(pisteet2) < 0 or int(pisteet2) > 10:
            flash("Nyt vaikuttaa huijaukselta.. Pisteitä liikaa tai liian vähän")
            return render_template("newmatch.html")
        
        if ottelut.ottelupelattu(joukkue1,joukkue2,pisteet1,pisteet2):
            return render_template("index.html")
        else:
            return render_template("newmatch.html")

@app.route("/createteam",methods=["GET","POST"])
def createteam():
    if request.method == "GET":
        return render_template("index.html")
    if request.method == "POST":
        username1 = request.form["username1"]
        username2 = request.form["username2"]
        team = request.form["team"]
        if username1 is "" or username2 is "" or team is "":
            flash("Kenttä tyhjä")
            return render_template("newteam.html")
        if joukkueet.createteam(username1,username2,team):
            return render_template("index.html")
        else:
            return render_template("newteam.html")

@app.route("/highscoreteam",methods=["GET","POST"])
def highscores():
    list = highscore.highscoreteam()
    return render_template("highscoreteam.html", joukkueet=list)

@app.route("/lowscoreteam",methods=["GET","POST"])
def lowscores():
    list = highscore.lowscoreteam()
    return render_template("lowscoreteam.html", joukkueet=list)

@app.route("/highscoreplayer",methods=["GET","POST"])
def highscoreplayer():
    list = highscore.highscoreplayer()
    return render_template("highscoreplayer.html", pelaajat=list)

@app.route("/lowscoreplayer",methods=["GET","POST"])
def lowscoreplayer():
    list = highscore.lowscoreplayer()
    return render_template("lowscoreplayer.html", pelaajat=list)
    
@app.route("/login",methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if kirjautuminen.tarkistus(username,password):
            return render_template("index.html")
        else:
            return render_template("login.html")

@app.route("/logout")
def logout():
    flash ("Hate to see you leave")
    del session["user_id"]
    return redirect("/")

@app.route("/result")
def result():
    query = request.form["query"]