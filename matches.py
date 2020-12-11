
from flask import session, flash
from db import db
import messages

def match_played(home_team, away_team, home_points, away_points):
    #inserting new match to the database
    sql = "SELECT id FROM Teams WHERE name=:name"
    result = db.session.execute(sql, {"name":home_team})
    team1sql = result.fetchone()
    sql = "SELECT id FROM Teams WHERE name=:name"
    result = db.session.execute(sql, {"name":away_team})
    team2sql = result.fetchone()
    if team1sql is None:
        flash("Ensimmäistä joukkuetta ei löydy")
    if team2sql is None:
        flash("Toista joukkuetta ei löydy")
    if team1sql == team2sql:
        flash("Ei voi pelata itseään vastaan man")
    if team1sql is None or team2sql is None or team1sql == team2sql:
        return False

    user_id = session["user_id"]
    sql = "SELECT team_id FROM Players WHERE member_id=:user_id"
    result = db.session.execute(sql, {"user_id":user_id})
    user_team = result.fetchall()
    if user_team is None:
        flash("Käyttäjä ei kuulu mihinkään joukkueeseen")
        return False

    if team1sql not in user_team:
        flash("Syötä oman joukkueesi tulos man")
        return False

    team1 = team1sql[0]
    team2 = team2sql[0]
    if player_not_in_both_teams(team1, team2):
        sql = "INSERT INTO Matches (team1_id,team2_id, \
            home_points,away_points, date) VALUES \
            (:team1,:team2,:home_points,:away_points, NOW())"
        db.session.execute(sql, {"team1":team1, "team2":team2, \
            "home_points":home_points, "away_points":away_points})
        db.session.commit()
        del session["home_team"]
        del session["away_team"]
        del session["home_points"]
        del session["away_points"]
        if home_points > away_points:
            win_added = add_win(team1)
            loss_added = add_loss(team2)
            update_team_wins(win_added, team1)
            update_team_losses(loss_added, team2)
            flash("Hyvä matzi")
            return True

        if home_points < away_points:
            loss_added = add_loss(team1)
            win_added = add_win(team2)
            update_team_wins(win_added, team2)
            update_team_losses(loss_added, team1)
            flash("Hyvä matzi")
            return True
    flash("Käyttäjä pelaa kummassakin joukkueessa")
    return False

def update_team_wins(wins, team):
    #updating team wins to the database
    sql = "UPDATE Teams SET wins=:wins WHERE id=:team"
    db.session.execute(sql, {"wins":wins, "team":team})
    db.session.commit()

def update_team_losses(losses, team):
    #updating team losses to the database
    sql = "UPDATE Teams SET losses=:losses WHERE id=:team"
    db.session.execute(sql, {"losses":losses, "team":team})
    db.session.commit()

def matches_latest_first():
    #fetching all matches sorted by date
    sql = "SELECT match_id FROM Matches ORDER BY date DESC"
    result = db.session.execute(sql)
    match_ids = result.fetchall()
    matches = []
    for match in match_ids:
        matches.append(get_match(match[0]))
    return matches

def matches_favorite_first():
    #fetching all matches sorted by rating
    sql = "SELECT match_id FROM Ratings GROUP BY match_id \
        ORDER BY SUM(rating) DESC, (SELECT COUNT(*) FROM Ratings \
        WHERE rating=1) DESC, (SELECT COUNT(*) FROM Ratings WHERE rating=-1) ASC"
    result = db.session.execute(sql)
    match_ids = result.fetchall()
    sql = "SELECT id FROM Matches WHERE id NOT IN (SELECT match_id \
        FROM Ratings) ORDER BY date"
    result = db.session.execute(sql)
    rating_not_found = result.fetchall()
    match_ids.extend(rating_not_found)
    matches = []
    for match in match_ids:
        matches.append(get_match(match[0]))
    return matches

def three_best_matches():
    #fetching three best matches sorted by rating
    sql = "SELECT match_id FROM Ratings GROUP BY match_id \
        ORDER BY SUM(rating) DESC, (SELECT COUNT(*) \
        FROM Ratings WHERE rating=1) DESC, (SELECT COUNT(*) \
        FROM Ratings WHERE rating=-1) ASC LIMIT 3"
    result = db.session.execute(sql)
    match_ids = result.fetchall()
    if len(match_ids) < 3:
        sql = "SELECT id FROM Matches LIMIT 3"
        result = db.session.execute(sql)
        missing = result.fetchall()
        for match in missing:
            if match not in match_ids:
                match_ids.append(match)
    matches = []
    for match in match_ids:
        matches.append(get_match(match[0]))
    for match in matches:
        index = matches.index(match)
        if index > 2:
            matches.remove(match)
    return matches

def get_match(match_id):
    #fetching data for a single match
    sql = "SELECT J.name, T.name, O.home_points, O.away_points, \
        O.date, O.id, (SELECT COUNT(*) FROM Ratings A WHERE \
        A.rating=1 AND A.match_id=:id), (SELECT COUNT(*) FROM \
        ratings A WHERE A.rating=-1 AND A.match_id=:id) FROM \
        Teams J, Teams T,Matches O WHERE O.id=:id AND \
        O.team1_id=J.id AND O.team2_id=T.id"
    result = db.session.execute(sql, {"id":match_id})
    return result.fetchone()

def refresh_match_page(match_id):
    #fetching latest lists of messages and match data
    match = get_match(match_id)
    message_list = messages.get_messages_by_match_id(match_id)
    return match, message_list

