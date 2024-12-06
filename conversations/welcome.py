import datetime

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

from conversations.utils import show_actions, MENU
from dal.users import users_collection

LAST_CYCLE, CYCLE_LENGTH = range(2)


async def capture_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id

    try:
        # Parse the date
        start_date = datetime.datetime.strptime(update.message.text, '%d-%m-%Y')

        # Update the user's last period in the database
        users_collection.update_one(
            {"user_id": user_id},
            {"$set": {"last_period": start_date.isoformat()}}  # Store as ISO 8601 string
        )

        await update.message.reply_text(
            f"Got it! Your last period was on {start_date.strftime('%d-%m-%Y')}."
            " You can now use the /predict_cycle command to estimate your next period."
        )
    except ValueError:
        await update.message.reply_text("Please enter a valid date in the format DD-MM-YYYY.")
    return MENU


# Capture cycle length from the user
async def capture_cycle_length(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id

    try:
        # Parse the cycle length as an integer
        cycle_length = int(update.message.text)

        if 15 <= cycle_length <= 40:  # Validate reasonable cycle length range
            # Update the user's average cycle length in the database
            users_collection.update_one(
                {"user_id": user_id},
                {"$set": {"cycle_length": cycle_length}}
            )
            await update.message.reply_text(
                f"Got it! I've set your average cycle length to {cycle_length} days. "
                "You can now use the /predict_cycle command to estimate your next period."
            )
        else:
            await update.message.reply_text(
                "Please provide a cycle length between 15 and 40 days."
            )
    except ValueError:
        await update.message.reply_text(
            "Please enter a valid number for your cycle length."
        )
    return ConversationHandler.END



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Define the main menu buttons
    keyboard = [
        [InlineKeyboardButton("Log Symptoms", callback_data="log_symptoms")],
        [InlineKeyboardButton("Predict Cycle", callback_data="predict_cycle")],
        [InlineKeyboardButton("Show Data", callback_data="show_data")],
        [InlineKeyboardButton("Ask Cycle Length", callback_data="ask_cycle_length")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Always send a new message for the main menu, regardless of how the user arrived here
    if update.message:
        await update.message.reply_text(
            "Welcome to the main menu. Please select an option:", reply_markup=reply_markup
        )
    elif update.callback_query:
        await update.callback_query.message.reply_text(
            "Welcome to the main menu. Please select an option:", reply_markup=reply_markup
        )

    return MENU


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    return ConversationHandler.END

conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LAST_CYCLE: [MessageHandler(filters.Regex("^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|1[0-2])-\d{4}$"), capture_date)],
            CYCLE_LENGTH: [MessageHandler(filters.Regex("^(1[5-9]|[2-3][0-9]|40)$"), capture_cycle_length)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
