
from flask import session, flash
from db import db
import messages

def match_played(joukkue1,joukkue2,points1,points2):
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
    user_team = result.fetchall() 
    if user_team is None:
        flash("Käyttäjä ei kuulu mihinkään joukkueeseen")
        return False
    if team1sql not in user_team:
        flash("Syötä oman joukkueesi tulos man")
        return False
    team1 = team1sql[0]
    team2 = team2sql[0]
    if check_teams(team1,team2):
        sql = "INSERT INTO ottelut (joukkue1_id,joukkue2_id,pisteet_koti,pisteet_vieras, ajankohta) VALUES (:joukkue1,:joukkue2,:pisteet1,:pisteet2, NOW())"
        db.session.execute(sql, {"joukkue1":team1,"joukkue2":team2,"pisteet1":points1,"pisteet2":points2})
        db.session.commit()
        del session["team1"]
        del session["team2"]
        del session["team1points"]
        del session["team2points"]
        if points1 > points2:
            sql = "SELECT voitot FROM joukkueet WHERE id=:team1"
            result = db.session.execute(sql, {"team1":team1})
            wins = result.fetchone()
            win_added = wins[0] + 1

            sql = "SELECT haviot FROM joukkueet WHERE id=:team2"
            result = db.session.execute(sql, {"team2":team2})
            losses = result.fetchone()
            loss_added = losses[0] + 1

            sql = "UPDATE joukkueet SET voitot=:lisattyvoitto WHERE id=:team1"
            db.session.execute(sql, {"lisattyvoitto":win_added,"team1":team1})
            db.session.commit()

            sql = "UPDATE joukkueet SET haviot=:lisattyhavio WHERE id=:team2"
            db.session.execute(sql, {"lisattyhavio":loss_added,"team2":team2})
            db.session.commit()
            flash ("Hyvä matzi")
            return True

        if points1 < points2:
            sql = "SELECT voitot FROM joukkueet WHERE id=:team2"
            result = db.session.execute(sql, {"team2":team2})
            wins = result.fetchone()
            win_added = wins[0] + 1

            sql = "SELECT haviot FROM joukkueet WHERE id=:team1"
            result = db.session.execute(sql, {"team1":team1})
            losses = result.fetchone()
            loss_added = losses[0] + 1

            sql = "UPDATE joukkueet SET voitot=:lisattyvoitto WHERE id=:team2"
            db.session.execute(sql, {"lisattyvoitto":win_added,"team2":team2})
            db.session.commit()

            sql = "UPDATE joukkueet SET haviot=:lisattyhavio WHERE id=:team1"
            db.session.execute(sql, {"lisattyhavio":loss_added,"team1":team1})
            db.session.commit()
            flash ("Hyvä matzi")
            return True
    else:
        flash("Käyttäjä pelaa kummassakin joukkueessa")
        return False
def matches_latest_first():
    sql = "SELECT ottelu_id FROM ottelut ORDER BY O.ajankohta DESC"
    result = db.session.execute(sql)
    match_ids = result.fetchall()
    matches=[]
    for match in match_ids:
        matches.append(get_match(match[0]))
    return matches

def matches_favorite_first():
    sql = "SELECT ottelu_id FROM arviot GROUP BY ottelu_id ORDER BY SUM(arvio) DESC, (SELECT COUNT(*) FROM arviot WHERE arvio=1) DESC, (SELECT COUNT(*) FROM arviot WHERE arvio=-1) ASC"
    result = db.session.execute(sql)
    match_ids = result.fetchall()
    sql = "SELECT id FROM Ottelut WHERE id NOT IN (SELECT ottelu_id FROM arviot) ORDER BY ajankohta"
    result = db.session.execute(sql)
    rating_not_found = result.fetchall()
    match_ids.extend(rating_not_found)
    matches=[]
    for match in match_ids:
        matches.append(get_match(match[0]))
    return matches

def three_best_matches():
    sql = "SELECT ottelu_id FROM arviot GROUP BY ottelu_id ORDER BY SUM(arvio) DESC, (SELECT COUNT(*) FROM arviot WHERE arvio=1) DESC, (SELECT COUNT(*) FROM arviot WHERE arvio=-1) ASC LIMIT 3"
    result = db.session.execute(sql)
    match_ids = result.fetchall()
    if len(match_ids) < 3:
        sql = "SELECT id FROM ottelut LIMIT 3"
        result = db.session.execute(sql)
        missing = result.fetchall()
        for match in missing:
            if match not in match_ids:
                match_ids.append(match)
    matches=[]
    for match in match_ids:
        matches.append(get_match(match[0]))
    for match in matches:
        index = matches.index(match)
        if index > 2:
            matches.remove(match) 
    return matches
