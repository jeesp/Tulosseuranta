from flask import Flask
from flask import redirect, render_template, request, session, flash
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from db import db
from app import app
import viestit, arviot

def ottelupelattu(joukkue1,joukkue2,pisteet1,pisteet2):
    sql = "SELECT id FROM joukkueet WHERE nimi=:nimi"
    result = db.session.execute(sql, {"nimi":joukkue1})
    team1sql = result.fetchone()
    sql = "SELECT id FROM joukkueet WHERE nimi=:nimi"
    result = db.session.execute(sql, {"nimi":joukkue2})
    team2sql = result.fetchone()
    if team1sql is None:
        flash("Ensimmäistä joukkuetta ei löydy")
    if team2sql is None:
        flash("Toista joukkuetta ei löydy")
    if team1sql == team2sql:
        flash("Ei voi pelata itseään vastaan man")
    if team1sql is None or team2sql is None or team1sql == team2sql:
        return False
    userid = session["user_id"]

    sql = "SELECT joukkue_id FROM joukkueidenpelaajat WHERE jasen_id=:userid"
    result = db.session.execute(sql, {"userid":userid})
    kayttajanjoukkue = result.fetchall() 
    if kayttajanjoukkue is None:
        flash("Käyttäjä ei kuulu mihinkään joukkueeseen")
        return False
    if team1sql not in kayttajanjoukkue:
        flash("Syötä oman joukkueesi tulos man")
        return False
    team1 = team1sql[0]
    team2 = team2sql[0]

    sql = "INSERT INTO ottelut (joukkue1_id,joukkue2_id,pisteet_koti,pisteet_vieras, ajankohta) VALUES (:joukkue1,:joukkue2,:pisteet1,:pisteet2, NOW())"
    db.session.execute(sql, {"joukkue1":team1,"joukkue2":team2,"pisteet1":pisteet1,"pisteet2":pisteet2})
    db.session.commit()
    del session["team1"]
    del session["team2"]
    del session["team1points"]
    del session["team2points"]
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
        return True

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
        return True
def OttelutViimeisinEnsin():
    sql = "SELECT ottelu_id FROM ottelut ORDER BY O.ajankohta DESC"
    result = db.session.execute(sql)
    otteluidt = result.fetchall()
    ottelut=[]
    for ottelu in otteluidt:
        ottelut.append(haeOttelu(ottelu[0]))
    return ottelut

def OttelutSuosituinEnsin():
    sql = "SELECT ottelu_id FROM arviot GROUP BY ottelu_id ORDER BY SUM(arvio) DESC, (SELECT COUNT(*) FROM arviot WHERE arvio=1) DESC, (SELECT COUNT(*) FROM arviot WHERE arvio=-1) ASC"
    result = db.session.execute(sql)
    otteluidt = result.fetchall()
    sql = "SELECT id FROM Ottelut WHERE id NOT IN (SELECT ottelu_id FROM arviot) ORDER BY ajankohta"
    result = db.session.execute(sql)
    arvioimattomat = result.fetchall()
    otteluidt.extend(arvioimattomat)
    ottelut=[]
    for ottelu in otteluidt:
        ottelut.append(haeOttelu(ottelu[0]))
    return ottelut

def kolmeparastaottelua():
    sql = "SELECT ottelu_id FROM arviot GROUP BY ottelu_id ORDER BY SUM(arvio) DESC, (SELECT COUNT(*) FROM arviot WHERE arvio=1) DESC, (SELECT COUNT(*) FROM arviot WHERE arvio=-1) ASC LIMIT 3"
    result = db.session.execute(sql)
    otteluidt = result.fetchall()
    ottelut=[]
    for ottelu in otteluidt:
        ottelut.append(haeOttelu(ottelu[0]))
    return ottelut
def haeOttelu(id):
    sql = "SELECT J.nimi, T.nimi, O.pisteet_koti, O.pisteet_vieras, O.ajankohta, O.id, (SELECT COUNT(*) FROM Arviot A WHERE A.arvio=1 AND A.ottelu_id=:id), (SELECT COUNT(*) FROM Arviot A WHERE A.arvio=-1 AND A.ottelu_id=:id) FROM Joukkueet J, Joukkueet T,Ottelut O WHERE O.id=:id AND O.joukkue1_id=J.id AND O.joukkue2_id=T.id"
    result = db.session.execute(sql, {"id":id})
    return result.fetchone()
def paivitaOttelusivu(otteluid):
    ottelu = haeOttelu(otteluid)
    viestilista = viestit.OttelunViestit(otteluid)
    return ottelu, viestilista

