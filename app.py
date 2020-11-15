from flask import Flask
from flask import redirect, render_template, request, session, flash
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
    sql = "SELECT username FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if user is not None:
        flash ("Käyttäjänimi varattu")
        return render_template("newuser.html")
    sql = "INSERT INTO users (username,password) VALUES (:username,:password)"
    db.session.execute(sql, {"username":username,"password":hash_value})
    db.session.commit()
    flash ("Voit kirjautua nyt sisään uudella tunnuksellasi")
    return redirect("/")

@app.route("/newuser",methods=["POST"])
def newuser():
    return render_template("newuser.html")
    
@app.route("/newteam",methods=["POST"])
def newteam():
    return render_template("newteam.html")

@app.route("/newmatch",methods=["POST"])
def newmatch():
    return render_template("newmatch.html")

@app.route("/creatematch",methods=["POST"])
def creatematch():
    joukkue1 = request.form["team1"]
    joukkue2 = request.form["team2"]
    pisteet1 = request.form["team1points"]
    pisteet2 = request.form["team2points"]
    if int(pisteet1) < 0 or int(pisteet1) > 10:
        flash("Nyt vaikuttaa huijaukselta")
        return render_template("newmatch.html")
    if int(pisteet2) < 0 or int(pisteet2) > 10:
        flash("Nyt vaikuttaa huijaukselta")
        return render_template("newmatch.html")

    sql = "SELECT id FROM joukkueet WHERE nimi=:nimi"
    result = db.session.execute(sql, {"nimi":joukkue1})
    team11 = result.fetchone()
    sql = "SELECT id FROM joukkueet WHERE nimi=:nimi"
    result = db.session.execute(sql, {"nimi":joukkue2})
    team22 = result.fetchone()
    if team11 is None:
        flash("Ensimmäistä joukkuetta ei löydy")
        return render_template("newmatch.html")
    if team22 is None:
        flash("Toista joukkuetta ei löydy")
        return render_template("newmatch.html")

    username = session["username"]
    sql = "SELECT id FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone() 
    userid1 = user[0]

    sql = "SELECT joukkue_id FROM joukkueidenpelaajat WHERE jasen_id=:userid"
    result = db.session.execute(sql, {"userid":userid1})
    kayttajanjoukkue = result.fetchall() 
    if kayttajanjoukkue is None:
        flash("Syötä oman joukkueesi tulos man")
        return render_template("newmatch.html")
    if team11 not in kayttajanjoukkue:
        flash("Syötä oman joukkueesi tulos man")
        return render_template("newmatch.html")
    team1 = team11[0]
    team2 = team22[0]

    sql = "INSERT INTO ottelut (joukkue1_id,joukkue2_id,pisteet_koti,pisteet_vieras) VALUES (:joukkue1,:joukkue2,:pisteet1,:pisteet2)"
    db.session.execute(sql, {"joukkue1":team1,"joukkue2":team2,"pisteet1":pisteet1,"pisteet2":pisteet2})
    db.session.commit()
    if pisteet1 > pisteet2:
        sql = "SELECT voitot FROM joukkueet WHERE id=:team1"
        result = db.session.execute(sql, {"team1":team1})
        voitot = result.fetchone()
        lisattyvoitto = voitot[0] + 1

        sql = "SELECT haviot FROM joukkueet WHERE id=:team2"
        result = db.session.execute(sql, {"team2":team2})
        haviot = result.fetchone()
        lisattyhavio = haviot[0] + 1

        sql = "UPDATE joukkueet SET voitot=:lisattyvoitto WHERE id=:team1"
        db.session.execute(sql, {"lisattyvoitto":lisattyvoitto,"team1":team1})
        db.session.commit()

        sql = "UPDATE joukkueet SET haviot=:lisattyhavio WHERE id=:team2"
        db.session.execute(sql, {"lisattyhavio":lisattyhavio,"team2":team2})
        db.session.commit()
        flash ("Hyvä matzi")
        return render_template("newmatch.html")

    if pisteet1 < pisteet2:
        sql = "SELECT voitot FROM joukkueet WHERE id=:team2"
        result = db.session.execute(sql, {"team2":team2})
        voitot = result.fetchone()
        lisattyvoitto = voitot[0] + 1

        sql = "SELECT haviot FROM joukkueet WHERE id=:team1"
        result = db.session.execute(sql, {"team1":team1})
        haviot = result.fetchone()
        lisattyhavio = haviot[0] + 1

        sql = "UPDATE joukkueet SET voitot=:lisattyvoitto WHERE id=:team2"
        db.session.execute(sql, {"lisattyvoitto":lisattyvoitto,"team2":team2})
        db.session.commit()

        sql = "UPDATE joukkueet SET haviot=:lisattyhavio WHERE id=:team1"
        db.session.execute(sql, {"lisattyhavio":lisattyhavio,"team1":team1})
        db.session.commit()
        flash ("Hyvä matzi")
        return render_template("newmatch.html")
    flash("Hmmm...?")
    flash("Tasapeli...? Ratkaistaan sudden deathilla")
    return render_template("newmatch.html")

        


