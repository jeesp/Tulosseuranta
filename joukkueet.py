from flask import Flask
from flask import redirect, render_template, request, session, flash
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from db import db
from app import app

def createteam(username1,username2,team):
    
        sql = "SELECT username FROM users WHERE username=:username"
        result = db.session.execute(sql, {"username":username1})
        username1sql = result.fetchone()
        sql = "SELECT username FROM users WHERE username=:username"
        result = db.session.execute(sql, {"username":username2})
        username2sql = result.fetchone()
        sql = "SELECT id FROM joukkueet WHERE nimi=:nimi"
        result = db.session.execute(sql, {"nimi":team})
        teamsql = result.fetchone()
        
        if teamsql is not None:
            flash("Nimi varattu")
        if username1sql == None or username2sql == None:
            flash("Käyttäjänimissä probleems")
        if username1sql == username2sql:
            flash("Valitse eri pelaajat bro")

        if teamsql is not None or username1sql == None or username2sql == None or username1sql == username2sql:
            return False
        else:
            username1sql = username1sql[0]
            username2sql = username2sql[0]
            sql = "SELECT id FROM users WHERE username=:username"
            result = db.session.execute(sql, {"username":username1sql})
            user = result.fetchone() 
            userid1 = user[0]

            sql = "SELECT id FROM users WHERE username=:username2"
            result = db.session.execute(sql, {"username2":username2sql})
            user = result.fetchone() 
            userid2 = user[0]

            sql = "INSERT INTO joukkueet (nimi,voitot,haviot) VALUES (:nimi,0,0)"
            db.session.execute(sql, {"nimi":team})
            db.session.commit()

            sql = "SELECT id FROM joukkueet WHERE nimi=:nimi"
            result = db.session.execute(sql, {"nimi":team})
            teamid = result.fetchone()[0]
            sql = "INSERT INTO joukkueidenpelaajat (joukkue_id,jasen_id) VALUES (:nimi,:jasen_id)"
            db.session.execute(sql, {"nimi":teamid,"jasen_id":userid1})
            db.session.commit()

            sql = "INSERT INTO joukkueidenpelaajat (joukkue_id,jasen_id) VALUES (:nimi,:jasen_id)"
            db.session.execute(sql, {"nimi":teamid,"jasen_id":userid2})
            db.session.commit()
            del session["username1"]
            del session["username2"]
            del session["team"]
            flash("Joukkue luotu")
            return True