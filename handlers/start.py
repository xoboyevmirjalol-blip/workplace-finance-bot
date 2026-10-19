from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from database import register_user
from keyboards import get_main_keyboard

router = Router()

HELP_TEXT = (
    "💼 **Ishxona Hisob-Kitob Boti**ga xush kelibsiz!\n\n"
    "Bu bot ishxonangizdagi barcha moliyaviy amallaringizni aniq va xatosiz hisoblab borishga yordam beradi:\n"
    "• 💰 **Kunlik daromadlar** (kunlik ish haqi, tushum, bonuslar)\n"
    "• 💸 **Kunlik xarajatlar** (tushlik, yo'l kira, ishga sarflangan pullar)\n"
    "• 🤝 **Ishxonadan olingan avanslar**\n"
    "• 📊 **Kunlik va 1 oylik to'liq hisob-kitob & statistika**\n"
    "• 📥 **Excel (.xlsx) formatda yuklab olish**\n\n"
    "⚡️ **Foydalanish usullari:**\n"
    "1️⃣ **Tugmalar orqali:** Pastdagi menyu tugmalaridan birini bosing va bot yo'riqnomasiga amal qiling.\n"
    "2️⃣ **Tezkor matn orqali:** Istalgan vaqtda quyidagicha yozib yuborishingiz mumkin:\n"
    "   • `+ 150000 kunlik ish haqi` (daromad)\n"
    "   • `- 35000 tushlik osh` (xarajat)\n"
    "   • `avans 500000 rahbardan` (avans)\n"
    "   *(Summalarni `50k`, `100 000`, `25ming` ko'rinishida ham yoza olasiz)*"
)

@router.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user
    await register_user(user.id, user.username, user.first_name)
    await message.answer(
        f"Assalomu alaykum, {user.first_name or 'qadrdon'}!\n\n" + HELP_TEXT,
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )

@router.message(Command("help"))
@router.message(F.text == "ℹ️ Qo'llanma / Yordam")
async def cmd_help(message: Message):
    await message.answer(
        HELP_TEXT,
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )
