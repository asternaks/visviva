from telegram import Update
from telegram.ext import ContextTypes

from dal.users import users_collection


async def show_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user = users_collection.find_one({"user_id": user_id})

    if user and user.get("last_period"):
        last_period = user["last_period"].strftime('%Y-%m-%d')
        await update.message.reply_text(
            f"Here's what I know about you:\n"
            f"Name: {user.get('name')}\n"
            f"Last Period: {last_period}"
        )
    else:
        await update.message.reply_text(
            "I don’t have any cycle information for you yet. Use the format YYYY-MM-DD to provide your last period date!"
        )
