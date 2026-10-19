import io
from datetime import date
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from database import get_monthly_summary, get_all_monthly_transactions
from keyboards import get_main_keyboard, get_export_month_picker
from config import CURRENCY

router = Router()

MONTH_NAMES_UZ = {
    1: "Yanvar", 2: "Fevral", 3: "Mart", 4: "Aprel",
    5: "May", 6: "Iyun", 7: "Iyul", 8: "Avgust",
    9: "Sentyabr", 10: "Oktyabr", 11: "Noyabr", 12: "Dekabr"
}

@router.message(F.text == "📥 Excel hisobot (.xlsx)")
async def export_menu_handler(message: Message):
    today = date.today()
    kb = get_export_month_picker(today.year, today.month)
    await message.answer(
        "📥 **Excel formatda hisobot yuklab olish:**\n\n"
        "Qaysi oy ma'lumotlarini `.xlsx` fayl ko'rinishida yuklamoqchisiz? Tanlang:",
        reply_markup=kb,
        parse_mode="Markdown"
    )

@router.callback_query(F.data.startswith("export_month_"))
async def generate_and_send_excel(callback: CallbackQuery):
    parts = callback.data.split("_")
    year = int(parts[2])
    month = int(parts[3])
    month_name = MONTH_NAMES_UZ.get(month, f"{month}-oy")

    await callback.message.edit_text(f"⏳ **{month_name} {year}** oyi bo'yicha Excel hisoboti tayyorlanmoqda...")

    stat = await get_monthly_summary(callback.from_user.id, year, month)
    items = await get_all_monthly_transactions(callback.from_user.id, year, month)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"{month_name} {year}"

    # Styles
    title_font = Font(name="Calibri", size=16, bold=True, color="1F497D")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    bold_font = Font(name="Calibri", size=11, bold=True)
    regular_font = Font(name="Calibri", size=11)
    
    header_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
    summary_fill = PatternFill(start_color="DCE6F1", end_color="DCE6F1", fill_type="solid")
    income_fill = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
    expense_fill = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")
    advance_fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")

    thin_border = Border(
        left=Side(style='thin', color='BFBFBF'),
        right=Side(style='thin', color='BFBFBF'),
        top=Side(style='thin', color='BFBFBF'),
        bottom=Side(style='thin', color='BFBFBF')
    )

    # 1. Title
    ws.merge_cells("A1:F1")
    ws["A1"] = f"HISOB-KITOB HISOBOTI: {month_name.upper()} {year}"
    ws["A1"].font = title_font
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 30

    # 2. Monthly Summary Box
    ws["A3"] = "OYLIK XULOSA"
    ws["A3"].font = bold_font
    ws["B3"] = f"{month_name} {year}"
    ws["B3"].font = bold_font

    summary_rows = [
        ("Jami daromad / tushum:", stat["total_income"]),
        ("Jami xarajatlar:", stat["total_expense"]),
        ("Olingan avanslar:", stat["total_advance"]),
        ("Sof daromad (Daromad - Xarajat):", stat["net"]),
        ("Ishxonadan qolgan haq (Daromad - Avans):", stat["net_with_advance"]),
    ]

    for idx, (label, val) in enumerate(summary_rows, start=4):
        ws[f"A{idx}"] = label
        ws[f"B{idx}"] = val
        ws[f"A{idx}"].font = bold_font
        ws[f"B{idx}"].font = bold_font
        ws[f"A{idx}"].fill = summary_fill
        ws[f"B{idx}"].fill = summary_fill
        ws[f"B{idx}"].number_format = '#,##0'
        ws[f"A{idx}"].border = thin_border
        ws[f"B{idx}"].border = thin_border

    # 3. Table Headers
    table_start_row = 11
    headers = ["№", "Sana", "Turi", "Summa (so'm)", "Kategoriya", "Izoh / Tafsilot"]
    for col_idx, h_text in enumerate(headers, start=1):
        cell = ws.cell(row=table_start_row, column=col_idx, value=h_text)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border
    ws.row_dimensions[table_start_row].height = 24

    # 4. Table Data
    current_row = table_start_row + 1
    for idx, item in enumerate(items, start=1):
        t_type = item['type']
        t_type_name = "Daromad" if t_type == "income" else ("Xarajat" if t_type == "expense" else "Avans")
        row_fill = income_fill if t_type == "income" else (expense_fill if t_type == "expense" else advance_fill)

        row_values = [
            idx,
            item['date'],
            t_type_name,
            item['amount'],
            item['category'] or "-",
            item['description'] or "-"
        ]

        for col_idx, val in enumerate(row_values, start=1):
            cell = ws.cell(row=current_row, column=col_idx, value=val)
            cell.font = regular_font
            cell.border = thin_border
            cell.fill = row_fill
            if col_idx == 1:
                cell.alignment = Alignment(horizontal="center")
            elif col_idx == 2:
                cell.alignment = Alignment(horizontal="center")
            elif col_idx == 3:
                cell.alignment = Alignment(horizontal="center")
            elif col_idx == 4:
                cell.number_format = '#,##0'
                cell.alignment = Alignment(horizontal="right")
            else:
                cell.alignment = Alignment(horizontal="left")

        current_row += 1

    # Auto adjust column widths
    col_widths = {1: 6, 2: 14, 3: 14, 4: 18, 5: 22, 6: 35}
    for col_idx, width in col_widths.items():
        col_letter = openpyxl.utils.get_column_letter(col_idx)
        ws.column_dimensions[col_letter].width = width

    # Save to BytesIO
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    filename = f"Hisobot_{month_name}_{year}.xlsx"
    file_doc = BufferedInputFile(output.read(), filename=filename)

    await callback.message.delete()
    await callback.message.answer_document(
        document=file_doc,
        caption=f"📄 **{month_name} {year}** oyi bo'yicha to'liq hisob-kitob fayli tayyor!\n\n"
                f"• Daromad: **{stat['total_income']:,.0f} {CURRENCY}**\n"
                f"• Xarajat: **{stat['total_expense']:,.0f} {CURRENCY}**\n"
                f"• Avans: **{stat['total_advance']:,.0f} {CURRENCY}**\n"
                f"• Qoldiq haq: **{stat['net_with_advance']:,.0f} {CURRENCY}**",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()
