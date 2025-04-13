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
from database import Database

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class MusicBot:
    def __init__(self):
        self.app = Application.builder().token(Config.BOT_TOKEN).build()
        self.downloader = Downloader()
        self.db = Database()
        self.setup_handlers()

    def setup_handlers(self):
        handlers = [
            CommandHandler("start", self.start),
            CommandHandler("auth", self.auth_user),
            CommandHandler("stats", self.stats),
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_link)
        ]
        for handler in handlers:
            self.app.add_handler(handler)

    async def start(self, update: Update, context: CallbackContext):
        user = update.effective_user
        await update.message.reply_markdown_v2(
            f"🎵 **Apple Music Download Bot**\n\n"
            f"Send me any Apple Music link!\n"
            f"`Public Mode: {'✅ ON' if Config.PUBLIC_MODE else '❌ OFF'}`"
        )

    async def auth_user(self, update: Update, context: CallbackContext):
        user = update.effective_user
        if user.id not in Config.ADMINS:
            return
        
        try:
            target_id = int(context.args[0])
            Config.AUTHORIZED_USERS.append(target_id)
            await update.message.reply_html(f"✅ Authorized user: <code>{target_id}</code>")
        except (IndexError, ValueError):
            await update.message.reply_html("⚠️ Usage: /auth <user_id>")

    async def handle_link(self, update: Update, context: CallbackContext):
        user = update.effective_user
        url = update.message.text
        
        # Authorization check
        if not Config.PUBLIC_MODE and user.id not in Config.AUTHORIZED_USERS:
            await update.message.reply_html("⛔️ You're not authorized!")
            return
        
        # Rate limiting
        if self._check_rate_limit(user.id):
            await update.message.reply_html("⚠️ Daily download limit reached!")
            return

        try:
            status_msg = await update.message.reply_text("🔍 Processing your request...")
            
            # Download process
            file_path = await asyncio.to_thread(
                self.downloader.process,
                url,
                user.id
            )
            
            # Log download
            self.db.log_download(user.id)
            
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

    def _check_rate_limit(self, user_id: int) -> bool:
        with closing(self.db.conn.cursor()) as c:
            c.execute('SELECT downloads FROM users WHERE user_id=?', (user_id,))
            result = c.fetchone()
            return result and result[0] >= Config.MAX_DOWNLOADS_PER_USER

    async def stats(self, update: Update, context: CallbackContext):
        if update.effective_user.id not in Config.ADMINS:
            return
        
        total_users, total_downloads = self.db.get_stats()
        stats_msg = (
            f"📊 Bot Statistics\n\n"
            f"👥 Total Users: {total_users or 0}\n"
            f"📥 Total Downloads: {total_downloads or 0}"
        )
        await update.message.reply_text(stats_msg)

    def run(self):
        Config.DOWNLOAD_DIR.mkdir(exist_ok=True, parents=True)
        Config.TEMP_DIR.mkdir(exist_ok=True, parents=True)
        self.app.run_polling()

if __name__ == "__main__":
    bot = MusicBot()
    bot.run()
