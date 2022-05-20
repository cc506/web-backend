import httpx
from fastapi import FastAPI

app = FastAPI()

@app.post("/game/new")
def new_game():
    pass

@app.post("/game/{user_id}")
def guess_word(user_id: int):
    pass