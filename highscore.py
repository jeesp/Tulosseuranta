from db import db

def highscore_for_teams():
    sql = "SELECT X.name, SUM(X.wins), SUM(X.losses),\
        (SELECT ROUND((SUM(X.wins)*1.0)/coalesce(NULLIF \
        (SUM(X.losses),0),1),2) AS DECIMAL) FROM Teams X \
        GROUP BY X.name ORDER BY SUM(X.wins)- SUM(X.losses) \
        DESC, SUM(X.wins) DESC, SUM(X.losses) ASC LIMIT 5"
    result = db.session.execute(sql)
    return result.fetchall()

def lowscore_for_teams():
    sql = "SELECT X.name, SUM(X.wins), SUM(X.losses),(SELECT \
        ROUND((SUM(X.wins)*1.0)/coalesce(NULLIF(SUM(X.losses),0),1),2) \
        AS DECIMAL) FROM Teams X GROUP BY X.name ORDER BY SUM(X.wins) \
        -SUM(X.losses) ASC, SUM(X.losses) DESC, SUM(X.wins) ASC LIMIT 5"
    result = db.session.execute(sql)
    return result.fetchall()

def highscore_for_players():
    sql = "SELECT S.username, SUM(X.wins), SUM(X.losses),(SELECT \
        ROUND((SUM(X.wins)*1.0)/coalesce(NULLIF(SUM(X.losses),0),1),2) \
        AS DECIMAL) FROM Users S, Teams X, Players Y \
        WHERE S.id=Y.member_id AND X.id=Y.team_id GROUP BY S.username \
        ORDER BY SUM(X.wins)-SUM(X.losses) DESC, \
        SUM(X.wins) DESC, SUM(X.losses) ASC LIMIT 5"
    result = db.session.execute(sql)
    return result.fetchall()

def lowscore_for_players():
    sql = "SELECT S.username, SUM(X.wins), SUM(X.losses),(SELECT \
        ROUND((SUM(X.wins)*1.0)/coalesce(NULLIF(SUM(X.losses),0),1),2) \
        AS DECIMAL) FROM Users S, Teams X, Players Y \
        WHERE S.id=Y.member_id AND X.id=Y.team_id GROUP BY S.username \
        ORDER BY SUM(X.wins)-SUM(X.losses) ASC, SUM(X.losses) DESC, \
        SUM(X.wins) ASC LIMIT 5"
    result = db.session.execute(sql)
    return result.fetchall()
