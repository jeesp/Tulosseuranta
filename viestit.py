from db import db
import kirjautuminen
from flask import redirect, render_template, request, session, flash

def Viestit():
    sql = "SELECT K.viesti, U.username, K.aika FROM Kommentit K, users U WHERE K.kayttaja_id=U.id ORDER BY K.id DESC"
    result = db.session.execute(sql)
    return result.fetchall()

def OttelunViestit(id):
    sql = "SELECT K.viesti, U.username, K.aika FROM Kommentit K, users U, Ottelut O WHERE O.id=:id AND O.id=K.ottelu_id AND K.kayttaja_id=U.id ORDER BY K.aika DESC"
    result = db.session.execute(sql, {"id":id})
    return result.fetchall()

def LahetaViesti(otteluid, viesti):
    userid = kirjautuminen.user_id()
    if userid == 0:
        flash("Viestin lähetys epäonnistui")
        return
    sql = "INSERT INTO Kommentit (kayttaja_id, ottelu_id, viesti,aika) VALUES (:userid,:otteluid, :viesti, NOW())"
    db.session.execute(sql, {"userid":userid, "otteluid":otteluid, "viesti":viesti})
    db.session.commit()
    flash("Kommentti lisätty")
    return