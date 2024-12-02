from telegram import Update
from telegram.ext import ContextTypes

from dal.users import users_collection
from conversations.utils import ASK_CYCLE_LENGTH, MENU  # Import the appropriate state

from conversations.welcome import start

async def ask_cycle_length(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = None

    # Determine if the update came from a message or a callback query
    if update.message:
        user_id = update.message.from_user.id
    elif update.callback_query:
        user_id = update.callback_query.from_user.id

    # Check if user_id was set correctly
    if not user_id:
        print("Error: User ID not found in update.")  # Debugging
        return ConversationHandler.END

    # Retrieve user information from the database
    user = users_collection.find_one({"user_id": user_id})

    if user:
        # Send a message to ask for the average cycle length
        if update.message:
            await update.message.reply_text("What is your average cycle length in days? (e.g., 28)")
        elif update.callback_query:
            await update.callback_query.message.reply_text("What is your average cycle length in days? (e.g., 28)")

        return ASK_CYCLE_LENGTH  # Return state to continue the conversation
    else:
        if update.message:
            await update.message.reply_text(
                "I don't have your information yet. Start with /start to get set up!"
            )
        elif update.callback_query:
            await update.callback_query.message.reply_text(
                "I don't have your information yet. Start with /start to get set up!"
            )

        return ConversationHandler.END


async def capture_cycle_length(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        user_id = update.message.from_user.id
        cycle_length = int(update.message.text)

        # Validate cycle length range
        if 15 <= cycle_length <= 40:
            # Update the user's average cycle length in the database
            users_collection.update_one(
                {"user_id": user_id},
                {"$set": {"cycle_length": cycle_length}}
            )
            await update.message.reply_text(
                f"Got it! I've set your average cycle length to {cycle_length} days."
            )

            # Call the start function to display the main menu options
            await start(update, context)  # Display main menu

            return MENU  # Return to the MENU state to indicate we're back in the main menu

        else:
            # Ask again if the input is not in the correct range
            await update.message.reply_text("Please provide a cycle length between 15 and 40 days.")
            return ASK_CYCLE_LENGTH

    except ValueError:
        # Handle non-integer input
        await update.message.reply_text("Please enter a valid number for your cycle length.")
        return ASK_CYCLE_LENGTH

