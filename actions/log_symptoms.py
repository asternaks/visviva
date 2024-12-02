from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update
from telegram.ext import ContextTypes
from dal.users import users_collection
import datetime
from conversations.welcome import start
from conversations.utils import START, MENU, show_actions, LOG_SYMPTOMS
import traceback



async def show_symptom_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    symptoms = ["Headache", "Cramps", "Fatigue", "Mood Swings", "Nausea", "Other"]
    keyboard = [
        [InlineKeyboardButton(symptom, callback_data=symptom)] for symptom in symptoms
    ]
    keyboard.append([InlineKeyboardButton("Finish", callback_data="finish")])  # Add Finish button
    keyboard.append([InlineKeyboardButton("Back", callback_data="back")])  # Add Back button

    reply_markup = InlineKeyboardMarkup(keyboard)
    message_text = "Please select a symptom to log (or click Finish when done):"

    try:
        if update.callback_query:
            current_message = update.callback_query.message

            # Check if the current message content and reply markup are the same
            if current_message.text != message_text or current_message.reply_markup != reply_markup:
                await update.callback_query.edit_message_text(
                    message_text, reply_markup=reply_markup
                )
            else:
                print("No changes detected in message text or reply markup, skipping edit.")
        elif update.message:
            await update.message.reply_text(message_text, reply_markup=reply_markup)

    except Exception as e:
        # If edit fails, send a new message instead
        print(f"Edit message failed: {e}, sending a new message instead.")
        traceback.print_exc()  # Print the complete traceback for better debugging information
        if update.callback_query:
            await update.callback_query.message.reply_text(
                message_text, reply_markup=reply_markup
            )

    return LOG_SYMPTOMS



import traceback

async def log_selected_symptom(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        query = update.callback_query
        selected_symptom = query.data

        # Debugging: Print which symptom was selected
        print(f"Selected symptom: {selected_symptom}")

        # Handle the "Back" button
        if selected_symptom == "back":
            print("Back button pressed, redirecting to main menu...")
            await start(update, context)  # Redirect to the main menu
            return MENU  # Return to the MENU state

        # Handle the "Finish" button
        if selected_symptom == "finish":
            print("Finish button pressed, attempting to save symptoms...")  # Debugging

            # Save all selected symptoms to the database
            user_id = query.from_user.id
            if 'symptoms' in context.user_data and context.user_data['symptoms']:
                symptom_entry = {
                    "date": datetime.datetime.now().isoformat(),
                    "symptoms": context.user_data['symptoms']
                }

                try:
                    result = users_collection.update_one(
                        {"user_id": user_id},
                        {"$push": {"symptom_log": symptom_entry}}
                    )

                    # Debugging: Check if the database update was successful
                    if result.modified_count > 0:
                        response_text = f"Got it! I've logged your symptoms: {', '.join(context.user_data['symptoms'])}."
                        print(f"Symptoms logged successfully for user {user_id}")
                    else:
                        response_text = (
                            "It looks like I wasn't able to log your symptoms. "
                            "Please make sure your information is set up and try again."
                        )
                        print(f"Failed to log symptoms for user {user_id}")

                    # Clear symptoms from context after saving
                    context.user_data.pop('symptoms', None)
                except Exception as e:
                    response_text = "An error occurred while trying to save your symptoms. Please try again later."
                    print(f"Error occurred while saving symptoms for user {user_id}: {e}")
                    traceback.print_exc()

                await query.answer()  # Acknowledge the callback query
                await query.message.reply_text(response_text)

                # After saving, navigate back to the main menu
                await start(update, context)
                return MENU

            else:
                print("No symptoms to log.")  # Debugging
                await query.answer()  # Acknowledge the callback query
                await query.message.reply_text("No symptoms selected to log.")

                # Navigate back to the main menu
                await start(update, context)
                return MENU

        # If a symptom was selected, store it in the user data
        if 'symptoms' not in context.user_data:
            context.user_data['symptoms'] = []

        context.user_data['symptoms'].append(selected_symptom)
        print(f"Current symptoms: {context.user_data['symptoms']}")  # Debugging

        # Acknowledge the callback query
        await query.answer()  # Acknowledge the callback query

        # Show options again for more selection
        await show_symptom_options(update, context)

        return LOG_SYMPTOMS

    except Exception as e:
        print(f"Error occurred in log_selected_symptom: {e}")
        traceback.print_exc()  # Print the complete traceback for better debugging information
        await query.message.reply_text("An error occurred. Please try again later.")
        return LOG_SYMPTOMS

    # Send the response text as a new message
    await query.message.reply_text(response_text)

    # After logging the symptom, navigate back to the main menu
    await start(update, context)  # Redirect to the main menu
    return MENU


