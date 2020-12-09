from flask import Flask
from flask import redirect, render_template, request, session, flash
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from db import db
from app import app

def create_team(username1,username2,team):
    
        sql = "SELECT username FROM users WHERE username=:username"
        result = db.session.execute(sql, {"username":username1})
        username1_sql = result.fetchone()
        sql = "SELECT username FROM users WHERE username=:username"
        result = db.session.execute(sql, {"username":username2})
        username2_sql = result.fetchone()
        sql = "SELECT id FROM joukkueet WHERE nimi=:nimi"
        result = db.session.execute(sql, {"nimi":team})
        team_sql = result.fetchone()
        
        if team_sql is not None:
            flash("Nimi varattu")
        if username1_sql == None or username2_sql == None:
            flash("Käyttäjänimissä probleems")
        if username1_sql == username2_sql:
            flash("Valitse eri pelaajat bro")

        if team_sql is not None or username1_sql == None or username2_sql == None or username1_sql == username2_sql:
            return False
        else:
            username1_sql = username1_sql[0]
            username2_sql = username2_sql[0]
            sql = "SELECT id FROM users WHERE username=:username"
            result = db.session.execute(sql, {"username":username1_sql})
            user = result.fetchone() 
            user1_id = user[0]

            sql = "SELECT id FROM users WHERE username=:username2"
            result = db.session.execute(sql, {"username2":username2_sql})
            user = result.fetchone() 
            user2_id = user[0]

            sql = "INSERT INTO joukkueet (nimi,voitot,haviot) VALUES (:nimi,0,0)"
            db.session.execute(sql, {"nimi":team})
            db.session.commit()

            sql = "SELECT id FROM joukkueet WHERE nimi=:nimi"
            result = db.session.execute(sql, {"nimi":team})
            team_id = result.fetchone()[0]
            sql = "INSERT INTO joukkueidenpelaajat (joukkue_id,jasen_id) VALUES (:nimi,:jasen_id)"
            db.session.execute(sql, {"nimi":team_id,"jasen_id":user1_id})
            db.session.commit()

            sql = "INSERT INTO joukkueidenpelaajat (joukkue_id,jasen_id) VALUES (:nimi,:jasen_id)"
            db.session.execute(sql, {"nimi":team_id,"jasen_id":user2_id})
            db.session.commit()
            del session["username1"]
            del session["username2"]
            del session["team"]
            flash("Joukkue luotu")
            return True

def modify_players(username1,username2,team):
    sql = "SELECT id FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username1})
    username1_sql = result.fetchone()
    sql = "SELECT id FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username2})
    username2_sql = result.fetchone()
    sql = "SELECT id FROM joukkueet WHERE nimi=:nimi"
    result = db.session.execute(sql, {"nimi":team})
    team_sql = result.fetchone()
    
    if team_sql is  None:
        flash("Tiimiä ei ole")
    if username1_sql == None or username2_sql == None:
        flash("Käyttäjänimeä ei löydy")
    if username1_sql == username2_sql:
        flash("Valitse eri pelaajat")
    if team_sql is None or username1_sql == None or username2_sql == None or username1_sql == username2_sql:
        return False
    else:
        sql = "DELETE FROM joukkueidenpelaajat WHERE joukkue_id =:teamid"
        db.session.execute(sql, {"teamid":team_sql[0]})
        db.session.commit()
        sql = "INSERT INTO joukkueidenpelaajat (joukkue_id,jasen_id) VALUES (:joukkue_id,:jasen_id)"
        db.session.execute(sql, {"joukkue_id":team_sql[0],"jasen_id":username1_sql[0]})
        db.session.commit()
        sql = "INSERT INTO joukkueidenpelaajat (joukkue_id,jasen_id) VALUES (:joukkue_id,:jasen_id)"
        db.session.execute(sql, {"joukkue_id":team_sql[0],"jasen_id":username2_sql[0]})
        db.session.commit()
        flash("Muutos suoritettu")
        return True

def delete_team(team):
    sql = "SELECT id FROM joukkueet WHERE nimi=:nimi"
    result = db.session.execute(sql, {"nimi":team})
    team_sql = result.fetchone()
    if team_sql is  None:
        flash("Tiimiä ei ole")
        return False
    else:
        sql = "DELETE FROM joukkueet WHERE id =:id"
        db.session.execute(sql, {"id":team_sql[0]})
        db.session.commit()
        flash("Joukkue poistettu")
        return True