def get_match(id):
    sql = "SELECT J.nimi, T.nimi, O.pisteet_koti, O.pisteet_vieras, O.ajankohta, O.id, (SELECT COUNT(*) FROM Arviot A WHERE A.arvio=1 AND A.ottelu_id=:id), (SELECT COUNT(*) FROM Arviot A WHERE A.arvio=-1 AND A.ottelu_id=:id) FROM Joukkueet J, Joukkueet T,Ottelut O WHERE O.id=:id AND O.joukkue1_id=J.id AND O.joukkue2_id=T.id"
    result = db.session.execute(sql, {"id":id})
    return result.fetchone()
def refresh_match_page(otteluid):
    match = get_match(otteluid)
    message_list = messages.get_messages_by_match_id(otteluid)
    return match, message_list
def is_match(otteluid):
    sql = "SELECT * FROM ottelut WHERE id=:otteluid"
    result = db.session.execute(sql, {"otteluid":otteluid})
    ottelusql = result.fetchone()
    if ottelusql is None:
        return False
    return True

def match_modify(otteluid,pisteet1,pisteet2):
    
    if is_match(otteluid) is False:
        flash("ottelua ei löytynyt")
        return False

    sql = "SELECT joukkue1_id, joukkue2_id, pisteet_koti, pisteet_vieras FROM ottelut WHERE id=:otteluid"
    result = db.session.execute(sql, {"otteluid":otteluid})
    teams_sql = result.fetchone()

    if teams_sql[2] > teams_sql[3]:
        sql = "SELECT voitot FROM joukkueet WHERE id=:joukkue1id"
        result = db.session.execute(sql, {"joukkue1id":teams_sql[0]})
        wins = result.fetchone()
        win_removed = wins[0] - 1

        sql = "SELECT haviot FROM joukkueet WHERE id=:joukkue1id"
        result = db.session.execute(sql, {"joukkue1id":teams_sql[0]})
        losses = result.fetchone()
        loss_added = losses[0] + 1

        sql = "SELECT voitot FROM joukkueet WHERE id=:joukkue2id"
        result = db.session.execute(sql, {"joukkue2id":teams_sql[1]})
        wins = result.fetchone()
        win_added = wins[0] + 1

        sql = "SELECT haviot FROM joukkueet WHERE id=:joukkue2id"
        result = db.session.execute(sql, {"joukkue2id":teams_sql[1]})
        losses = result.fetchone()
        loss_removed = losses[0] - 1

        sql = "UPDATE joukkueet SET voitot=:vahennettyvoitto1, haviot=:lisattyhavio1 WHERE id=:joukkue1id"
        db.session.execute(sql, {"vahennettyvoitto1":win_removed, "lisattyhavio1":loss_added, "joukkue1id":teams_sql[0]})
        db.session.commit()

        sql = "UPDATE joukkueet SET voitot=:lisattyvoitto2, haviot=:vahennettyhavio2 WHERE id=:joukkue2id"
        db.session.execute(sql, {"lisattyvoitto2":win_added, "vahennettyhavio2":loss_removed, "joukkue2id":teams_sql[1]})
        db.session.commit()

        sql = "UPDATE ottelut SET pisteet_koti=:pisteet1, pisteet_vieras=:pisteet2 WHERE id=:otteluid"
        db.session.execute(sql, {"pisteet1":pisteet1,"pisteet2":pisteet2,"otteluid":otteluid})
        db.session.commit()
        flash ("Muutos suoritettu")
        return True
    if teams_sql[3] > teams_sql[2]:
        sql = "SELECT voitot FROM joukkueet WHERE id=:joukkue1id"
        result = db.session.execute(sql, {"joukkue1id":teams_sql[1]})
        wins = result.fetchone()
        win_removed = wins[0] - 1

        sql = "SELECT haviot FROM joukkueet WHERE id=:joukkue1id"
        result = db.session.execute(sql, {"joukkue1id":teams_sql[1]})
        losses = result.fetchone()
        loss_added = losses[0] + 1

        sql = "SELECT voitot FROM joukkueet WHERE id=:joukkue2id"
        result = db.session.execute(sql, {"joukkue2id":teams_sql[0]})
        wins = result.fetchone()
        win_added = wins[0] + 1

        sql = "SELECT haviot FROM joukkueet WHERE id=:joukkue2id"
        result = db.session.execute(sql, {"joukkue2id":teams_sql[0]})
        losses = result.fetchone()
        loss_removed = losses[0] - 1

        sql = "UPDATE joukkueet SET voitot=:vahennettyvoitto1, haviot=:lisattyhavio1 WHERE id=:joukkue1id"
        db.session.execute(sql, {"vahennettyvoitto1":win_removed, "lisattyhavio1":loss_added, "joukkue1id":teams_sql[1]})
        db.session.commit()

        sql = "UPDATE joukkueet SET voitot=:lisattyvoitto2, haviot=:vahennettyhavio2 WHERE id=:joukkue2id"
        db.session.execute(sql, {"lisattyvoitto2":win_added, "vahennettyhavio2":loss_removed, "joukkue2id":teams_sql[0]})
        db.session.commit()

        sql = "UPDATE ottelut SET pisteet_koti:pisteet1, pisteet_vieras:pisteet2 WHERE id=:otteluid"
        db.session.execute(sql, {"pisteet1":pisteet1,"pisteet2":pisteet2,"otteluid":otteluid})
        db.session.commit()
        flash ("Muutos suoritettu")
        return True

