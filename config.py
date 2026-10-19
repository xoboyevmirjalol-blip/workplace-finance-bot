import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN", "8994052815:AAHt_peOECP0DbZ0SFWz2o4sUMEbp0YaykQ")
DB_NAME = os.getenv("DB_NAME", str(BASE_DIR / "finance.db"))
CURRENCY = os.getenv("CURRENCY", "so'm")
