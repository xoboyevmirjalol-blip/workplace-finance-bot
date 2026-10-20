from aiogram import Router, F, Bot
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, MenuButtonWebApp, WebAppInfo
from aiogram.filters import CommandStart, Command
from database import register_user
from keyboards import get_main_keyboard
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

HELP_TEXT = (
    "💼 **Ishxona Hisob-Kitob Boti**ga xush kelibsiz!\n\n"
    "Bu bot ishxonangizdagi daromad, xarajat va avanslaringizni aniq hisoblab boradi:\n"
    "• 💰 **Kunlik daromadlar** (kunlik ish haqi, tushum, bonuslar)\n"
    "• 💸 **Kunlik xarajatlar** (tushlik, yo'l kira, choy-chaqa)\n"
    "• 🤝 **Ishxonadan olingan avanslar**\n"
    "• 📊 **1 Oylik statistika & yakuniy hisob-kitob**\n"
    "• 📥 **Excel (.xlsx) formatda yuklab olish**\n\n"
    "Pastdagi menyu tugmalari yoki ilova orqali hisob-kitobingizni boshlashingiz mumkin:"
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
    try:
        if webapp_kb:
            await message.answer(
                f"Assalomu alaykum, {user.first_name or 'qadrdon'}!\n\n" + HELP_TEXT,
                reply_markup=webapp_kb,
                parse_mode="Markdown"
            )
            await message.answer("Yoki pastdagi tugmalardan foydalaning:", reply_markup=get_main_keyboard())
        else:
            await message.answer(
                f"Assalomu alaykum, {user.first_name or 'qadrdon'}!\n\n" + HELP_TEXT,
                reply_markup=get_main_keyboard(),
                parse_mode="Markdown"
            )
    except Exception as e:
        # Har qanday holatda ham oddiy xabar yuborish
        await message.answer(
            f"Assalomu alaykum, {user.first_name or 'qadrdon'}!\n\n" + HELP_TEXT,
            reply_markup=get_main_keyboard()
        )

@router.message(Command("help"))
@router.message(F.text == "ℹ️ Qo'llanma / Yordam")
async def cmd_help(message: Message):
    webapp_kb = get_webapp_inline_keyboard()
    if webapp_kb:
        await message.answer(HELP_TEXT, reply_markup=webapp_kb, parse_mode="Markdown")
    else:
        await message.answer(HELP_TEXT, reply_markup=get_main_keyboard(), parse_mode="Markdown")

