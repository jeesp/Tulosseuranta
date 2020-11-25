from db import db
import kirjautuminen
from flask import redirect, render_template, request, session, flash

def OttelunArviot(id):
    sql = "SELECT arvio FROM arviot WHERE ottelu_id=:id"
    result = db.session.execute(sql, {"id":id})
    arviot = result.fetchall()
    ylapeukut = 0
    alapeukut = 0
    flash(arviot)
    for arvio in arviot:
        flash(arvio)
        if arvio[0] == 1:
            ylapeukut += 1
        if arvio[0] == 0:
            alapeukut += 1
    list = [ylapeukut, alapeukut]
    return list

def LisaaArvio(userid, otteluid, arvio):
    sql = "SELECT arvio FROM arviot A WHERE kayttaja_id=:userid AND ottelu_id=:otteluid"
    result = db.session.execute(sql, {"userid":userid, "otteluid":otteluid})
    aikaisempiarvio = result.fetchone()
    if aikaisempiarvio is None:
        sql = "INSERT INTO arviot (kayttaja_id, ottelu_id, arvio) VALUES (:userid, :otteluid, :arvio)"
        db.session.execute(sql, {"userid":userid, "otteluid":otteluid, "arvio":arvio})
        db.session.commit()
        return
    if aikaisempiarvio == arvio:
        return
    sql = "UPDATE arviot SET arvio =:arvio WHERE kayttaja_id=:userid AND ottelu_id=:otteluid"  
    db.session.execute(sql, {"arvio":arvio, "userid":userid, "otteluid":otteluid})
    db.session.commit()
    return