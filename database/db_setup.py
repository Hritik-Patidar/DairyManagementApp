# database/db_setup.py

import sqlite3
from datetime import datetime, timedelta
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
        balance REAL DEFAULT 0,
        milk_type TEXT NOT NULL CHECK(milk_type IN ('C','B')),
        previous_balance  REAL DEFAULT 0
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
        amount DECIMAL(10,2) NOT NULL,
        proof TEXT,
        FOREIGN KEY(account_no) REFERENCES farmers(account_no)
    )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS FatCLRRate (
            Fat DECIMAL(3,1) NOT NULL,
            CLR INT NOT NULL,
            Rate DECIMAL(5,2) NOT NULL,
            PRIMARY KEY (Fat, CLR)
        );
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS DailyEntry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_no INTEGER NOT NULL,
            quantity DECIMAL(7,2) NOT NULL,
            fat DECIMAL(3,1) NOT NULL,
            clr INTEGER NOT NULL,
            rate DECIMAL(7,2) NOT NULL,
            total_amount DECIMAL(7,2) NOT NULL,
            date TEXT NOT NULL,
            shift TEXT NOT NULL CHECK(shift IN ('M','E')),
            milk_type TEXT NOT NULL CHECK(milk_type IN ('C','B')),
            is_settled INTEGER DEFAULT 0,
            FOREIGN KEY(account_no) REFERENCES farmers(account_no),
            UNIQUE(account_no, date, shift)
            
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hafta_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_no INTEGER NOT NULL,
            from_date TEXT NOT NULL,
            to_date TEXT NOT NULL,
            total_amount DECIMAL(10,2) NOT NULL,
            created_on TEXT DEFAULT (date('now')),
            FOREIGN KEY(account_no) REFERENCES farmers(account_no)
        );
    """)
    #     cursor.execute("""
    # INSERT INTO FatCLRRate (Fat, CLR, Rate) VALUES
    # (3.2, 25, 16.83),(3.3, 25, 17.02),(3.4, 25, 17.21),(3.5, 25, 17.39),(3.6, 25, 17.58),(3.7, 25, 17.77),(3.8, 25, 17.96),(3.9, 25, 18.14),
    # (4.0, 25, 18.33),(4.1, 25, 18.52),(4.2, 25, 18.70),(4.3, 25, 37.52),(4.4, 25, 37.97),(4.5, 25, 38.42),(4.6, 25, 39.86),(4.7, 25, 40.32),
    # (4.8, 25, 40.77),(4.9, 25, 41.23),(5.0, 25, 41.69),(5.1, 25, 42.14),(5.2, 25, 42.60),(5.3, 25, 43.05),(5.4, 25, 43.51),(5.5, 25, 43.97),
    # (3.2, 26, 33.06),(3.3, 26, 33.50),(3.4, 26, 33.93),(3.5, 26, 34.37),(3.6, 26, 34.80),(3.7, 26, 35.24),(3.8, 26, 35.67),(3.9, 26, 36.11),
    # (4.0, 26, 36.54),(4.1, 26, 38.19),(4.2, 26, 38.63),(4.3, 26, 39.08),(4.4, 26, 39.53),(4.5, 26, 39.97),(4.6, 26, 41.44),(4.7, 26, 41.89),
    # (4.8, 26, 42.35),(4.9, 26, 42.80),(5.0, 26, 43.26),(5.1, 26, 43.72),(5.2, 26, 44.17),(5.3, 26, 44.63),(5.4, 26, 45.08),(5.5, 26, 45.54),
    # (3.2, 27, 34.59),(3.3, 27, 35.03),(3.4, 27, 35.46),(3.5, 27, 35.90),(3.6, 27, 36.33),(3.7, 27, 36.77),(3.8, 27, 37.20),(3.9, 27, 37.64),
    # (4.0, 27, 38.07),(4.1, 27, 39.74),(4.2, 27, 40.19),(4.3, 27, 40.60),(4.4, 27, 40.99),(4.5, 27, 41.38),(4.6, 27, 42.80),(4.7, 27, 43.20),
    # (4.8, 27, 43.59),(4.9, 27, 43.99),(5.0, 27, 44.39),(5.1, 27, 44.78),(5.2, 27, 45.18),(5.3, 27, 46.40),(5.4, 27, 46.80),(5.5, 27, 47.21),
    # (3.2, 28, 36.00),(3.3, 28, 36.38),(3.4, 28, 36.75),(3.5, 28, 37.13),(3.6, 28, 38.70),(3.7, 28, 39.09),(3.8, 28, 39.48),(3.9, 28, 39.87),
    # (4.0, 28, 40.25),(4.1, 28, 41.65),(4.2, 28, 42.04),(4.3, 28, 42.44),(4.4, 28, 42.83),(4.5, 28, 43.23),(4.6, 28, 44.42),(4.7, 28, 44.82),
    # (4.8, 28, 45.23),(4.9, 28, 45.63),(5.0, 28, 46.03),(5.1, 28, 46.44),(5.2, 28, 46.84),(5.3, 28, 47.24),(5.4, 28, 47.64),(5.5, 28, 48.05),
    # (3.2, 29, 36.78),(3.3, 29, 37.16),(3.4, 29, 37.53),(3.5, 29, 37.91),(3.6, 29, 39.51),(3.7, 29, 39.90),(3.8, 29, 40.28),(3.9, 29, 40.67),
    # (4.0, 29, 41.06),(4.1, 29, 42.47),(4.2, 29, 42.87),(4.3, 29, 43.26),(4.4, 29, 43.66),(4.5, 29, 44.05),(4.6, 29, 45.26),(4.7, 29, 45.66),
    # (4.8, 29, 46.07),(4.9, 29, 46.47),(5.0, 29, 46.87),(5.1, 29, 47.28),(5.2, 29, 47.68),(5.3, 29, 48.09),(5.4, 29, 48.38),(5.5, 29, 48.72),
    # (3.2, 30, 37.56),(3.3, 30, 37.94),(3.4, 30, 38.31),(3.5, 30, 38.69),(3.6, 30, 40.31),(3.7, 30, 40.70),(3.8, 30, 41.09),(3.9, 30, 41.47),
    # (4.0, 30, 41.86),(4.1, 30, 43.23),(4.2, 30, 43.56),(4.3, 30, 43.89),(4.4, 30, 44.22),(4.5, 30, 44.55),(4.6, 30, 45.76),(4.7, 30, 46.03),
    # (4.8, 30, 46.37),(4.9, 30, 46.70),(5.0, 30, 47.04),(5.1, 30, 47.38),(5.2, 30, 47.71),(5.3, 30, 48.05),(5.4, 30, 48.38),(5.5, 30, 48.72);
    # """)
    import random
    milk_types = ['C', 'B']

    # Dummy names for random farmers
    names = [
        "Ramesh", "Suresh", "Mahesh", "Mukesh", "Rajesh", "Naresh", "Lokesh",
        "Kamal", "Ravi", "Vikas", "Deepak", "Anil", "Sunil", "Vinod", "Pankaj",
        "Sanjay", "Arun", "Ajay", "Vijay", "Dinesh", "Manoj", "Ashok", "Rohit",
        "Kiran", "Nitin", "Harish", "Prakash", "Mahendra", "Narayan", "Subhash"
    ]

    for acc_no in range(8, 131):
        name = random.choice(names)
        phone = f"9{random.randint(100000000, 999999999)}"  # 10-digit phone
        milk_type = random.choice(milk_types)

        cursor.execute("""
            INSERT OR IGNORE INTO farmers (account_no, name, phone, milk_type)
            VALUES (?, ?, ?, ?)
        """, (acc_no, name, phone, milk_type))

    print("✅ Dummy farmer entries inserted successfully (8–130).")

    today = datetime.now().date()

    # Loop for last 10 days
    for day_offset in range(50):
        entry_date = (today - timedelta(days=day_offset)).strftime("%d-%m-%Y")

        for acc_no in range(1, 131):  # 1 to 130 farmers
            milk_type = random.choice(['C', 'B'])

            for shift in ['M', 'E']:
                qty = round(random.uniform(3, 10), 2)  # 3L - 10L
                fat = round(random.uniform(3.5, 6.5), 1)
                clr = random.randint(24, 30)
                rate = round(random.uniform(30, 45), 2)
                total_amount = round(qty * rate, 2)

                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO DailyEntry 
                        (account_no, quantity, fat, clr, rate, total_amount, date, shift, milk_type)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (acc_no, qty, fat, clr, rate, total_amount, entry_date, shift, milk_type))
                except Exception as e:
                    print(f"❌ Error inserting for acc_no {acc_no}: {e}")

    conn.commit()
    conn.close()
# ✅ Create DB only when run directly
if __name__ == "__main__":
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)  # Create /data folder if missing
    setup_database()
    print("✅ Database and tables created at:", DB_PATH)
