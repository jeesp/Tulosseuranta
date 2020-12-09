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
    return render_template("index.html", ottelut=list)

@app.route("/show_matches")
def show_matches():
    list = matches.matches_favorite_first()
    return render_template("kaikkiottelut.html", ottelut=list)

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

@app.route("/ottelu/<int:otteluid>", methods=["GET", "POST"])
def match(otteluid):
    if request.method == "GET":
        return redirect("/")
    if request.method == "POST":
        list = matches.refresh_match_page(otteluid)
        return render_template("ottelusivu.html", ottelu=list[0], viestit=list[1])

@app.route("/ottelu/<int:otteluid>/lisaakommentti", methods=["GET", "POST"])
def add_comment(otteluid):
    if request.method == "GET":
        return redirect("/")
    if request.method == "POST":
        viesti = request.form["viesti"]
        if len(viesti) < 1:
            flash("Tyhjä kenttä")
        if len(viesti) > 500:
            flash("Liian pitkä viesti")
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        messages.send_message(otteluid, viesti)
        list = matches.refresh_match_page(otteluid)
        return render_template("ottelusivu.html", ottelu=list[0], viestit=list[1])

@app.route("/ottelu/<int:otteluid>/lisaaArvio", methods=["GET", "POST"])
def add_rating(otteluid):
    if request.method == "GET":
        return redirect("/")
    if request.method == "POST":
        arvio = request.form["arvio"]
        ratings.add_rating(login.user_id(), otteluid, arvio)
        list = matches.refresh_match_page(otteluid)
        return render_template("ottelusivu.html", ottelu=list[0], viestit=list[1])

@app.route("/newteam", methods=["GET", "POST"])
def new_team():
    if login.user_id == 0:
        redirect("/")
    return render_template("newteam.html")

@app.route("/modifyteam", methods=["GET", "POST"])
def modify_team():
    if login.user_id == 0:
        return redirect("/")
    if login.is_admin(login.user_id()):
        return render_template("modifyteam.html")
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
        return render_template("modifyteam.html")
    flash("Ei admin-oikeutta")
    return redirect("/")

@app.route("/deleteteam", methods=["GET", "POST"])
def delete_team():
    if login.user_id == 0:
        return redirect("/")
    if login.is_admin(login.user_id()):
        team = request.form["team"]
        teams.delete_team(team)
        return render_template("modifyteam.html")
    flash("Ei admin-oikeutta")
    return redirect("/")

@app.route("/modifymatch", methods=["GET", "POST"])
def modify_match():
    if login.user_id == 0:
        return redirect("/")
    if login.is_admin(login.user_id()):
        return render_template("modifymatch.html")
    flash("Ei admin-oikeutta")
    return redirect("/")

@app.route("/deletematch", methods=["GET", "POST"])
def delete_match():
    if request.method == "GET":
        return redirect("/")
    if login.user_id == 0:
        return redirect("/")
    if login.is_admin(login.user_id()):
        otteluid = request.form["otteluid"]
        matches.delete_match(otteluid)
        return render_template("modifymatch.html")
    flash("Ei admin-oikeutta")
    return redirect("/")

@app.route("/modifymatchresult", methods=["GET", "POST"])
def modify_match_result():
    if request.method == "GET":
        return redirect("/")
    if login.user_id == 0:
        return redirect("/")
    if login.is_admin(login.user_id()):
        otteluid = request.form["otteluid"]
        homepoints = request.form["homepoints"]
        awaypoints = request.form["awaypoints"]
        matches.match_modify(otteluid, homepoints, awaypoints)
        return render_template("modifymatch.html")
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
        joukkue1 = request.form["team1"]
        session["team1"] = joukkue1
        joukkue2 = request.form["team2"]
        session["team2"] = joukkue2
        pisteet1 = request.form["team1points"]
        session["team1points"] = pisteet1
        pisteet2 = request.form["team2points"]
        session["team2points"] = pisteet2
        if len(joukkue1) < 1 or len(joukkue2) < 1  or len(pisteet1) < 1  or len(pisteet2) < 1:
            flash("Jokin kenttä oli tyhjä.")
            return render_template("newmatch.html")
        if int(pisteet1) < 0 or int(pisteet1) > 10 or int(pisteet2) < 0 or int(pisteet2) > 10:
            flash("Nyt vaikuttaa huijaukselta.. Pisteitä liikaa tai liian vähän")
            return render_template("newmatch.html")
        if int(pisteet1) == int(pisteet2):
            flash("Hmm... tasapeli? Ratkaistaan sudden deathilla")
            return render_template("newmatch.html")
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        if matches.match_played(joukkue1, joukkue2, pisteet1, pisteet2):

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
    return render_template("highscoreteam.html", joukkueet=list)

@app.route("/lowscoreteam", methods=["GET", "POST"])
def lowscore_for_teams():
    list = highscore.lowscore_for_teams()
    return render_template("lowscoreteam.html", joukkueet=list)

@app.route("/highscoreplayer", methods=["GET", "POST"])
def highscore_for_players():
    list = highscore.highscore_for_players()
    return render_template("highscoreplayer.html", pelaajat=list)

@app.route("/lowscoreplayer", methods=["GET", "POST"])
def lowscore_for_players():
    list = highscore.lowscore_for_players()
    return render_template("lowscoreplayer.html", pelaajat=list)

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
