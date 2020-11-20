from db import db
import kirjautuminen

def Viestit():
    sql = "SELECT K.viesti, U.username, K.aika FROM Kommentit K, users U WHERE K.kayttaja_id=U.id ORDER BY K.id DESC"
    result = db.session.execute(sql)
    return result.fetchall()

def OttelunViestit(id):
    sql = "SELECT K.viesti, U.username, K.aika FROM Kommentit K, users U, Ottelut O WHERE O.id=:id AND O.id=K.ottelu_id AND K.kayttaja_id=U.id ORDER BY K.aika DESC"
    result = db.session.execute(sql, {"id":id})
    return result.fetchall()

def LahetaViesti(otteluid, viesti):
    user_id = kirjautuminen.user_id()
    if user_id == 0:
        return False
    sql = "INSERT INTO Kommentit (kayttaja_id, ottelu_id, viesti,aika) VALUES (:user_id,:otteluid, :viesti, NOW())"
    db.session.execute(sql, {"user_id":user_id, "otteluid":otteluid, "viesti":viesti})
    db.session.commit()
    
    return True