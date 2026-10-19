import aiosqlite
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from config import DB_NAME

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                type TEXT NOT NULL, -- 'income', 'expense', 'advance'
                amount REAL NOT NULL,
                category TEXT,
                description TEXT,
                date TEXT NOT NULL, -- 'YYYY-MM-DD'
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        await db.execute("CREATE INDEX IF NOT EXISTS idx_trans_user_date ON transactions(user_id, date);")
        await db.commit()

async def register_user(user_id: int, username: Optional[str], first_name: Optional[str]):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            INSERT INTO users (user_id, username, first_name)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username=excluded.username,
                first_name=excluded.first_name
            """,
            (user_id, username, first_name)
        )
        await db.commit()

async def add_transaction(user_id: int, trans_type: str, amount: float, category: str = "", description: str = "", custom_date: Optional[str] = None) -> int:
    today_str = custom_date or date.today().isoformat()
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            """
            INSERT INTO transactions (user_id, type, amount, category, description, date)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, trans_type, amount, category, description, today_str)
        )
        await db.commit()
        return cursor.lastrowid

async def get_recent_transactions(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """
            SELECT id, type, amount, category, description, date, created_at
            FROM transactions
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (user_id, limit)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def delete_last_transaction(user_id: int) -> Optional[Dict[str, Any]]:
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """
            SELECT id, type, amount, category, description, date
            FROM transactions
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if not row:
                return None
            trans = dict(row)

        await db.execute("DELETE FROM transactions WHERE id = ?", (trans['id'],))
        await db.commit()
        return trans

async def get_daily_summary(user_id: int, date_str: Optional[str] = None) -> Dict[str, Any]:
    target_date = date_str or date.today().isoformat()
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        
        async with db.execute(
            """
            SELECT 
                SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as total_income,
                SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as total_expense,
                SUM(CASE WHEN type = 'advance' THEN amount ELSE 0 END) as total_advance,
                COUNT(id) as count
            FROM transactions
            WHERE user_id = ? AND date = ?
            """,
            (user_id, target_date)
        ) as cursor:
            row = await cursor.fetchone()
            total_income = row['total_income'] or 0.0
            total_expense = row['total_expense'] or 0.0
            total_advance = row['total_advance'] or 0.0
            count = row['count'] or 0

        async with db.execute(
            """
            SELECT id, type, amount, category, description, created_at
            FROM transactions
            WHERE user_id = ? AND date = ?
            ORDER BY id ASC
            """,
            (user_id, target_date)
        ) as cursor:
            items = [dict(r) for r in await cursor.fetchall()]

        return {
            "date": target_date,
            "total_income": total_income,
            "total_expense": total_expense,
            "total_advance": total_advance,
            "net": total_income - total_expense,
            "items": items,
            "count": count
        }

async def get_monthly_summary(user_id: int, year: int, month: int) -> Dict[str, Any]:
    month_prefix = f"{year:04d}-{month:02d}%"
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row

        # General totals
        async with db.execute(
            """
            SELECT 
                SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as total_income,
                SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as total_expense,
                SUM(CASE WHEN type = 'advance' THEN amount ELSE 0 END) as total_advance,
                COUNT(id) as count
            FROM transactions
            WHERE user_id = ? AND date LIKE ?
            """,
            (user_id, month_prefix)
        ) as cursor:
            row = await cursor.fetchone()
            total_income = row['total_income'] or 0.0
            total_expense = row['total_expense'] or 0.0
            total_advance = row['total_advance'] or 0.0
            count = row['count'] or 0

        # Category breakdown for expenses
        async with db.execute(
            """
            SELECT category, SUM(amount) as cat_sum
            FROM transactions
            WHERE user_id = ? AND type = 'expense' AND date LIKE ?
            GROUP BY category
            ORDER BY cat_sum DESC
            """,
            (user_id, month_prefix)
        ) as cursor:
            expense_by_cat = [dict(r) for r in await cursor.fetchall()]

        # Daily breakdown
        async with db.execute(
            """
            SELECT 
                date,
                SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as day_income,
                SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as day_expense,
                SUM(CASE WHEN type = 'advance' THEN amount ELSE 0 END) as day_advance
            FROM transactions
            WHERE user_id = ? AND date LIKE ?
            GROUP BY date
            ORDER BY date ASC
            """,
            (user_id, month_prefix)
        ) as cursor:
            daily_breakdown = [dict(r) for r in await cursor.fetchall()]

        return {
            "year": year,
            "month": month,
            "total_income": total_income,
            "total_expense": total_expense,
            "total_advance": total_advance,
            "net": total_income - total_expense,
            "net_with_advance": total_income - total_advance, # Agar maoshdan avans hisoblansa
            "count": count,
            "expense_by_cat": expense_by_cat,
            "daily_breakdown": daily_breakdown
        }

async def get_all_monthly_transactions(user_id: int, year: int, month: int) -> List[Dict[str, Any]]:
    month_prefix = f"{year:04d}-{month:02d}%"
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """
            SELECT id, type, amount, category, description, date, created_at
            FROM transactions
            WHERE user_id = ? AND date LIKE ?
            ORDER BY date ASC, id ASC
            """,
            (user_id, month_prefix)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]
