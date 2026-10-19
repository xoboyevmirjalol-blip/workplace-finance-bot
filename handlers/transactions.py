import re
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import add_transaction, delete_last_transaction, get_daily_summary
from keyboards import (
    get_main_keyboard,
    get_cancel_keyboard,
    get_income_categories,
    get_expense_categories,
    get_advance_categories
)
from config import CURRENCY

router = Router()

class TransactionFSM(StatesGroup):
    waiting_for_amount = State()
    waiting_for_category = State()
    waiting_for_description = State()

def parse_amount(text: str) -> float | None:
    """Parses numeric amounts supporting 'k', 'ming', 'mln', and spaced numbers."""
    cleaned = text.strip().lower().replace(" ", "").replace(",", ".")
    multiplier = 1.0
    if cleaned.endswith("k") or cleaned.endswith("к"):
        multiplier = 1_000.0
        cleaned = cleaned[:-1]
    elif cleaned.endswith("ming"):
        multiplier = 1_000.0
        cleaned = cleaned[:-4]
    elif cleaned.endswith("m") or cleaned.endswith("mln"):
        multiplier = 1_000_000.0
        cleaned = cleaned.replace("mln", "").replace("m", "")
    
    try:
        val = float(cleaned)
        if val <= 0:
            return None
        return round(val * multiplier, 2)
    except ValueError:
        return None

def format_number(val: float) -> str:
    """Formats 150000 to 150 000."""
    return f"{val:,.0f}".replace(",", " ")

# --- Cancel handler ---
@router.message(F.text == "🚫 Bekor qilish")
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Amal bekor qilindi.", reply_markup=get_main_keyboard())

# --- Delete last transaction ---
@router.message(F.text == "❌ Oxirgisini o'chirish")
async def delete_last_handler(message: Message):
    deleted = await delete_last_transaction(message.from_user.id)
    if not deleted:
        await message.answer("⚠️ O'chirish uchun oxirgi amal topilmadi.", reply_markup=get_main_keyboard())
        return

    type_name = "💰 Daromad" if deleted['type'] == 'income' else ("💸 Xarajat" if deleted['type'] == 'expense' else "🤝 Avans")
    await message.answer(
        f"🗑 **Oxirgi amal bekor qilindi va o'chirildi:**\n\n"
        f"• Turi: {type_name}\n"
        f"• Summa: **{format_number(deleted['amount'])} {CURRENCY}**\n"
        f"• Kategoriya: {deleted['category'] or 'Ko\\'rsatilmagan'}\n"
        f"• Izoh: {deleted['description'] or '-'}\n"
        f"• Sana: {deleted['date']}",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )

# --- Button Initiated Flow ---
@router.message(F.text == "💰 Daromad qo'shish")
async def start_income(message: Message, state: FSMContext):
    await state.set_state(TransactionFSM.waiting_for_amount)
    await state.update_data(trans_type="income")
    await message.answer(
        "💰 **Daromad summasini kiriting:**\n\n"
        "Masalan: `150000`, `150 000`, `150k` yoki `1.5m`",
        reply_markup=get_cancel_keyboard(),
        parse_mode="Markdown"
    )

@router.message(F.text == "💸 Xarajat qo'shish")
async def start_expense(message: Message, state: FSMContext):
    await state.set_state(TransactionFSM.waiting_for_amount)
    await state.update_data(trans_type="expense")
    await message.answer(
        "💸 **Xarajat summasini kiriting:**\n\n"
        "Masalan: `35000`, `35k`, `50 000`",
        reply_markup=get_cancel_keyboard(),
        parse_mode="Markdown"
    )

@router.message(F.text == "🤝 Avans qo'shish")
async def start_advance(message: Message, state: FSMContext):
    await state.set_state(TransactionFSM.waiting_for_amount)
    await state.update_data(trans_type="advance")
    await message.answer(
        "🤝 **Ishxonadan olingan avans summasini kiriting:**\n\n"
        "Masalan: `500000`, `500k`, `1m`",
        reply_markup=get_cancel_keyboard(),
        parse_mode="Markdown"
    )

# --- State: waiting_for_amount ---
@router.message(TransactionFSM.waiting_for_amount)
async def process_amount(message: Message, state: FSMContext):
    amount = parse_amount(message.text)
    if not amount:
        await message.answer(
            "⚠️ Noto'g'ri summa kiritildi. Iltimos, faqat son kiriting (masalan: `50000` yoki `50k`):",
            reply_markup=get_cancel_keyboard(),
            parse_mode="Markdown"
        )
        return

    data = await state.get_data()
    trans_type = data.get("trans_type", "expense")
    await state.update_data(amount=amount)
    await state.set_state(TransactionFSM.waiting_for_category)

    if trans_type == "income":
        kb = get_income_categories()
        prompt = f"💰 Summa: **{format_number(amount)} {CURRENCY}**\n\nKategoriyani tanlang yoki o'zingiz yozing:"
    elif trans_type == "expense":
        kb = get_expense_categories()
        prompt = f"💸 Summa: **{format_number(amount)} {CURRENCY}**\n\nKategoriyani tanlang yoki o'zingiz yozing:"
    else:
        kb = get_advance_categories()
        prompt = f"🤝 Summa: **{format_number(amount)} {CURRENCY}**\n\nAvans turini tanlang yoki o'zingiz yozing:"

    await message.answer(prompt, reply_markup=kb, parse_mode="Markdown")

