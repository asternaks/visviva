from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from actions.ask_cycle_length import ask_cycle_length
from actions.predict_cycle import predict_cycle
from actions.show_data import show_data
import datetime
import os

from conversations.welcome import conv_handler
from dal.users import users_collection


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
    # application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("show_data", show_data))
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, capture_data))
    application.add_handler(CommandHandler("ask_cycle_length", ask_cycle_length))
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, capture_cycle_length))
    application.add_handler(CommandHandler("predict_cycle", predict_cycle))
    application.add_handler(conv_handler)
    # Start polling
    application.run_polling()

if __name__ == "__main__":
    main()