@app.route("/createteam",methods=["POST"])
def createteam():
    username1 = request.form["username1"]
    username2 = request.form["username2"]
    nimia = request.form["team"]
    sql = "SELECT username FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username1})
    user11 = result.fetchone() 
    sql = "SELECT username FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username2})
    user22 = result.fetchone() 
    sql = "SELECT id FROM joukkueet WHERE nimi=:nimi"
    result = db.session.execute(sql, {"nimi":nimia})
    teamm = result.fetchone()
    
    if teamm is not None:
        flash("Nimi varattu")
        return render_template("newteam.html")
    elif user11 == None or user22 == None:
        flash("Käyttäjänimissä probleems")
        return render_template("newteam.html")
    elif username1 == username2:
        flash("Valitse eri pelaajat bro")
        return render_template("newteam.html")
    else:
        user1 = user11[0]
        user2 = user22[0]


        sql = "SELECT id FROM users WHERE username=:username"
        result = db.session.execute(sql, {"username":user1})
        user = result.fetchone() 
        userid1 = user[0]

        sql = "SELECT id FROM users WHERE username=:username2"
        result = db.session.execute(sql, {"username2":user2})
        user = result.fetchone() 
        userid2 = user[0]

        sql = "INSERT INTO joukkueet (nimi,voitot,haviot) VALUES (:nimi,0,0)"
        db.session.execute(sql, {"nimi":nimia})
        db.session.commit()

        sql = "SELECT id FROM joukkueet WHERE nimi=:nimi"
        result = db.session.execute(sql, {"nimi":nimia})
        teamm = result.fetchone() 
        teammm = teamm[0]
        sql = "INSERT INTO joukkueidenpelaajat (joukkue_id,jasen_id) VALUES (:nimi,:jasen_id)"
        db.session.execute(sql, {"nimi":teammm,"jasen_id":userid1})
        db.session.commit()

        sql = "INSERT INTO joukkueidenpelaajat (joukkue_id,jasen_id) VALUES (:nimi,:jasen_id)"
        db.session.execute(sql, {"nimi":teammm,"jasen_id":userid2})
        db.session.commit()

        flash("Joukkue luotu")
        return render_template("etusivu.html")        
@app.route("/etusivu")
def etusivu():
    return render_template("etusivu.html")

@app.route("/login",methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    hash_value = generate_password_hash(password)
    sql = "SELECT password FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()    
    if user == None:
        flash ("Käyttäjää ei löydy")
        return redirect("/")
    
    else:
    	hash_value = user[0]
    	
    if check_password_hash(hash_value,password):
        session["username"] = username
        flash ("Tervetuloa!")
        return render_template("etusivu.html")
    else:
        flash("Väärä salis bro")
        return redirect("/")


@app.route("/logout")
def logout():
    flash ("Hate to see you leave")
    del session["username"]
    return redirect("/")

@app.route("/result")
def result():
    query = request.form["query"]
    

