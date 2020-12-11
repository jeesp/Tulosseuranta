import os
from flask import session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from db import db


def check(username, password):
    #checking if the user is real
    sql = "SELECT password, id FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if user == None:
        flash("Käyttäjää ei löydy")
        return False
    if check_password_hash(user[0], password):
        session["user_id"] = user[1]
        session["username"] = username
        session["csrf_token"] = os.urandom(16).hex()
        del session["username_filled"]
        flash("Tervetuloa!")
        if is_admin(user[1]):
            session["admin"] = True
        return True
    flash("Väärä salis bro")
    return False

def user_id():
    #returning a user id
    return session.get("user_id", 0)

def is_admin(users_id):
    #checking if the user is admin
    sql = "SELECT admin FROM users WHERE id=:id"
    result = db.session.execute(sql, {"id":users_id})
    admin = result.fetchone()[0]
    return bool(admin == 1)


def new_user(username, password):
    #generating a new user if the username is not taken
    hash_value = generate_password_hash(password)
    sql = "SELECT username FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if user is not None:
        flash("Käyttäjänimi varattu")
        return False
    sql = "INSERT INTO users (username,password) VALUES (:username,:password)"
    db.session.execute(sql, {"username":username, "password":hash_value})
    db.session.commit()
    flash("Voit kirjautua nyt sisään uudella tunnuksellasi")
    return True
