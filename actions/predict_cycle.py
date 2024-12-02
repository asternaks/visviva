import datetime
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from dal.users import users_collection
from conversations.welcome import start  # Import start to call the main menu

async def predict_cycle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Get callback query and user ID from the button click
    query = update.callback_query
    user_id = query.from_user.id

    # Retrieve user information from the database
    user = users_collection.find_one({"user_id": user_id})

    if user and user.get("last_period") and user.get("cycle_length"):
        last_period = user["last_period"]  # Retrieve stored last_period
        if isinstance(last_period, str):  # Handle potential string storage
            last_period = datetime.datetime.fromisoformat(last_period)

        cycle_length = user["cycle_length"]  # Retrieve stored cycle_length

        # Calculate the next period date
        next_cycle = last_period + datetime.timedelta(days=cycle_length)

        response_text = f"Your next period is predicted to start on {next_cycle.strftime('%d-%m-%Y')}."

        # Send a new message with the prediction so it stays in the chat
        await query.message.reply_text(response_text)

        # Delay for 3 seconds to let the user read the prediction
        await asyncio.sleep(3)

        # After showing the prediction, navigate back to the main menu
        await start(update, context)  # Redirect user to the main menu

    else:
        response_text = (
            "I don’t have enough information to predict your next cycle. "
            "Please provide your last period date (DD-MM-YYYY) and average cycle length (/ask_cycle_length)."
        )

        # Send a new message with the prompt for more information so it stays in the chat
        await query.message.reply_text(response_text)

        # Delay for 3 seconds to let the user read the prompt
        await asyncio.sleep(3)

        # After showing the error message, navigate back to the main menu
        await start(update, context)  # Redirect user to the main menu
