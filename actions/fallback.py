from telegram import Update
from telegram.ext import ContextTypes


async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "I don't understand you 😭"
    )