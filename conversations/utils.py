from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# State definitions for top level conversation
START, MENU, ASK_CYCLE_LENGTH, WAIT_FOR_DATE, PREDICT_CYCLE, LOG_SYMPTOMS = map(chr, range(6    ))

# Meta states
STOPPING, SHOW_DATA = map(chr, range(8, 10))

async def show_actions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Create buttons for actions
    keyboard = [

            [InlineKeyboardButton("Input Cycle Length ", callback_data=ASK_CYCLE_LENGTH)],
            [InlineKeyboardButton("Input Last Cycle", callback_data="?")],
            [InlineKeyboardButton("Log New Symptom", callback_data=LOG_SYMPTOMS)],
            [InlineKeyboardButton("Predict Cycle", callback_data=PREDICT_CYCLE)],

    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Please select what you want to do:", reply_markup=reply_markup
    )