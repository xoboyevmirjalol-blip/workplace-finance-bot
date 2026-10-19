from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard() -> ReplyKeyboardMarkup:
    kb = [
        [
            KeyboardButton(text="💰 Daromad qo'shish"),
            KeyboardButton(text="💸 Xarajat qo'shish")
        ],
        [
            KeyboardButton(text="🤝 Avans qo'shish"),
            KeyboardButton(text="📊 Bugungi hisobot")
        ],
        [
            KeyboardButton(text="📈 Oylik statistika"),
            KeyboardButton(text="📜 Oxirgi amallar")
        ],
        [
            KeyboardButton(text="📥 Excel hisobot (.xlsx)"),
            KeyboardButton(text="❌ Oxirgisini o'chirish")
        ],
        [
            KeyboardButton(text="ℹ️ Qo'llanma / Yordam")
        ]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🚫 Bekor qilish")]],
        resize_keyboard=True
    )

def get_income_categories() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="💼 Kunlik ish haqi", callback_data="cat_inc_Kunlik ish haqi")],
        [InlineKeyboardButton(text="🎁 Bonus / Mukofot", callback_data="cat_inc_Bonus/Mukofot")],
        [InlineKeyboardButton(text="⚡️ Qo'shimcha ish (Xaltur)", callback_data="cat_inc_Qo'shimcha ish")],
        [InlineKeyboardButton(text="💵 Boshqa daromad", callback_data="cat_inc_Boshqa daromad")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_expense_categories() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="🍱 Tushlik / Ovqat", callback_data="cat_exp_Tushlik/Ovqat"),
            InlineKeyboardButton(text="🚖 Yo'l kira / Benzin", callback_data="cat_exp_Yo'l kira")
        ],
        [
            InlineKeyboardButton(text="☕️ Kofe / Choy / Suv", callback_data="cat_exp_Choy-chaqa"),
            InlineKeyboardButton(text="🛠 Ish uchun sarf", callback_data="cat_exp_Ish uchun")
        ],
        [
            InlineKeyboardButton(text="📱 Telefon / Internet", callback_data="cat_exp_Aloqa"),
            InlineKeyboardButton(text="📦 Boshqa xarajat", callback_data="cat_exp_Boshqa")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_advance_categories() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="🤝 Ishxonadan naqd avans", callback_data="cat_adv_Naqd avans")],
        [InlineKeyboardButton(text="💳 Plastik kartaga avans", callback_data="cat_adv_Plastik avans")],
        [InlineKeyboardButton(text="🏢 Rahbariyatdan qarz/avans", callback_data="cat_adv_Rahbariyatdan")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_month_picker(current_year: int, current_month: int) -> InlineKeyboardMarkup:
    months_uz = [
        "Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun",
        "Iyul", "Avgust", "Sentyabr", "Oktyabr", "Noyabr", "Dekabr"
    ]
    
    # Show current month, previous month, and month before that
    buttons = []
    for offset in range(0, 3):
        m = current_month - offset
        y = current_year
        if m <= 0:
            m += 12
            y -= 1
        label = f"📅 {months_uz[m-1]} {y}"
        if offset == 0:
            label += " (Joriy oy)"
        buttons.append([InlineKeyboardButton(text=label, callback_data=f"stat_month_{y}_{m}")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_export_month_picker(current_year: int, current_month: int) -> InlineKeyboardMarkup:
    months_uz = [
        "Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun",
        "Iyul", "Avgust", "Sentyabr", "Oktyabr", "Noyabr", "Dekabr"
    ]
    buttons = []
    for offset in range(0, 3):
        m = current_month - offset
        y = current_year
        if m <= 0:
            m += 12
            y -= 1
        label = f"📊 {months_uz[m-1]} {y} (.xlsx)"
        buttons.append([InlineKeyboardButton(text=label, callback_data=f"export_month_{y}_{m}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
