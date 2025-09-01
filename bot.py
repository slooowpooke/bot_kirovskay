
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Read tokens from environment variables (set these in Render)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
MANAGER_CHAT_ID = os.getenv("MANAGER_CHAT_ID")

# Validate environment variables
if not TELEGRAM_TOKEN:
    raise RuntimeError("Environment variable TELEGRAM_TOKEN is not set.")
if not MANAGER_CHAT_ID:
    raise RuntimeError("Environment variable MANAGER_CHAT_ID is not set.")

# Conversation states
CONSENT, WAIT_VIDEO = range(2)

# /start: greeting and policy consent
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Согласен ✅", "Не согласен ❌"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(
        "👋 Привет! Перед началом необходимо согласиться с политикой обработки данных. "
        "Нажмите кнопку ниже 👇",
        reply_markup=reply_markup
    )
    return CONSENT

# Handle consent
async def consent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Согласен ✅":
        await update.message.reply_text("Отлично! Пришлите, пожалуйста, видео 🎥 (можно как видео или как файл)")
        return WAIT_VIDEO
    else:
        await update.message.reply_text("Вы не согласились с политикой ❌. Диалог завершён.")
        return ConversationHandler.END

# Wait for video and forward to manager
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Accept both native videos and documents that are videos
    video = update.message.video
    document = update.message.document

    # Prefer native video
    file_id = None
    if video:
        file_id = video.file_id
    elif document and document.mime_type and document.mime_type.startswith("video/"):
        file_id = document.file_id

    if file_id:
        # Notify and forward to manager chat
        try:
            await context.bot.send_message(MANAGER_CHAT_ID, f"📩 Новое видео от @{update.effective_user.username or update.effective_user.first_name}")
            # send_video works with file_id
            await context.bot.send_video(MANAGER_CHAT_ID, file_id)
        except Exception as e:
            # If sending as video fails (size/codec), try as document
            try:
                await context.bot.send_document(MANAGER_CHAT_ID, file_id)
            except Exception as e2:
                await update.message.reply_text("Произошла ошибка при пересылке видео менеджеру. Попробуйте ещё раз позже.")
                return ConversationHandler.END

        await update.message.reply_text("Спасибо! Видео получено ✅. Менеджер свяжется с вами.")
        return ConversationHandler.END

    await update.message.reply_text("Пожалуйста, отправьте именно видео (как видео или файл) 🎥")
    return WAIT_VIDEO

# /cancel: abort conversation
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Диалог завершён ❌")
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CONSENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, consent)],
            WAIT_VIDEO: [
                MessageHandler(filters.VIDEO, handle_video),
                MessageHandler(filters.Document.VIDEO, handle_video)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
