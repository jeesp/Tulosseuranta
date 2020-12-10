from db import db
from flask import redirect, render_template, request, session, flash

def match_ratings(id):
    sql = "SELECT arvio FROM arviot WHERE ottelu_id=:id"
    result = db.session.execute(sql, {"id":id})
    ratings = result.fetchall()
    thumbs_up = 0
    thumbs_down = 0
    for rating in ratings:
        if rating[0] == 1:
            thumbs_up += 1
        if rating[0] == -1:
            thumbs_down += 1
    list = [thumbs_up, thumbs_down]
    return list

def add_rating(userid, otteluid, arvio):
    sql = "SELECT arvio FROM arviot A WHERE kayttaja_id=:userid AND ottelu_id=:otteluid"
    result = db.session.execute(sql, {"userid":userid, "otteluid":otteluid})
    previous_rating = result.fetchone()
    if previous_rating is None:
        sql = "INSERT INTO arviot (kayttaja_id, ottelu_id, arvio) VALUES (:userid, :otteluid, :arvio)"
        db.session.execute(sql, {"userid":userid, "otteluid":otteluid, "arvio":arvio})
        db.session.commit()
        return
    if previous_rating == arvio:
        return
    sql = "UPDATE arviot SET arvio =:arvio WHERE kayttaja_id=:userid AND ottelu_id=:otteluid"  
    db.session.execute(sql, {"arvio":arvio, "userid":userid, "otteluid":otteluid})
    db.session.commit()
    return