def delete_match(otteluid):

    if is_match(otteluid) is False:
        flash("ottelua ei löytynyt")
        return False
    sql = "SELECT joukkue1_id, joukkue2_id, pisteet_koti, pisteet_vieras FROM ottelut WHERE id=:otteluid"
    result = db.session.execute(sql, {"otteluid":otteluid})
    teams_sql = result.fetchone()

    if teams_sql[2] > teams_sql[3]:
        sql = "SELECT voitot FROM joukkueet WHERE id=:joukkue1id"
        result = db.session.execute(sql, {"joukkue1id":teams_sql[0]})
        wins = result.fetchone()
        win_removed = wins[0] - 1
        sql = "SELECT haviot FROM joukkueet WHERE id=:joukkue2id"
        result = db.session.execute(sql, {"joukkue2id":teams_sql[1]})
        losses = result.fetchone()
        loss_removed = losses[0] - 1
        sql = "UPDATE joukkueet SET voitot=:vahennettyvoitto1 WHERE id=:joukkue1id"
        db.session.execute(sql, {"vahennettyvoitto1":win_removed,  "joukkue1id":teams_sql[0]})
        db.session.commit()
        sql = "UPDATE joukkueet SET haviot=:vahennettyhavio2 WHERE id=:joukkue2id"
        db.session.execute(sql, {"vahennettyhavio2":loss_removed, "joukkue2id":teams_sql[1]})
        db.session.commit()
        sql = "DELETE FROM ottelut WHERE id=:otteluid"
        db.session.execute(sql, {"otteluid":otteluid})
        db.session.commit()
        flash("Ottelu poistettu")
        return True
    if teams_sql[3] > teams_sql[2]:
        sql = "SELECT voitot FROM joukkueet WHERE id=:joukkue1id"
        result = db.session.execute(sql, {"joukkue1id":teams_sql[1]})
        wins = result.fetchone()
        win_removed = wins[0] - 1
        sql = "SELECT haviot FROM joukkueet WHERE id=:joukkue2id"
        result = db.session.execute(sql, {"joukkue2id":teams_sql[0]})
        losses = result.fetchone()
        loss_removed = losses[0] - 1
        sql = "UPDATE joukkueet SET voitot=:vahennettyvoitto1 WHERE id=:joukkue1id"
        db.session.execute(sql, {"vahennettyvoitto1":win_removed,  "joukkue1id":teams_sql[1]})
        db.session.commit()
        sql = "UPDATE joukkueet SET haviot=:vahennettyhavio2 WHERE id=:joukkue2id"
        db.session.execute(sql, {"vahennettyhavio2":loss_removed, "joukkue2id":teams_sql[0]})
        db.session.commit()
        sql = "DELETE FROM ottelut WHERE id=:otteluid"
        db.session.execute(sql, {"otteluid":otteluid})
        db.session.commit()
        flash("Ottelu poistettu")
        return True

def check_teams(team1,team2):
    sql = "SELECT J.joukkue_id FROM joukkueidenpelaajat J, joukkueidenpelaajat K WHERE J.jasen_id=K.jasen_id AND J.joukkue_id=:team1 AND K.joukkue_id=:team2"
    result = db.session.execute(sql, {"team1":team1, "team2":team2})
    check = result.fetchone()
    return bool(check)




