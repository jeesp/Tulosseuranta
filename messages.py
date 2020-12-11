from flask import session, flash
from db import db
import login


def get_messages_by_match_id(match_id):
    #fetching a list of messages by match id
    sql = "SELECT K.message, U.username, K.date, K.id \
        FROM Messages K, Users U, Matches O WHERE O.id=:id \
        AND O.id=K.match_id AND K.user_id=U.id \
        ORDER BY K.date DESC"
    result = db.session.execute(sql, {"id":match_id})
    return result.fetchall()

def send_message(match_id, message):
    #adding a message to a match by id
    userid = login.user_id()
    if userid == 0 or len(message) < 1 or len(message) > 500:
        flash("Viestin lähetys epäonnistui")
        return
    pieces = str.split(message)
    for piece in pieces:
        if len(piece) > 25:
            flash("Lyhennä sanoja, max pituus 25 merkkiä")
            return
    sql = "INSERT INTO Messages (user_id, match_id, message, date) \
        VALUES (:userid,:match_id, :message, NOW())"
    db.session.execute(sql, {"userid":userid, "match_id":match_id, "message":message})
    db.session.commit()
    flash("Kommentti lisätty")
    del session["message"]
    return

def delete_message(message_id):
    #deleting a message by message id
    sql = "SELECT id FROM Messages WHERE id=:id"
    result = db.session.execute(sql, {"id":message_id})
    comment = result.fetchone()
    if comment is  None:
        flash("Viestiä ei ole")
        return
    sql = "DELETE FROM Messages WHERE id=:id;"
    db.session.execute(sql, {"id":message_id})
    db.session.commit()
    flash("Viesti poistettu")
    return
