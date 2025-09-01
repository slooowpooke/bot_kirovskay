import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# --- Настройки ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
MANAGER_CHAT_ID = os.getenv("MANAGER_CHAT_ID")

if not TELEGRAM_TOKEN:
    raise RuntimeError("Не задан TELEGRAM_TOKEN")
if not MANAGER_CHAT_ID:
    raise RuntimeError("Не задан MANAGER_CHAT_ID")

# --- Health-сервер для Render ---
class _HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def _run_health_server():
    port = int(os.getenv("PORT", "8000"))
    server = HTTPServer(("0.0.0.0", port), _HealthHandler)
    server.serve_forever()

# --- Состояния бота ---
CONSENT, WAIT_VIDEO = range(2)

# --- Обработчики команд ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Согласен ✅", "Не согласен ❌"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(
        "👋 Привет! Перед началом необходимо согласиться с политикой обработки данных. "
        "Нажмите кнопку ниже 👇",
        reply_markup=reply_markup
    )
    return CONSENT

async def consent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Согласен ✅":
        await update.message.reply_text("Отлично! Пришлите, пожалуйста, видео 🎥 (можно как видео или файл)")
        return WAIT_VIDEO
    else:
        await update.message.reply_text("Вы не согласились с политикой ❌. Диалог завершён.")
        return ConversationHandler.END

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video = update.message.video
    document = update.message.document

    file_id = None
    if video:
        file_id = video.file_id
    elif document and document.mime_type and document.mime_type.startswith("video/"):
        file_id = document.file_id

    if file_id:
        try:
            await context.bot.send_message(MANAGER_CHAT_ID, f"📩 Новое видео от @{update.effective_user.username or update.effective_user.first_name}")
            await context.bot.send_video(MANAGER_CHAT_ID, file_id)
        except:
            await context.bot.send_document(MANAGER_CHAT_ID, file_id)

        await update.message.reply_text("Спасибо! Видео получено ✅. Менеджер свяжется с вами.")
        return ConversationHandler.END

    await update.message.reply_text("Пожалуйста, отправьте именно видео 🎥")
    return WAIT_VIDEO

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Диалог завершён ❌")
    return ConversationHandler.END

# --- Запуск ---
def main():
    # Запускаем Health-сервер
    threading.Thread(target=_run_health_server, daemon=True).start()

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
