import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from database import init_db
from handlers import start, transactions, reports, export

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("finance_bot")

async def main():
    if not BOT_TOKEN or "YOUR_" in BOT_TOKEN:
        logger.error("BOT_TOKEN noto'g'ri yoki ko'rsatilmagan! .env faylni tekshiring.")
        return

    logger.info("Ma'lumotlar bazasi initsializatsiya qilinmoqda...")
    await init_db()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # Routers
    dp.include_router(start.router)
    dp.include_router(transactions.router)
    dp.include_router(reports.router)
    dp.include_router(export.router)

    # Delete existing webhook if any
    await bot.delete_webhook(drop_pending_updates=True)

    bot_info = await bot.get_me()
    logger.info(f"Bot ishga tushdi: @{bot_info.username} (ID: {bot_info.id})")
    print(f"\n==========================================")
    print(f"🚀 Telegram Bot faol ishlamoqda: @{bot_info.username}")
    print(f"==========================================\n")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
