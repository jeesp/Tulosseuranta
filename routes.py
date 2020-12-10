from flask import redirect, render_template, request, session, flash
from app import app
import login
import teams
import matches
import highscore
import messages
import ratings


@app.route("/")
def index():
    list = matches.three_best_matches()
    return render_template("index.html", matches=list)

@app.route("/all_matches")
def all_matches():
    list = matches.matches_favorite_first()
    return render_template("allmatches.html", matches=list)

@app.route("/sign_in", methods=["GET", "POST"])
def sign_in():
    if request.method == "GET":
        return render_template("newuser.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if len(username) < 1 or len(password) < 1:
            flash("Tyhjä kenttä")
            return render_template("newuser.html")
        if len(password) < 4:
            flash("Salasana liian lyhyt, pitää olla vähintään 4 merkkiä.")
            return render_template("newuser.html")
        if len(username) > 30:
            flash("Käyttäjänimi liian pitkä, alle 30 sallittu")
            return render_template("newuser.html")
        if login.new_user(username, password):
            return render_template("login.html")
        return render_template("newuser.html")

@app.route("/newuser", methods=["GET", "POST"])
def newuser():
    return render_template("newuser.html")

@app.route("/match/<int:match_id>", methods=["GET", "POST"])
def match(match_id):
    if request.method == "GET":
        return redirect("/")
    if request.method == "POST":
        list = matches.refresh_match_page(match_id)
        return render_template("matchpage.html", match=list[0], messages=list[1])

@app.route("/match/<int:match_id>/add_comment", methods=["GET", "POST"])
def add_comment(match_id):
    if request.method == "GET":
        return redirect("/")
    if request.method == "POST":
        message = request.form["message"]
        session["message"] = message
        if len(message) < 1:
            flash("Tyhjä kenttä")
        if len(message) > 500:
            flash("Liian pitkä viesti")
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        messages.send_message(match_id, message)
        list = matches.refresh_match_page(match_id)
        return render_template("matchpage.html", match=list[0], messages=list[1])

@app.route("/match/<int:otteluid>/add_rating", methods=["GET", "POST"])
def add_rating(match_id):
    if request.method == "GET":
        return redirect("/")
    if request.method == "POST":
        rating = request.form["rating"]
        ratings.add_rating(login.user_id(), match_id, rating)
        list = matches.refresh_match_page(match_id)
        return render_template("matchpage.html", match=list[0], messages=list[1])

@app.route("/newteam", methods=["GET", "POST"])
def new_team():
    if login.user_id == 0:
        redirect("/")
    return render_template("newteam.html")

@app.route("/adminpage", methods=["GET", "POST"])
def modify_team():
    if login.user_id == 0:
        return redirect("/")
    if login.is_admin(login.user_id()):
        return render_template("adminpage.html")
    flash("Ei admin-oikeutta")
    return redirect("/")

@app.route("/modifyteamusers", methods=["GET", "POST"])
def modify_team_users():
    if request.method == "GET":
        return redirect("/")
    if login.user_id == 0:
        return redirect("/")
    if login.is_admin(login.user_id()):
        team = request.form["team"]
        username1 = request.form["username1"]
        username2 = request.form["username2"]
        teams.modify_players(username1, username2, team)
        return render_template("adminpage.html")
    flash("Ei admin-oikeutta")
    return redirect("/")

@app.route("/deleteteam", methods=["GET", "POST"])
def delete_team():
    if login.user_id == 0:
        return redirect("/")
    if login.is_admin(login.user_id()):
        team = request.form["team"]
        teams.delete_team(team)
        return render_template("adminpage.html")
    flash("Ei admin-oikeutta")
    return redirect("/")

@app.route("/deletemessage", methods=["GET", "POST"])
def delete_message():
    if login.user_id == 0:
        return redirect("/")
    if login.is_admin(login.user_id()):
        id = request.form["message_id"]
        messages.delete_message(id)
        return render_template("adminpage.html")
    flash("Ei admin-oikeutta")
    return redirect("/")

@app.route("/deletematch", methods=["GET", "POST"])
def delete_match():
    if request.method == "GET":
        return redirect("/")
    if login.user_id == 0:
        return redirect("/")
    if login.is_admin(login.user_id()):
        match_id = request.form["otteluid"]
        matches.delete_match(match_id)
        return render_template("adminpage.html")
    flash("Ei admin-oikeutta")
    return redirect("/")

@app.route("/modifymatch", methods=["GET", "POST"])
def modify_match():
    if request.method == "GET":
        return redirect("/")
    if login.user_id == 0:
        return redirect("/")
    if login.is_admin(login.user_id()):
        match_id = request.form["match_id"]
        home_points = request.form["home_points"]
        away_points = request.form["away_points"]
        matches.match_modify(match_id, home_points, away_points)
        return render_template("adminpage.html")
    flash("Ei admin-oikeutta")
    return redirect("/")

@app.route("/newmatch", methods=["GET", "POST"])
def new_match():
    return render_template("newmatch.html")

@app.route("/creatematch", methods=["GET", "POST"])
def create_match():
    if request.method == "GET":
        return redirect("/")
    if request.method == "POST":
        team1 = request.form["home_team"]
        session["home_team"] = team1
        team2 = request.form["away_team"]
        session["away_team"] = team2
        points1 = request.form["home_points"]
        session["home_points"] = points1
        points2 = request.form["away_points"]
        session["away_points"] = points2
        if len(team1) < 1 or len(team2) < 1  or len(points1) < 1  or len(points2) < 1:
            flash("Jokin kenttä oli tyhjä.")
            return render_template("newmatch.html")
        if int(points1) < 0 or int(points1) > 10 or int(points2) < 0 or int(points2) > 10:
            flash("Nyt vaikuttaa huijaukselta.. Pisteitä liikaa tai liian vähän")
            return render_template("newmatch.html")
        if int(points1) == int(points2):
            flash("Hmm... tasapeli? Ratkaistaan sudden deathilla")
            return render_template("newmatch.html")
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        if matches.match_played(team1, team2, points1, points2):
            return redirect("/")

        return render_template("newmatch.html")

@app.route("/createteam", methods=["GET", "POST"])
def create_team():
    if request.method == "GET":
        return render_template("index.html")
    if request.method == "POST":
        username1 = request.form["username1"]
        session["username1"] = username1
        username2 = request.form["username2"]
        session["username2"] = username2
        team = request.form["team"]
        session["team"] = team
        if len(username1) < 1 or len(username2) < 1 or len(team) < 1:
            flash("Kenttä tyhjä")
            return render_template("newteam.html")
        if len(team) > 20:
            flash("Liian pitkä nimi joukkueella")
            return render_template("newteam.html")
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        if teams.create_team(username1, username2, team):
            return redirect("/")
        return render_template("newteam.html")

@app.route("/highscoreteam", methods=["GET", "POST"])
def highscore_for_teams():
    list = highscore.highscore_for_teams()
    return render_template("highscoreteam.html", teams=list)

@app.route("/lowscoreteam", methods=["GET", "POST"])
def lowscore_for_teams():
    list = highscore.lowscore_for_teams()
    return render_template("lowscoreteam.html", teams=list)

@app.route("/highscoreplayer", methods=["GET", "POST"])
def highscore_for_players():
    list = highscore.highscore_for_players()
    return render_template("highscoreplayer.html", players=list)

@app.route("/lowscoreplayer", methods=["GET", "POST"])
def lowscore_for_players():
    list = highscore.lowscore_for_players()
    return render_template("lowscoreplayer.html", players=list)

@app.route("/login", methods=["GET", "POST"])
def log_in():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if len(username) < 1 or len(password) < 1:
            flash("Tyhjä kenttä")
            return render_template("login.html")
        if login.check(username, password):
            return redirect("/")
        return render_template("login.html")

@app.route("/logout")
def log_out():
    flash("Hate to see you leave")
    if login.is_admin(session["user_id"]):
        del session["admin"]
    del session["user_id"]
    del session["username"]
    return redirect("/")
