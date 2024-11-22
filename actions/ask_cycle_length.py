from telegram import Update
from telegram.ext import ContextTypes

from dal.users import users_collection


async def ask_cycle_length(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user = users_collection.find_one({"user_id": user_id})

    if user:
        await update.message.reply_text(
            "What is your average cycle length in days? (e.g., 28)"
        )
    else:
        await update.message.reply_text(
            "I don't have your information yet. Start with /start to get set up!"
        )
