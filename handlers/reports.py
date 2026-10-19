from datetime import date
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from database import get_daily_summary, get_monthly_summary, get_recent_transactions
from keyboards import get_main_keyboard, get_month_picker
from config import CURRENCY

router = Router()

MONTH_NAMES_UZ = {
    1: "Yanvar", 2: "Fevral", 3: "Mart", 4: "Aprel",
    5: "May", 6: "Iyun", 7: "Iyul", 8: "Avgust",
    9: "Sentyabr", 10: "Oktyabr", 11: "Noyabr", 12: "Dekabr"
}

def format_number(val: float) -> str:
    return f"{val:,.0f}".replace(",", " ")

# --- Bugungi hisobot ---
@router.message(F.text == "📊 Bugungi hisobot")
async def daily_report_handler(message: Message):
    today = date.today().isoformat()
    summary = await get_daily_summary(message.from_user.id, today)

    lines = [
        f"📅 **Bugungi hisobot ({today})**",
        "━━━━━━━━━━━━━━━━━━━━",
        f"💰 **Jami daromad:** {format_number(summary['total_income'])} {CURRENCY}",
        f"💸 **Jami xarajat:** {format_number(summary['total_expense'])} {CURRENCY}",
        f"🤝 **Jami avans:** {format_number(summary['total_advance'])} {CURRENCY}",
        f"⚖️ **Kunlik sof qoldiq:** {format_number(summary['net'])} {CURRENCY}",
        "━━━━━━━━━━━━━━━━━━━━"
    ]

    if not summary["items"]:
        lines.append("\n_Bugun hali hech qanday amal kiritilmadi._")
    else:
        lines.append("\n📋 **Bugungi amallar ro'yxati:**")
        for idx, item in enumerate(summary["items"], 1):
            icon = "💰" if item['type'] == 'income' else ("💸" if item['type'] == 'expense' else "🤝")
            cat = f" [{item['category']}]" if item['category'] else ""
            desc = f" - {item['description']}" if item['description'] else ""
            lines.append(f"{idx}. {icon} {format_number(item['amount'])} {CURRENCY}{cat}{desc}")

    await message.answer("\n".join(lines), reply_markup=get_main_keyboard(), parse_mode="Markdown")

# --- Oylik statistika menyusi ---
@router.message(F.text == "📈 Oylik statistika")
async def monthly_stats_menu(message: Message):
    today = date.today()
    kb = get_month_picker(today.year, today.month)
    await message.answer(
        "📈 **Oylik statistika va hisob-kitob:**\n\n"
        "Qaysi oy bo'yicha hisobot ko'rmoqchisiz? Tanlang:",
        reply_markup=kb,
        parse_mode="Markdown"
    )

# --- Oylik statistika ko'rsatish ---
@router.callback_query(F.data.startswith("stat_month_"))
async def show_monthly_stat(callback: CallbackQuery):
    parts = callback.data.split("_")
    year = int(parts[2])
    month = int(parts[3])
    month_name = MONTH_NAMES_UZ.get(month, f"{month}-oy")

    stat = await get_monthly_summary(callback.from_user.id, year, month)

    lines = [
        f"📊 **{month_name} {year} oyi bo'yicha to'liq hisobot**",
        "━━━━━━━━━━━━━━━━━━━━",
        f"💰 **Jami tushum / Daromad:** {format_number(stat['total_income'])} {CURRENCY}",
        f"💸 **Jami xarajatlar:** {format_number(stat['total_expense'])} {CURRENCY}",
        f"🤝 **Olingan avanslar:** {format_number(stat['total_advance'])} {CURRENCY}",
        "━━━━━━━━━━━━━━━━━━━━",
        f"💵 **Sof foyda (Daromad - Xarajat):** {format_number(stat['net'])} {CURRENCY}",
        f"💼 **Ishxonadan qolgan haq (Daromad - Avans):** {format_number(stat['net_with_advance'])} {CURRENCY}",
        f"🔢 **Jami qayd etilgan amallar soni:** {stat['count']} ta",
        "━━━━━━━━━━━━━━━━━━━━"
    ]

    # Category breakdown
    if stat["expense_by_cat"]:
        lines.append("\n🏷 **Xarajatlar toifalar bo'yicha:**")
        total_exp = stat['total_expense'] or 1.0
        for cat in stat["expense_by_cat"]:
            amount = cat['cat_sum']
            pct = (amount / total_exp) * 100
            name = cat['category'] or 'Boshqa'
            lines.append(f"• {name}: **{format_number(amount)} {CURRENCY}** ({pct:.1f}%)")

    # Daily summary highlights
    if stat["daily_breakdown"]:
        lines.append("\n🗓 **Kunlik faollik (oxirgi kunlar):**")
        for day in stat["daily_breakdown"][-7:]: # show last 7 active days
            lines.append(
                f"• {day['date']}: "
                f"+{format_number(day['day_income'])} | "
                f"-{format_number(day['day_expense'])} | "
                f"avans: {format_number(day['day_advance'])}"
            )

    await callback.message.edit_text("\n".join(lines), parse_mode="Markdown")
    await callback.answer()

# --- Oxirgi amallar ---
@router.message(F.text == "📜 Oxirgi amallar")
async def recent_transactions_handler(message: Message):
    items = await get_recent_transactions(message.from_user.id, limit=10)
    if not items:
        await message.answer("📭 Hozircha birorta ham amal qayd etilmagan.", reply_markup=get_main_keyboard())
        return

    lines = ["📜 **Oxirgi 10 ta amallar tarixi:**\n"]
    for idx, item in enumerate(items, 1):
        icon = "💰" if item['type'] == 'income' else ("💸" if item['type'] == 'expense' else "🤝")
        type_str = "Daromad" if item['type'] == 'income' else ("Xarajat" if item['type'] == 'expense' else "Avans")
        cat = f" [{item['category']}]" if item['category'] else ""
        desc = f" ({item['description']})" if item['description'] else ""
        date_str = item['date']
        lines.append(f"{idx}. {icon} **{format_number(item['amount'])} {CURRENCY}** — {type_str}{cat}{desc}\n   🗓 Sana: `{date_str}`")

    await message.answer("\n".join(lines), reply_markup=get_main_keyboard(), parse_mode="Markdown")
