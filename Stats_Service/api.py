from http import HTTPStatus
from fastapi import FastAPI, Depends
from Stats_Service.models import User, Game
from Stats_Service.update.update import redisClient
import sqlite3
import contextlib
import uuid

app = FastAPI()


def get_db():
    with contextlib.closing(sqlite3.connect("StatDB_0.db")) as db:
        db.row_factory = sqlite3.Row
        yield db
def get_db1():
    with contextlib.closing(sqlite3.connect("StatDB_1.db")) as db1:
        db1.row_factory = sqlite3.Row
        yield db1
def get_db2():
    with contextlib.closing(sqlite3.connect("StatDB_2.db")) as db2:
        db2.row_factory = sqlite3.Row
        yield db2

# Posting a u or loss for a particular game, along with a timestamp and number of guesses.
@app.post("/games")
def add_game(game: Game, db: sqlite3.Connection = Depends(get_db), 
             db1: sqlite3.Connection = Depends(get_db1), db2: sqlite3.Connection = Depends(get_db2)):
    shard_key = int(uuid.UUID(game.user_id)) % (3)
    #print(shard_key)
    if shard_key == 0:
        db.execute(
            """
            INSERT INTO games (user_id, game_id, finished, guesses, won) VALUES (?, ?, ?, ?, ?);
            """, (game.user_id, game.game_id, game.finished, game.guesses, game.won, )
        )
        db.commit()
        
        return HTTPStatus.OK
        
    elif shard_key == 1:
        db1.execute(
            """
            INSERT INTO games (user_id, game_id, finished, guesses, won) VALUES (?, ?, ?, ?, ?);
            """, (game.user_id, game.game_id, game.finished, game.guesses, game.won, )
        )
        db1.commit()
        
        return HTTPStatus.OK
    
    elif shard_key == 2:
        db2.execute(
            """
            INSERT INTO games (user_id, game_id, finished, guesses, won) VALUES (?, ?, ?, ?, ?);
            """, (game.user_id, game.game_id, game.finished, game.guesses, game.won, )
        )
        db2.commit()
        
        return HTTPStatus.OK


# Retrieving the statistics for a user.
@app.get("/games/{user_id}")
def get_statistics(user_id: str, db: sqlite3.Connection = Depends(get_db), 
                   db1: sqlite3.Connection = Depends(get_db1), db2: sqlite3.Connection = Depends(get_db2)):
    shard_key = int(uuid.UUID(user_id)) % (3)  
    if shard_key == 0:
        cur = db.execute(
            """
            SELECT game_id, finished, guesses, won FROM games WHERE user_id = (?);
            """,
            ([user_id]))
        stats = cur.fetchall()
        print(stats)
        
        cur = db.execute(
            """
            SELECT streak, beginning, ending FROM streaks WHERE user_id = (?);
            """,
            ([user_id]))
        streak = cur.fetchall()
        
        cur = db.execute(
            """
            SELECT * FROM wins WHERE user_id = (?);
            """,
            ([user_id]))
        wins = cur.fetchall()
        
        return ({"Stats": stats, "Streak": streak, "Wins": wins})
    
    elif shard_key == 1:
        cur = db1.execute(
            """
            SELECT game_id, finished, guesses, won FROM games WHERE user_id = (?);
            """,
            ([user_id]))
        stats = cur.fetchall()
        
        cur = db1.execute(
            """
            SELECT streak, beginning, ending FROM streaks WHERE user_id = (?);
            """,
            ([user_id]))
        streak = cur.fetchall()
        
        cur = db1.execute(
            """
            SELECT * FROM wins WHERE user_id = (?);
            """,
            ([user_id]))
        wins = cur.fetchall()
        
        return {"Stats": stats, "Streak": streak, "Wins": wins}
    
    elif shard_key == 2:
        cur = db2.execute(
            """
            SELECT game_id, finished, guesses, won FROM games WHERE user_id = (?);
            """,
            ([user_id]))
        stats = cur.fetchall()
        
        cur = db2.execute(
            """
            SELECT streak, beginning, ending FROM streaks WHERE user_id = (?);
            """,
            ([user_id]))
        streak = cur.fetchall()
        
        cur = db2.execute(
            """
            SELECT * FROM wins WHERE user_id = (?);
            """,
            ([user_id]))
        wins = cur.fetchall()
        
        return {"Stats": stats, "Streak": streak, "Wins": wins}
    
# Retrieving the user.
@app.get("/uuid/{user}")
def get_uuid(user: str, db: sqlite3.Connection = Depends(get_db), 
                   db1: sqlite3.Connection = Depends(get_db1), db2: sqlite3.Connection = Depends(get_db2)):
    user_list = []
     
    cur = db.execute(
        """
        SELECT user_id FROM users WHERE username = ?
        """,
        ([user])
    )
    users = cur.fetchall()
    for u in users:
        user_list.append(u)
    users.clear()

    cur = db1.execute(
        """
        SELECT user_id FROM users WHERE username = ?
        """,
        ([user])
    )
    users = cur.fetchall()
    for u in users:
        user_list.append(u)
    users.clear()

    cur = db2.execute(
        """
        SELECT user_id FROM users WHERE username = ?
        """,
        ([user])
    )
    users = cur.fetchall()
    for u in users:
        user_list.append(u)
    users.clear()
    
    
    if not user_list:
        
        user_id = uuid.uuid4()
        print(user_id)
        shard_key = int(user_id) % (3)
        user_id = str(user_id)
        print(user_id)
        
        if shard_key == 0:
            cur = db.execute(
                """
                INSERT into users (user_id, username) VALUES (?, ?)
                """,
                (user_id, user))
            db.commit()
            
            return {"user_id": user_id}
        
        elif shard_key == 1:
            cur = db1.execute(
                """
                INSERT into users (user_id, username) VALUES (?, ?)
                """,
                (user_id, user))
            db1.commit()
            
            return {"user_id": user_id}
        
        elif shard_key == 2:
            cur = db2.execute(
                """
                INSERT into users (user_id, username) VALUES (?, ?)
                """,
                (user_id, user))
            db2.commit()
            
            return {"user_id": user_id}
    else:
        
        return user_list[0]

# Retrieving the top 10 users by number of wins
@app.get("/top10wins")
def get_top_10_users_by_wins():
    return {"Top_10_Wins": redisClient.zrange("Wins", 0, -1, withscores=True, desc=True) }


# Retrieving the top 10 users by longest streak
@ app.get("/top10streak")
def get_top_10_users_by_longest_streak():
    return {"Top_10_Streaks": redisClient.zrange("Streaks", 0, -1, withscores=True, desc=True)}