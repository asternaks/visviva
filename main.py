from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from pymongo import MongoClient
from dotenv import load_dotenv
import datetime
import os

# Connect to MongoDB
MONGO_URI = "mongodb+srv://alexsternik:dtxqIYBJdohN4cZg@cluster0.lrpt9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client['vis_viva']  # Database name
users_collection = db['users']  # Collection name


# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name

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
        la

# Load variables from the .env file
load_dotenv()

# Retrieve BOT_TOKEN
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Access the variables
mongo_uri = os.getenv("MONGO_URI")
bot_token = os.getenv("BOT_TOKEN")

print(f"Mongo URI: {MONGO_URI}")
print(f"Bot Token: {BOT_TOKEN}")