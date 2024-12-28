from datetime import datetime
import os
import asyncio
from pymongo import MongoClient

from config import get_mongo_uri
from pydantic import BaseModel
from telegram import Bot

def format_rec(rec: dict):
    text = ""
    for k, v in rec.items():
        if k in ('Tags', '_id', 'Day of the Cycle '):
            continue
        if k == "Physical Sympotms":
            text+=f"• *{k}*:\n          {v.replace('\n', '\n          ')} \n"
            continue
        text+=f"• *{k}*: {v} \n"
    return text

class User(BaseModel):
    user_id: int
    user_name: str
    last_period: datetime
    cycle_length: int

def morning_routine(bot, db):
    users_collection = db['users']
    recs = db['recommendations']

    for user_raw in users_collection.find():
        user = User(**user_raw)
        rec = recs.find_one({"Day of the Cycle ": (datetime.now()-user.last_period).days})
        if rec is not None:
            rec_text = format_rec(rec)
        else:
            rec_text = "Fuck you no recommendation for you specifically"
        message = f"Good morning {user.user_name}, day in cycle is {(datetime.now()-user.last_period).days}, the recommendation is:\n{rec_text}"
        print(message)
        asyncio.run(bot.send_message(chat_id=user.user_id, text=message, parse_mode='Markdown'))

if __name__ == "__main__":
    BOT_TOKEN = os.getenv("BOT_TOKEN")  # This retrieves the Telegram bot token
    if not BOT_TOKEN:
        raise ValueError("Bot token not found! Ensure BOT_TOKEN is set in the environment or .env file.")

    MONGO_URI = get_mongo_uri()
    client = MongoClient(MONGO_URI)
    db = client[os.getenv("MONGO_DB_NAME")]


    bot = Bot(token=BOT_TOKEN)
    morning_routine(bot, db)