def is_match(match_id):
    #checking if a match exists
    sql = "SELECT * FROM Matches WHERE id=:match_id"
    result = db.session.execute(sql, {"match_id":match_id})
    match_sql = result.fetchone()
    return bool(match_sql is not None)

def match_modify(match_id, home_points, away_points):
    #modifying match points and teams wins and losses by match id and team ids
    if is_match(match_id) is False:
        flash("ottelua ei löytynyt")
        return

    sql = "SELECT team1_id, team2_id, home_points, away_points \
        FROM Matches WHERE id=:match_id"
    result = db.session.execute(sql, {"match_id":match_id})
    teams_sql = result.fetchone()
    if home_points > away_points:
        if teams_sql[2] > teams_sql[3]:
            sql = "UPDATE Matches SET home_points=:home_points, \
                away_points=:away_points WHERE id=:match_id"
            db.session.execute(sql, {"home_points":home_points, \
                "away_points":away_points, "match_id":match_id})
            db.session.commit()
            flash("Muutos suoritettu")
            return
        win_removed = remove_win(teams_sql[1])
        loss_added = add_loss(teams_sql[1])
        win_added = add_win(teams_sql[0])
        loss_removed = remove_loss(teams_sql[0])
        update_team_wins_and_losses(win_removed, loss_added, teams_sql[1])
        update_team_wins_and_losses(win_added, loss_removed, teams_sql[0])
        sql = "UPDATE Matches SET home_points=:home_points, \
            away_points=:away_points WHERE id=:match_id"
        db.session.execute(sql, {"home_points":home_points, \
            "away_points":away_points, "match_id":match_id})
        db.session.commit()
        flash("Muutos suoritettu")
        return

    if away_points > home_points:
        if teams_sql[3] > teams_sql[2]:
            sql = "UPDATE Matches SET home_points=:home_points, \
                away_points=:away_points WHERE id=:match_id"
            db.session.execute(sql, {"home_points":home_points, \
                "away_points":away_points, "match_id":match_id})
            db.session.commit()
            flash("Muutos suoritettu")
            return

        win_removed = remove_win(teams_sql[0])
        loss_added = add_loss(teams_sql[0])
        win_added = add_win(teams_sql[1])
        loss_removed = remove_loss(teams_sql[1])
        update_team_wins_and_losses(win_removed, loss_added, teams_sql[0])
        update_team_wins_and_losses(win_added, loss_removed, teams_sql[1])

        sql = "UPDATE Matches SET home_points=:home_points, \
            away_points=:away_points WHERE id=:match_id"
        db.session.execute(sql, {"home_points":home_points, \
            "away_points":away_points, "match_id":match_id})
        db.session.commit()
        flash("Muutos suoritettu")
        return

def update_team_wins_and_losses(wins, losses, team):
    #update both wins and losses
    sql = "UPDATE Teams SET wins=:wins, losses=:losses WHERE id=:team"
    db.session.execute(sql, {"wins":wins, "losses":losses, "team":team})
    db.session.commit()

def remove_win(team):
    #removes win by team id
    sql = "SELECT wins FROM Teams WHERE id=:team_id"
    result = db.session.execute(sql, {"team_id":team})
    win_list = result.fetchone()[0] - 1
    if win_list < 0:
        win_list = 0
    return win_list

def remove_loss(team):
    #removes loss by team id
    sql = "SELECT losses FROM Teams WHERE id=:team_id"
    result = db.session.execute(sql, {"team_id":team})
    loss_list = result.fetchone()[0] - 1
    if loss_list < 0:
        loss_list = 0
    return loss_list
def add_win(team):
    #adds win by team id
    sql = "SELECT wins FROM Teams WHERE id=:team_id"
    result = db.session.execute(sql, {"team_id":team})
    win_list = result.fetchone()[0] +1
    return win_list
def add_loss(team):
    #adds loss by team id
    sql = "SELECT losses FROM Teams WHERE id=:team_id"
    result = db.session.execute(sql, {"team_id":team})
    loss_list = result.fetchone()[0] +1
    return loss_list

def delete_match(match_id):
    #deleting the match result from the teams that played
    if is_match(match_id) is False:
        flash("ottelua ei löytynyt")
        return
    sql = "SELECT team1_id, team2_id, home_points, \
        away_points FROM Matches WHERE id=:match_id"
    result = db.session.execute(sql, {"match_id":match_id})
    teams_sql = result.fetchone()
    if teams_sql[2] > teams_sql[3]:
        win_removed = remove_win(teams_sql[0])
        loss_removed = remove_loss(teams_sql[1])
        update_team_wins(win_removed, teams_sql[0])
        update_team_losses(loss_removed, teams_sql[1])
        delete(match_id)
        flash("Ottelu poistettu")
        return

    if teams_sql[3] > teams_sql[2]:
        win_removed = remove_win(teams_sql[1])
        loss_removed = remove_loss(teams_sql[0])
        update_team_wins(win_removed, teams_sql[1])
        update_team_losses(loss_removed, teams_sql[0])
        delete(match_id)
        flash("Ottelu poistettu")
        return

def delete(match_id):
    #deletes the match from the database
    sql = "DELETE FROM Matches WHERE id=:match_id"
    db.session.execute(sql, {"match_id":match_id})
    db.session.commit()

def player_not_in_both_teams(team1, team2):
    #checking if player is playing in both teams
    sql = "SELECT J.team_id FROM Players J, \
        Players K WHERE J.member_id=K.member_id \
        AND J.team_id=:team1 AND K.team_id=:team2"
    result = db.session.execute(sql, {"team1":team1, "team2":team2})
    player_in_both = result.fetchone()
    return bool(player_in_both is None)
