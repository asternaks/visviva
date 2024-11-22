from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from pymongo import MongoClient
from config import get_mongo_uri  # Properly using get_mongo_uri
import datetime
import os

# Correctly set the BOT_TOKEN
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Check if BOT_TOKEN is properly loaded
if not BOT_TOKEN:
    raise ValueError("Bot token not found! Ensure BOT_TOKEN is set in the environment or .env file.")

# Get the MongoDB URI (properly encoded)
MONGO_URI = get_mongo_uri()

# MongoDB setup
from pymongo import MongoClient
client = MongoClient(MONGO_URI)
db = client['vis_viva']
users_collection = db['users']


# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
            "Let's get started! When did your last period start? (e.g., 2024-11-15)"
        )
    else:
        await update.message.reply_text(
            f"Welcome back, {user_name}! Let me know if you want to update your cycle information or track habits."
        )


# Capture and store the last period date
async def capture_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id

    try:
        # Parse the date
        start_date = datetime.datetime.strptime(update.message.text, '%Y-%m-%d')

        # Update the user's last period in the database
        users_collection.update_one(
            {"user_id": user_id},
            {"$set": {"last_period": start_date}}
        )

        await update.message.reply_text(
            f"Got it! Your last period was on {start_date.strftime('%Y-%m-%d')}."
            " I’ll help you track your cycle. You can log symptoms, check your next cycle date, or get insights!"
        )
    except ValueError:
        await update.message.reply_text("Please enter a valid date in the format YYYY-MM-DD.")


# Retrieve user data
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


# Main function
def main():
    print("started")
    # Retrieve the bot token from environment variables
    BOT_TOKEN = os.getenv("BOT_TOKEN")  # This retrieves the Telegram bot token
    if not BOT_TOKEN:
        raise ValueError("Bot token not found! Ensure BOT_TOKEN is set in the environment or .env file.")

    # Create the bot application
    application = Application.builder().token(BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("show_data", show_data))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, capture_date))

    # Start polling
    application.run_polling()


if __name__ == "__main__":
    main()

