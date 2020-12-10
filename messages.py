from flask import session, flash
from db import db
import login


def get_messages_by_match_id(match_id):
    #fetching a list of messages by match id
    sql = "SELECT K.viesti, U.username, K.aika, K.id \
        FROM Kommentit K, users U, Ottelut O WHERE O.id=:id \
        AND O.id=K.ottelu_id AND K.kayttaja_id=U.id \
        ORDER BY K.aika DESC"
    result = db.session.execute(sql, {"id":match_id})
    return result.fetchall()

def send_message(otteluid, viesti):
    #adding a message to a match by id
    userid = login.user_id()
    if userid == 0 or len(viesti) < 1 or len(viesti) > 500:
        flash("Viestin lähetys epäonnistui")
        return
    pieces = str.split(viesti)
    for piece in pieces:
        if len(piece) > 25:
            flash("Lyhennä sanoja, max pituus 25 merkkiä")
            return
    sql = "INSERT INTO Kommentit (kayttaja_id, ottelu_id, viesti,aika) \
        VALUES (:userid,:otteluid, :viesti, NOW())"
    db.session.execute(sql, {"userid":userid, "otteluid":otteluid, "viesti":viesti})
    db.session.commit()
    flash("Kommentti lisätty")
    del session["message"]
    return

def delete_message(message_id):
    #deleting a message by message id
    sql = "SELECT id FROM kommentit WHERE id=:id"
    result = db.session.execute(sql, {"id":message_id})
    comment = result.fetchone()
    if comment is  None:
        flash("Viestiä ei ole")
        return
    sql = "DELETE FROM kommentit WHERE id=:id;"
    db.session.execute(sql, {"id":message_id})
    db.session.commit()
    flash("Viesti poistettu")
    return
