from db import db

def match_ratings(match_id):
    #fetching the ratings by match id
    sql = "SELECT rating FROM Ratings WHERE match_id=:match_id"
    result = db.session.execute(sql, {"match_id":match_id})
    ratings = result.fetchall()
    thumbs_up = 0
    thumbs_down = 0
    for rating in ratings:
        if rating[0] == 1:
            thumbs_up += 1
        if rating[0] == -1:
            thumbs_down += 1
    ratings_list = [thumbs_up, thumbs_down]
    return ratings_list

def add_rating(user_id, match_id, rating):
    #adding a rating to a match (and removing old one)
    sql = "SELECT rating FROM Ratings \
        WHERE user_id=:user_id AND match_id=:match_id"
    result = db.session.execute(sql, {"user_id":user_id, "match_id":match_id})
    previous_rating = result.fetchone()
    if previous_rating is None:
        sql = "INSERT INTO Ratings (user_id, match_id, rating)\
            VALUES (:user_id, :match_id, :rating)"
        db.session.execute(sql, {"user_id":user_id, "match_id":match_id, "rating":rating})
        db.session.commit()
        return
    if previous_rating == rating:
        return
    sql = "UPDATE Ratings SET rating =:rating \
        WHERE user_id=:user_id AND match_id=:match_id"
    db.session.execute(sql, {"rating":rating, "user_id":user_id, "match_id":match_id})
    db.session.commit()
    return

