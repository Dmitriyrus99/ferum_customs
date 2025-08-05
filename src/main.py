import os

from aiogram import Bot, Dispatcher
from fastapi import FastAPI

app = FastAPI()

bot = Bot(token=os.getenv("TELEGRAM_TOKEN", ""))
dp = Dispatcher()


@app.get("/")
async def read_root():
    return {"status": "ok"}
