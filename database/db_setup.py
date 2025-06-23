# database/db_setup.py

import sqlite3
from pathlib import Path

DB_PATH = Path("data/dairy_management.db")

def setup_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create farmers table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS farmers (
        account_no INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        phone TEXT,
        balance REAL DEFAULT 0
    )
    """)

    # Create products table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL
    )
    """)

    # Create transactions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_no INTEGER NOT NULL,
        date TEXT NOT NULL,
        type TEXT NOT NULL CHECK(type IN ('purchase', 'payment_give','payment_take', 'add_balance', 'settled')),
        product_name TEXT,
        amount REAL NOT NULL,
        proof TEXT,
        FOREIGN KEY(account_no) REFERENCES farmers(account_no)
    )
    """)

    conn.commit()
    conn.close()

# ✅ Create DB only when run directly
if __name__ == "__main__":
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)  # Create /data folder if missing
    setup_database()
    print("✅ Database and tables created at:", DB_PATH)
