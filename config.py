import os
from pathlib import Path

class Config:
    # Bot Settings
    BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
    PUBLIC_MODE = True
    MAX_DOWNLOADS_PER_USER = 5  # Rate limiting
    
    # Paths
    BASE_DIR = Path(__file__).parent
    COOKIES_PATH = BASE_DIR / "cookies.txt"
    DOWNLOAD_DIR = BASE_DIR / "downloads"
    TEMP_DIR = BASE_DIR / "temp"
    
    # Admin Controls
    ADMINS = [123456789]  # Admin Telegram IDs
    AUTHORIZED_USERS = ADMINS.copy() if not PUBLIC_MODE else []
