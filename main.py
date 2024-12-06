from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters, \
    ConversationHandler
from actions.ask_cycle_length import ask_cycle_length, capture_cycle_length 
from actions.fallback import fallback
from actions.log_symptoms import log_selected_symptom, show_symptom_options
from actions.predict_cycle import predict_cycle
from actions.show_data import show_data
import datetime
import os

from conversations.utils import START, MENU, STOPPING, SHOW_DATA, PREDICT_CYCLE, LOG_SYMPTOMS, ASK_CYCLE_LENGTH, \
    WAIT_FOR_DATE
from conversations.welcome import conv_handler, start, capture_date
from dal.users import users_collection


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    #
    # # CallbackQueries need to be answered, even if no notification to the user is needed
    # await query.answer()
    # await query.edit_message_text(text=f"Selected option: {query.data}")

    if query.data == LOG_SYMPTOMS:
        await show_symptom_options(update, context)
    return query.data

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End Conversation by command."""
    await update.message.reply_text("Okay, bye.")

    return STOPPING

# Main function
def main():
    print("started")
    # Retrieve the bot token from environment variables
    BOT_TOKEN = os.getenv("BOT_TOKEN")  # This retrieves the Telegram bot token
    if not BOT_TOKEN:
        raise ValueError("Bot token not found! Ensure BOT_TOKEN is set in the environment or .env file.")

    # Create the bot application
    application = Application.builder().token(BOT_TOKEN).build()

    from telegram.ext import MessageHandler, filters

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],  # Start the main menu
        states={
            MENU: [
                CallbackQueryHandler(show_symptom_options, pattern="^log_symptoms$"),
                CallbackQueryHandler(start, pattern="^back$"),
                CallbackQueryHandler(predict_cycle, pattern="^predict_cycle$"),
                CallbackQueryHandler(show_data, pattern="^show_data$"),
                CallbackQueryHandler(ask_cycle_length, pattern="^ask_cycle_length$")
            ],
            ASK_CYCLE_LENGTH: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, capture_cycle_length)
            ],
            WAIT_FOR_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, capture_date)],
            SHOW_DATA: [CallbackQueryHandler(show_data, pattern="^show_data$")],
            LOG_SYMPTOMS: [
                CallbackQueryHandler(log_selected_symptom,
                                     pattern="^(Headache|Cramps|Fatigue|Mood Swings|Nausea|Other|back|finish)$")
            ],
            STOPPING: [CommandHandler("start", start)]
        },
        fallbacks=[CommandHandler("stop", stop)],  # Handle stop command to end the conversation
    )

    application.add_handler(conv_handler)
    # application.add_handler()
    # application.add_handler(CallbackQueryHandler(button))

    application.add_handler(MessageHandler(filters.COMMAND, fallback))


    application.run_polling()

if __name__ == "__main__":
    main()
