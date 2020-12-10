from db import db

def match_ratings(match_id):
    #fetching the ratings by match id
    sql = "SELECT arvio FROM arviot WHERE ottelu_id=:id"
    result = db.session.execute(sql, {"id":match_id})
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
    sql = "SELECT arvio FROM arviot A \
        WHERE kayttaja_id=:userid AND ottelu_id=:otteluid"
    result = db.session.execute(sql, {"userid":user_id, "otteluid":match_id})
    previous_rating = result.fetchone()
    if previous_rating is None:
        sql = "INSERT INTO arviot (kayttaja_id, ottelu_id, arvio)\
            VALUES (:userid, :otteluid, :arvio)"
        db.session.execute(sql, {"userid":user_id, "otteluid":match_id, "arvio":rating})
        db.session.commit()
        return
    if previous_rating == rating:
        return
    sql = "UPDATE arviot SET arvio =:arvio \
        WHERE kayttaja_id=:userid AND ottelu_id=:otteluid"
    db.session.execute(sql, {"arvio":rating, "userid":user_id, "otteluid":match_id})
    db.session.commit()
    return
