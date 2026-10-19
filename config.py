import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN", "8994052815:AAHt_peOECP0DbZ0SFWz2o4sUMEbp0YaykQ")
DB_NAME = os.getenv("DB_NAME", str(BASE_DIR / "finance.db"))
CURRENCY = os.getenv("CURRENCY", "so'm")
PORT = int(os.getenv("PORT", 8080))

# Railway automatically sets RAILWAY_PUBLIC_DOMAIN (e.g. app.up.railway.app)
RAILWAY_DOMAIN = os.getenv("RAILWAY_PUBLIC_DOMAIN", "")
if os.getenv("WEBAPP_URL"):
    WEBAPP_URL = os.getenv("WEBAPP_URL")
elif RAILWAY_DOMAIN:
    WEBAPP_URL = f"https://{RAILWAY_DOMAIN}"
else:
    WEBAPP_URL = f"http://localhost:{PORT}"
