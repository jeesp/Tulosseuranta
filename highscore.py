from flask import Flask
from flask import redirect, render_template, request, session, flash
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from db import db
from app import app

def highscore_for_teams():
    sql = "SELECT X.nimi, SUM(X.voitot), SUM(X.haviot),(SELECT ROUND((SUM(X.voitot)*1.0)/coalesce(NULLIF(SUM(X.haviot),0),1),2) AS DECIMAL) FROM Joukkueet X GROUP BY X.nimi ORDER BY SUM(X.voitot) DESC, SUM(X.haviot) ASC LIMIT 5"
    result = db.session.execute(sql)
    return result.fetchall()
def lowscore_for_teams():
    sql = "SELECT X.nimi, SUM(X.voitot), SUM(X.haviot),(SELECT ROUND((SUM(X.voitot)*1.0)/coalesce(NULLIF(SUM(X.haviot),0),1),2) AS DECIMAL) FROM Joukkueet X GROUP BY X.nimi ORDER BY SUM(X.voitot) ASC, SUM(X.haviot) DESC LIMIT 5"
    result = db.session.execute(sql)
    return result.fetchall()
def highscore_for_players():
    sql = "SELECT S.username, SUM(X.voitot), SUM(X.haviot),(SELECT ROUND((SUM(X.voitot)*1.0)/coalesce(NULLIF(SUM(X.haviot),0),1),2) AS DECIMAL) FROM Users S, Joukkueet X, Joukkueidenpelaajat Y WHERE S.id=Y.jasen_id AND X.id=Y.joukkue_id GROUP BY S.username ORDER BY SUM(X.voitot) DESC, SUM(X.haviot) ASC LIMIT 5"
    result = db.session.execute(sql)
    return result.fetchall()
def lowscore_for_players():
    sql = "SELECT S.username, SUM(X.voitot), SUM(X.haviot),(SELECT ROUND((SUM(X.voitot)*1.0)/coalesce(NULLIF(SUM(X.haviot),0),1),2) AS DECIMAL) FROM Users S, Joukkueet X, Joukkueidenpelaajat Y WHERE S.id=Y.jasen_id AND X.id=Y.joukkue_id GROUP BY S.username ORDER BY SUM(X.voitot) ASC, SUM(X.haviot) DESC LIMIT 5"
    result = db.session.execute(sql)
    return result.fetchall()


    