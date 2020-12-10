from db import db
import login
from flask import redirect, render_template, request, session, flash

def get_messages_by_match_id(id):
    sql = "SELECT K.viesti, U.username, K.aika, K.id FROM Kommentit K, users U, Ottelut O WHERE O.id=:id AND O.id=K.ottelu_id AND K.kayttaja_id=U.id ORDER BY K.aika DESC"
    result = db.session.execute(sql, {"id":id})
    return result.fetchall()

def send_message(otteluid, viesti):
    userid = login.user_id()
    if userid == 0 or len(viesti) < 1 or len(viesti) > 500:
        flash("Viestin lähetys epäonnistui")
        return False
    pieces = str.split(viesti)
    for piece in pieces:
        if len(piece) > 25:
            flash("Lyhennä sanoja, max pituus 25 merkkiä")
            return False
    sql = "INSERT INTO Kommentit (kayttaja_id, ottelu_id, viesti,aika) VALUES (:userid,:otteluid, :viesti, NOW())"
    db.session.execute(sql, {"userid":userid, "otteluid":otteluid, "viesti":viesti})
    db.session.commit()
    flash("Kommentti lisätty")
    del session["message"]
    return True
def delete_message(id):
    sql = "SELECT id FROM kommentit WHERE id=:id"
    result = db.session.execute(sql, {"id":id})
    comment = result.fetchone()
    if comment is  None:
        flash("Viestiä ei ole")
        return False
    else:
        sql = "DELETE FROM kommentit WHERE id=:id;"
        db.session.execute(sql, {"id":id})
        db.session.commit()
        flash("Viesti poistettu")
        return True