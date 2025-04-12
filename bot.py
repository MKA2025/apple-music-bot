import logging
import asyncio
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext
)
from config import Config
from downloader import Downloader, DownloadError

# Initialize logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class MusicBot:
    def __init__(self):
        self.app = Application.builder().token(Config.BOT_TOKEN).build()
        self.downloader = Downloader()
        self.active_tasks = {}
        self.setup_handlers()

    def setup_handlers(self):
        handlers = [
            CommandHandler("start", self.start),
            CommandHandler("auth", self.auth_user),
            CommandHandler("stats", self.bot_stats),
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_link),
            MessageHandler(filters.Document.ALL, self.handle_document)
        ]
        for handler in handlers:
            self.app.add_handler(handler)

    async def start(self, update: Update, context: CallbackContext):
        user = update.effective_user
        msg = (
            "🎵 *Apple Music Download Bot*\n\n"
            "Send me any Apple Music song/album link!\n"
            f"Public Mode: {'✅ ON' if Config.PUBLIC_MODE else '❌ OFF'}"
        )
        await update.message.reply_markdown(msg)

    async def auth_user(self, update: Update, context: CallbackContext):
        user = update.effective_user
        if user.id not in Config.ADMINS:
            return
        
        try:
            target_id = int(context.args[0])
            Config.AUTHORIZED_USERS.append(target_id)
            await update.message.reply_html(
                f"✅ Authorized user: <code>{target_id}</code>"
            )
        except (IndexError, ValueError):
            await update.message.reply_html("⚠️ Usage: /auth <user_id>")

    async def handle_link(self, update: Update, context: CallbackContext):
        user = update.effective_user
        url = update.message.text
        
        # Authorization check
        if not Config.PUBLIC_MODE and user.id not in Config.AUTHORIZED_USERS:
            await update.message.reply_html("⛔️ You're not authorized!")
            return

        try:
            status_msg = await update.message.reply_text("🔍 Processing your request...")
            
            # Start download
            file_path = await asyncio.to_thread(
                self.downloader.process,
                url,
                user.id
            )
            
            # Send result
            await update.message.reply_audio(
                audio=open(file_path, 'rb'),
                title=file_path.stem,
                performer="Apple Music",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("Delete", callback_data=f"delete_{file_path.name}")
                ]])
            )
            await status_msg.edit_text("✅ Download completed!")
            
        except DownloadError as e:
            await status_msg.edit_text(f"❌ Error: {str(e)}")
            logger.error(f"Download failed for {user.id}: {str(e)}")

    async def bot_stats(self, update: Update, context: CallbackContext):
        if update.effective_user.id not in Config.ADMINS:
            return
        
        stats = (
            f"👥 Users: {len(Config.AUTHORIZED_USERS)}\n"
            f"💾 Storage: {self.downloader.get_storage_usage()}\n"
            f"🔥 Active Tasks: {len(self.active_tasks)}"
        )
        await update.message.reply_text(stats)

    def run(self):
        Config.DOWNLOAD_DIR.mkdir(exist_ok=True)
        Config.TEMP_DIR.mkdir(exist_ok=True)
        self.app.run_polling()

if __name__ == "__main__":
    bot = MusicBot()
    bot.run()
