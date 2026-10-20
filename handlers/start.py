from aiogram import Router, F, Bot
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, MenuButtonWebApp, WebAppInfo, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command
from database import register_user
import config

router = Router()

def get_webapp_inline_keyboard() -> InlineKeyboardMarkup | None:
    if config.WEBAPP_URL and config.WEBAPP_URL.startswith("https://"):
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📱 Hisob-kitob ilovasini ochish",
                    web_app=WebAppInfo(url=config.WEBAPP_URL)
                )
            ]
        ])
    return None

WELCOME_TEXT = (
    "💼 **Ishxona Hisob-Kitob Ilovasi**ga xush kelibsiz!\n\n"
    "Barcha hisob-kitoblaringiz (🔨 **Yasalgan buyumlar**, 🔧 **Montajlar**, 💰 **Daromad**, 💸 **Xarajat** va 🤝 **Avanslar**) qulay Mini App ilovasi orqali yuritiladi.\n\n"
    "👇 **Ilovani ochish uchun pastdagi tugmani bosing:**"
)

@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot):
    user = message.from_user
    await register_user(user.id, user.username, user.first_name)
    
    # Agar HTTPS domen mavjud bo'lsa, chat menyu tugmasini Mini App qilib o'rnatamiz
    if config.WEBAPP_URL and config.WEBAPP_URL.startswith("https://"):
        try:
            await bot.set_chat_menu_button(
                chat_id=message.chat.id,
                menu_button=MenuButtonWebApp(
                    text="💼 Hisob-kitob",
                    web_app=WebAppInfo(url=config.WEBAPP_URL)
                )
            )
        except Exception:
            pass

    webapp_kb = get_webapp_inline_keyboard()
    # Pastdagi barcha ortiqcha tugmalarni olib tashlaymiz (ReplyKeyboardRemove)
    if webapp_kb:
        await message.answer(
            WELCOME_TEXT,
            reply_markup=webapp_kb,
            parse_mode="Markdown"
        )
    else:
        await message.answer(
            WELCOME_TEXT,
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="Markdown"
        )

@router.message(Command("help"))
async def cmd_help(message: Message):
    webapp_kb = get_webapp_inline_keyboard()
    await message.answer(
        WELCOME_TEXT,
        reply_markup=webapp_kb or ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )
