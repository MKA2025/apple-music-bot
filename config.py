import os
from pathlib import Path

class Config:
    # Bot Settings
    BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
    PUBLIC_MODE = True  # True = Anyone can use, False = Auth only
    
    # Path Configurations
    BASE_DIR = Path(__file__).parent
    COOKIES_PATH = BASE_DIR / "cookies.txt"
    DOWNLOAD_DIR = BASE_DIR / "downloads"
    TEMP_DIR = BASE_DIR / "temp"
    
    # Rate Limits
    MAX_CONCURRENT_DOWNLOADS = 2
    REQUEST_COOLDOWN = 60 * 60  # 1 hour
    
    # Admin Controls
    ADMINS = [123456789]  # Admin Telegram IDs
    AUTHORIZED_USERS = ADMINS.copy() if not PUBLIC_MODE else []
