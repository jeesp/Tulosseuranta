from db import db
import login
from flask import redirect, render_template, request, session, flash

def get_messages():
    sql = "SELECT K.viesti, U.username, K.aika FROM Kommentit K, users U WHERE K.kayttaja_id=U.id ORDER BY K.id DESC"
    result = db.session.execute(sql)
    return result.fetchall()

def get_messages_by_match_id(id):
    sql = "SELECT K.viesti, U.username, K.aika FROM Kommentit K, users U, Ottelut O WHERE O.id=:id AND O.id=K.ottelu_id AND K.kayttaja_id=U.id ORDER BY K.aika DESC"
    result = db.session.execute(sql, {"id":id})
    return result.fetchall()

def send_message(otteluid, viesti):
    userid = login.user_id()
    if userid == 0 or len(viesti) < 1 or len(viesti) > 500:
        flash("Viestin lähetys epäonnistui")
        return
    sql = "INSERT INTO Kommentit (kayttaja_id, ottelu_id, viesti,aika) VALUES (:userid,:otteluid, :viesti, NOW())"
    db.session.execute(sql, {"userid":userid, "otteluid":otteluid, "viesti":viesti})
    db.session.commit()
    flash("Kommentti lisätty")
    return