# --- State: waiting_for_category (Callback) ---
@router.callback_query(TransactionFSM.waiting_for_category, F.data.startswith("cat_"))
async def process_category_callback(callback: CallbackQuery, state: FSMContext):
    cat_parts = callback.data.split("_", 2)
    category = cat_parts[2] if len(cat_parts) > 2 else "Boshqa"
    await state.update_data(category=category)
    await state.set_state(TransactionFSM.waiting_for_description)
    await callback.message.edit_text(f"Tanlangan toifa: **{category}**", parse_mode="Markdown")
    await callback.message.answer(
        "📝 **Qo'shimcha izoh yozing** (masalan: `Oshxonada osh yedik` yoki `Taksi xarajati`):\n\n"
        "Agar izoh kerak bo'lmasa, shunchaki `yo'q` yoki `0` deb yozing.",
        reply_markup=get_cancel_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

# --- State: waiting_for_category (Text) ---
@router.message(TransactionFSM.waiting_for_category)
async def process_category_text(message: Message, state: FSMContext):
    category = message.text.strip()
    await state.update_data(category=category)
    await state.set_state(TransactionFSM.waiting_for_description)
    await message.answer(
        f"Kategoriya: **{category}** qabul qilindi.\n\n"
        "📝 **Qo'shimcha izoh yozing** (yoki shunchaki `yo'q` deb yuboring):",
        reply_markup=get_cancel_keyboard(),
        parse_mode="Markdown"
    )

# --- State: waiting_for_description ---
@router.message(TransactionFSM.waiting_for_description)
async def process_description(message: Message, state: FSMContext):
    desc = message.text.strip()
    if desc.lower() in ["yo'q", "yoq", "none", "-", "0", "skip", "yo'q."]:
        desc = ""

    data = await state.get_data()
    trans_type = data.get("trans_type", "expense")
    amount = data.get("amount", 0.0)
    category = data.get("category", "Umumiy")

    await add_transaction(
        user_id=message.from_user.id,
        trans_type=trans_type,
        amount=amount,
        category=category,
        description=desc
    )
    await state.clear()

    # Get updated daily summary
    summary = await get_daily_summary(message.from_user.id)
    icon = "💰" if trans_type == "income" else ("💸" if trans_type == "expense" else "🤝")
    type_title = "Daromad" if trans_type == "income" else ("Xarajat" if trans_type == "expense" else "Avans")

    await message.answer(
        f"✅ **{icon} {type_title} muvaffaqiyatli saqlandi!**\n\n"
        f"• Summa: **{format_number(amount)} {CURRENCY}**\n"
        f"• Toifa: {category}\n"
        f"• Izoh: {desc or '-'}\n\n"
        f"📊 **Bugungi holat:**\n"
        f"• 💰 Jami daromad: **{format_number(summary['total_income'])} {CURRENCY}**\n"
        f"• 💸 Jami xarajat: **{format_number(summary['total_expense'])} {CURRENCY}**\n"
        f"• 🤝 Jami avans: **{format_number(summary['total_advance'])} {CURRENCY}**\n"
        f"• ⚖️ Kunlik qoldiq: **{format_number(summary['net'])} {CURRENCY}**",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )

# --- Smart Fast Text Input (e.g., '+ 50000 oylik' or '- 20000 tushlik' or 'avans 300k') ---
@router.message(F.text.regexp(r"^([\+\-]|\bavans\b|\bqarz\b|\bdaromad\b|\bxarajat\b)\s*([0-9\s,\.kKmMmingmln]+)(.*)$", flags=re.IGNORECASE))
async def quick_entry_handler(message: Message):
    match = re.match(r"^([\+\-]|\bavans\b|\bqarz\b|\bdaromad\b|\bxarajat\b)\s*([0-9\s,\.kKmMmingmln]+)(.*)$", message.text.strip(), flags=re.IGNORECASE)
    if not match:
        return

    indicator, amount_str, rest = match.groups()
    amount = parse_amount(amount_str)
    if not amount:
        return

    indicator = indicator.strip().lower()
    if indicator in ["+", "daromad"]:
        trans_type = "income"
        default_cat = "Kunlik ish haqi"
        icon = "💰"
        title = "Daromad"
    elif indicator in ["-", "xarajat"]:
        trans_type = "expense"
        default_cat = "Kundalik xarajat"
        icon = "💸"
        title = "Xarajat"
    else:
        trans_type = "advance"
        default_cat = "Ishxonadan avans"
        icon = "🤝"
        title = "Avans"

    description = rest.strip() if rest else ""
    category = default_cat
    if description:
        # If short description, use it as category or description
        category = description.split()[0].capitalize()

    await add_transaction(
        user_id=message.from_user.id,
        trans_type=trans_type,
        amount=amount,
        category=category,
        description=description
    )

    summary = await get_daily_summary(message.from_user.id)
    await message.answer(
        f"⚡️ **Tezkor kiritish saqlandi ({icon} {title})!**\n\n"
        f"• Summa: **{format_number(amount)} {CURRENCY}**\n"
        f"• Izoh: {description or category}\n\n"
        f"📊 **Bugungi holat:**\n"
        f"• 💰 Daromad: **{format_number(summary['total_income'])} {CURRENCY}**\n"
        f"• 💸 Xarajat: **{format_number(summary['total_expense'])} {CURRENCY}**\n"
        f"• 🤝 Avans: **{format_number(summary['total_advance'])} {CURRENCY}**\n"
        f"• ⚖️ Kunlik qoldiq: **{format_number(summary['net'])} {CURRENCY}**",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )
