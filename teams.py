from flask import Flask
from flask import redirect, render_template, request, session, flash
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from db import db
from app import app

def create_team(username1,username2,team):

        sql = "SELECT id FROM joukkueet WHERE nimi=:nimi"
        result = db.session.execute(sql, {"nimi":team})
        team_sql = result.fetchone()
        if team_sql is not None:
            flash("Nimi varattu")
        
        

        if team_sql is not None or check_users(username1, username2) is False:
            return False

        else:
            user1_id = get_user_id(username1)
            user2_id = get_user_id(username2)
            sessionid = session["user_id"]
            if sessionid is not user1_id and sessionid is not user2_id:
                flash("Sinun pitää kuulua joukkueeseen")
                return False

            sql = "INSERT INTO joukkueet (nimi,voitot,haviot) VALUES (:nimi,0,0)"
            db.session.execute(sql, {"nimi":team})
            db.session.commit()

            team_id = get_team_id(team)

            insert_player_to_team(team_id, user1_id)
            insert_player_to_team(team_id, user2_id)

            del session["username1"]
            del session["username2"]
            del session["team"]
            flash("Joukkue luotu")
            return True
def get_user_id(username):
    sql = "SELECT id FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    return result.fetchone()[0]

def get_team_id(team):
    sql = "SELECT id FROM joukkueet WHERE nimi=:team"
    result = db.session.execute(sql, {"team":team})
    return result.fetchone()[0]

def insert_player_to_team(team, username):
    sql = "INSERT INTO joukkueidenpelaajat (joukkue_id,jasen_id) VALUES (:team,:jasen_id)"
    db.session.execute(sql, {"team":team,"jasen_id":username})
    db.session.commit()

def check_users(username1, username2):
    sql = "SELECT id FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username1})
    username1_sql = result.fetchone()
    sql = "SELECT id FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username2})
    username2_sql = result.fetchone()
    if username1_sql == None or username2_sql == None:
        flash("Käyttäjänimeä ei löydy")
    if username1_sql == username2_sql:
        flash("Valitse eri pelaajat")
    if username1_sql == None or username2_sql == None or username1_sql == username2_sql:
        return False
    return True
def modify_players(username1,username2,team):
    
    sql = "SELECT id FROM joukkueet WHERE nimi=:nimi"
    result = db.session.execute(sql, {"nimi":team})
    team_sql = result.fetchone()
    
    if team_sql is  None:
        flash("Tiimiä ei ole")

    if team_sql is None or check_users(username1, username2) is False:
        return False
    else:
        sql = "DELETE FROM joukkueidenpelaajat WHERE joukkue_id =:teamid"
        db.session.execute(sql, {"teamid":team_sql[0]})
        db.session.commit()
        team_id = get_team_id(team)
        user1_id = get_user_id(username1)
        user2_id = get_user_id(username2)
        insert_player_to_team(team_id, user1_id)
        insert_player_to_team(team_id, user2_id)
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
