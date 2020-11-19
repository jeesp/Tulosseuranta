from flask import Flask
from flask import redirect, render_template, request, session, flash
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from db import db
from app import app

def tarkistus(username, password):
    sql = "SELECT password, id FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()    
    if user == None:
        flash ("Käyttäjää ei löydy")
        return False
    else:
        if check_password_hash(user[0],password):
            session["user_id"] = user[1]
            flash ("Tervetuloa!")

            return True
        else:
            flash("Väärä salis bro")
            return False

def user_id():
    return session.get("user_id",0)

def uusikayttaja(username,password):
    hash_value = generate_password_hash(password)
    sql = "SELECT username FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if user is not None:
        flash ("Käyttäjänimi varattu")
        return False
    sql = "INSERT INTO users (username,password) VALUES (:username,:password)"
    db.session.execute(sql, {"username":username,"password":hash_value})
    db.session.commit()
    flash ("Voit kirjautua nyt sisään uudella tunnuksellasi")
    return True