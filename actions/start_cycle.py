from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from conversations.utils import START_CYCLE_OPTIONS, WAIT_FOR_DATE, MENU
from dal.users import users_collection


async def start_cycle (update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get callback query and user ID from the button click
    query = update.callback_query
    user_id = query.from_user.id

    options = ["My cycle started today","Input custom date"]

    keyboard = [
        [InlineKeyboardButton(option, callback_data=option)] for option in options

    ]
    keyboard.append([InlineKeyboardButton("Back", callback_data="back")])  # Add Back button
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        "Please select an option:", reply_markup=reply_markup
    )
    return START_CYCLE_OPTIONS

async def parse_start_cycle_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if query.data == "My cycle started today":
        # Parse the date
        start_date = datetime.now()

        # Update the user's last period in the database
        users_collection.update_one(
            {"user_id": user_id},
            {"$set": {"last_period": start_date.isoformat()}}  # Store as ISO 8601 string
        )

        # Use query to send the response
        await query.edit_message_text(
            f"Got it! Your last period was on {start_date.strftime('%d-%m-%Y')}. You can now use the /predict_cycle command to estimate your next period."
        )

    elif query.data == "Input custom date":
        return WAIT_FOR_DATE
    else:
        return MENU
