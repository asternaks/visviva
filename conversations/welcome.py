import datetime

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters

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
    return CYCLE_LENGTH


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
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name
    print (f"starting for {user_name=}, {user_id=}")

    # Check if the user already exists in the database
    user = users_collection.find_one({"user_id": user_id})

    if not user:
        # Add a new user to the database
        users_collection.insert_one({"user_id": user_id, "name": user_name, "last_period": None})
        await update.message.reply_text(
            f"Hi {user_name}! Welcome to Vis Viva. I'm here to help you track your menstrual cycle and related habits. "
            "Let's get started! When did your last period start? (e.g., 15-11-2024)"
        )
        return LAST_CYCLE
    else:
        await update.message.reply_text(
            f"Welcome back, {user_name}! Let me know if you want to update your cycle information or track habits."
        )
        return ConversationHandler.END

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
