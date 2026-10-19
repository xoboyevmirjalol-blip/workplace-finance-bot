from aiogram import Router, F, Bot
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, MenuButtonWebApp, WebAppInfo
from aiogram.filters import CommandStart, Command
from database import register_user
from keyboards import get_main_keyboard
import config

router = Router()

def get_webapp_inline_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📱 Hisob-kitob ilovasini ochish",
                web_app=WebAppInfo(url=config.WEBAPP_URL)
            )
        ]
    ])

HELP_TEXT = (
    "💼 **Ishxona Hisob-Kitob Mini App Boti**ga xush kelibsiz!\n\n"
    "Bu bot ishxonangizdagi daromad, xarajat va avanslaringizni zamonaviy **Mini App oynasi**da hisoblab boradi:\n"
    "• 💰 **Kunlik daromadlar** (kunlik ish haqi, tushum, bonuslar)\n"
    "• 💸 **Kunlik xarajatlar** (tushlik, yo'l kira, choy-chaqa)\n"
    "• 🤝 **Ishxonadan olingan avanslar**\n"
    "• 📊 **1 Oylik statistika & yakuniy hisob-kitob**\n"
    "• 📥 **Excel (.xlsx) formatda yuklab olish**\n\n"
    "👇 **Ilovani ochish uchun pastdagi tugmani bosing:**"
)

@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot):
    user = message.from_user
    await register_user(user.id, user.username, user.first_name)
    
    # Set chat menu button (pastdagi 'Menu' tugmasi o'rnida mini app tugmasi)
    try:
        await bot.set_chat_menu_button(
            chat_id=message.chat.id,
            menu_button=MenuButtonWebApp(
                text="💼 Hisob-kitob",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )
        )
    except Exception:
        pass

    await message.answer(
        f"Assalomu alaykum, {user.first_name or 'qadrdon'}!\n\n" + HELP_TEXT,
        reply_markup=get_webapp_inline_keyboard(),
        parse_mode="Markdown"
    )

@router.message(Command("help"))
@router.message(F.text == "ℹ️ Qo'llanma / Yordam")
async def cmd_help(message: Message):
    await message.answer(
        HELP_TEXT,
        reply_markup=get_webapp_inline_keyboard(),
        parse_mode="Markdown"
    )
