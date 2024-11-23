from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update
from telegram.ext import ContextTypes
from dal.users import users_collection
import datetime


async def show_symptom_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Define the symptoms
    symptoms = ["Headache", "Cramps", "Fatigue", "Mood Swings", "Nausea", "Other"]

    # Create buttons for symptoms
    keyboard = [
        [InlineKeyboardButton(symptom, callback_data=symptom)] for symptom in symptoms
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Please select a symptom to log:", reply_markup=reply_markup
    )
async def log_selected_symptom(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    selected_symptom = query.data  # This contains the symptom the user selected

    # Log the symptom in the database
    symptom_entry = {
        "date": datetime.datetime.now().isoformat(),
        "symptoms": selected_symptom
    }
    users_collection.update_one(
        {"user_id": user_id},
        {"$push": {"symptom_log": symptom_entry}}
    )

    # Acknowledge the button press
    await query.answer()

    # Confirm the symptom has been logged
    await query.edit_message_text(
        f"Got it! I've logged your symptom: {selected_symptom}."
    )
