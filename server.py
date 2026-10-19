import io
from datetime import date
from aiohttp import web
from pathlib import Path
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

from database import (
    get_daily_summary,
    get_monthly_summary,
    add_transaction,
    delete_transaction_by_id,
    get_all_monthly_transactions
)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

MONTH_NAMES_UZ = {
    1: "Yanvar", 2: "Fevral", 3: "Mart", 4: "Aprel",
    5: "May", 6: "Iyun", 7: "Iyul", 8: "Avgust",
    9: "Sentyabr", 10: "Oktyabr", 11: "Noyabr", 12: "Dekabr"
}

async def handle_index(request: web.Request):
    return web.FileResponse(STATIC_DIR / "index.html")

async def handle_summary(request: web.Request):
    user_id = int(request.query.get("user_id", 0))
    target_date = request.query.get("date") or date.today().isoformat()
    data = await get_daily_summary(user_id, target_date)
    return web.json_response(data)

async def handle_monthly(request: web.Request):
    user_id = int(request.query.get("user_id", 0))
    today = date.today()
    year = int(request.query.get("year", today.year))
    month = int(request.query.get("month", today.month))
    data = await get_monthly_summary(user_id, year, month)
    return web.json_response(data)

async def handle_add_tx(request: web.Request):
    try:
        body = await request.json()
        user_id = int(body.get("user_id", 0))
        t_type = body.get("type", "expense")
        amount = float(body.get("amount", 0.0))
        category = body.get("category", "")
        description = body.get("description", "")
        custom_date = body.get("date") or date.today().isoformat()

        if amount <= 0:
            return web.json_response({"error": "Noto'g'ri summa"}, status=400)

        tx_id = await add_transaction(user_id, t_type, amount, category, description, custom_date)
        return web.json_response({"success": True, "id": tx_id})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

async def handle_delete_tx(request: web.Request):
    user_id = int(request.query.get("user_id", 0))
    trans_id = int(request.match_info.get("id", 0))
    success = await delete_transaction_by_id(user_id, trans_id)
    return web.json_response({"success": success})

async def handle_export(request: web.Request):
    user_id = int(request.query.get("user_id", 0))
    today = date.today()
    year = int(request.query.get("year", today.year))
    month = int(request.query.get("month", today.month))
    month_name = MONTH_NAMES_UZ.get(month, f"{month}-oy")

    stat = await get_monthly_summary(user_id, year, month)
    items = await get_all_monthly_transactions(user_id, year, month)

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

    ws.merge_cells("A1:F1")
    ws["A1"] = f"HISOB-KITOB HISOBOTI: {month_name.upper()} {year}"
    ws["A1"].font = title_font
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 30

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

    table_start_row = 11
    headers = ["№", "Sana", "Turi", "Summa (so'm)", "Kategoriya", "Izoh / Tafsilot"]
    for col_idx, h_text in enumerate(headers, start=1):
        cell = ws.cell(row=table_start_row, column=col_idx, value=h_text)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border
    ws.row_dimensions[table_start_row].height = 24

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
            if col_idx in [1, 2, 3]:
                cell.alignment = Alignment(horizontal="center")
            elif col_idx == 4:
                cell.number_format = '#,##0'
                cell.alignment = Alignment(horizontal="right")
            else:
                cell.alignment = Alignment(horizontal="left")

        current_row += 1

    col_widths = {1: 6, 2: 14, 3: 14, 4: 18, 5: 22, 6: 35}
    for col_idx, width in col_widths.items():
        col_letter = openpyxl.utils.get_column_letter(col_idx)
        ws.column_dimensions[col_letter].width = width

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    filename = f"Hisobot_{month_name}_{year}.xlsx"
    return web.Response(
        body=output.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

def create_web_app() -> web.Application:
    app = web.Application()
    app.router.add_get("/", handle_index)
    app.router.add_static("/static", path=STATIC_DIR, name="static")
    app.router.add_get("/api/summary", handle_summary)
    app.router.add_get("/api/monthly", handle_monthly)
    app.router.add_post("/api/transaction", handle_add_tx)
    app.router.add_delete("/api/transaction/{id}", handle_delete_tx)
    app.router.add_get("/api/export", handle_export)
    return app
