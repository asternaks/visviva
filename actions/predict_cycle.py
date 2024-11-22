import datetime

from telegram import Update
from telegram.ext import ContextTypes

from dal.users import users_collection


async def predict_cycle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user = users_collection.find_one({"user_id": user_id})

    if user and user.get("last_period") and user.get("cycle_length"):
        last_period = user["last_period"]  # Retrieve stored last_period
        if isinstance(last_period, str):  # Handle potential string storage
            last_period = datetime.datetime.fromisoformat(last_period)

        cycle_length = user["cycle_length"]  # Retrieve stored cycle_length

        # Calculate the next period date
        next_cycle = last_period + datetime.timedelta(days=cycle_length)

        await update.message.reply_text(
            f"Your next period is predicted to start on {next_cycle.strftime('%d-%m-%Y')}."
        )
    else:
        await update.message.reply_text(
            "I don’t have enough information to predict your next cycle. "
            "Please provide your last period date (DD-MM-YYYY) and average cycle length (/ask_cycle_length)."
        )
