import asyncio
import logging
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import MenuButtonWebApp, WebAppInfo

import config
from database import init_db
from server import create_web_app
from tunnel import start_tunnel
from handlers import start, transactions, reports, export

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("finance_bot")

async def main():
    if not config.BOT_TOKEN or "YOUR_" in config.BOT_TOKEN:
        logger.error("BOT_TOKEN noto'g'ri yoki ko'rsatilmagan! .env faylni tekshiring.")
        return

    logger.info("Ma'lumotlar bazasi initsializatsiya qilinmoqda...")
    await init_db()

    # 1. Start Aiohttp Web Server
    logger.info(f"Web server ishga tushirilmoqda (port {config.PORT})...")
    app = create_web_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", config.PORT)
    await site.start()
    logger.info(f"Web server faol: http://localhost:{config.PORT}")

    # 2. Check / Setup Public HTTPS Tunnel if running locally without Railway
    if not config.WEBAPP_URL.startswith("https://"):
        logger.info("Lokal rejim aniqlandi, Telegram Mini App uchun HTTPS tunnel ishga tushirilmoqda...")
        tunnel_url = start_tunnel(config.PORT)
        if tunnel_url:
            config.WEBAPP_URL = tunnel_url
            logger.info(f"Cloudflare HTTPS Tunnel yaratildi: {config.WEBAPP_URL}")
        else:
            logger.warning("Tunnel ishga tushmadi. WEBAPP_URL: " + config.WEBAPP_URL)
    else:
        logger.info(f"Mini App HTTPS URL: {config.WEBAPP_URL}")

    # 3. Setup Telegram Bot
    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(transactions.router)
    dp.include_router(reports.router)
    dp.include_router(export.router)

    await bot.delete_webhook(drop_pending_updates=True)

    # 4. Set Chat Menu Button to open Mini App directly from Telegram
    try:
        await bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(
                text="💼 Hisob-kitob",
                web_app=WebAppInfo(url=config.WEBAPP_URL)
            )
        )
        logger.info("Telegram Chat Menu tugmasi Mini App'ga muvaffaqiyatli ulandi.")
    except Exception as e:
        logger.warning(f"Chat Menu tugmasini sozlashda ogohlantirish: {e}")

    bot_info = await bot.get_me()
    print("\n" + "=" * 50)
    print(f"🚀 Telegram Bot: @{bot_info.username}")
    print(f"📱 Telegram Mini App URL: {config.WEBAPP_URL}")
    print("=" * 50 + "\n")

    try:
        await dp.start_polling(bot)
    finally:
        await runner.cleanup()
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
