import httpx
import asyncio
from fastapi import FastAPI

app = FastAPI()
localhost="http://localhost:9999/api"

@app.post("/game/new")
def new_game(user: str, new_game_id: str):
    
    r_user = httpx.get(localhost + "/v4/uuid/" + user)
    uuid = r_user.json()["user_id"]
    
    params = {
        'user_id': uuid,
        'game_id': new_game_id
    }
    r = httpx.post(localhost+"/v4/create", json=params)
    
    return r.status_code

@app.post("/game/{user_id}")
async def guess_word(user_id: int):
    pass