import sqlite3
from pathlib import Path

DB_PATH = Path("data/dairy_management.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)  # Ensure 'data/' exists

def get_connection():
    return sqlite3.connect(DB_PATH)

# --- FARMER FUNCTIONS ---
def get_filtered_transactions(account_no, start_date, end_date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT date, type, product_name, proof, amount
        FROM transactions
        WHERE account_no = ?
        AND DATE(date) BETWEEN DATE(?) AND DATE(?)
        ORDER BY date DESC
    """, (account_no, start_date, end_date))
    result = cursor.fetchall()
    conn.close()
    return result




def get_farmer_main(account_no):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM farmers WHERE account_no = ?", (account_no,))
    farmer = cursor.fetchone()
    conn.close()
    return farmer

def get_transactions(account_no, limit=5):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT date, type, product_name, amount, proof 
        FROM transactions 
        WHERE account_no = ? 
        ORDER BY date DESC 
        LIMIT ?
    """, (account_no, limit))
    results = cursor.fetchall()
    conn.close()
    return results
def get_all_transactions(limit):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT account_no, date, type, product_name, amount, proof 
        FROM transactions
        ORDER BY date DESC 
        LIMIT ?
    """, (limit,))  # ✅ Tuple form में pass करें
    results = cursor.fetchall()
    conn.close()
    return results

# --- PRODUCT FUNCTIONS ---

def get_all_products():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, price FROM products")
    results = cursor.fetchall()
    conn.close()
    return results

def add_product(name, price):
    try:
        conn = sqlite3.connect("data/dairy_management.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO products (name, price) VALUES (?, ?)", (name, price))
        conn.commit()
        conn.close()
        print(f"✅ Product added: {name} ₹{price}")
        return True
    except Exception as e:
        print("❌ Error in add_product:", e)
        return False

# --- TRANSACTION FUNCTIONS ---

def add_transaction(account_no, t_type, amount, product_name=None, proof=None):
    try:
        from datetime import datetime
        conn = sqlite3.connect("data/dairy_management.db")
        cursor = conn.cursor()

        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            INSERT INTO transactions (account_no, date, type, product_name, amount, proof)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (account_no, date_str, t_type, product_name, amount, proof))

        # ✅ Correct balance update logic
        if t_type == "purchase":
            cursor.execute("UPDATE farmers SET balance = balance - ? WHERE account_no = ?", (amount, account_no))
        elif t_type == "payment_give":
            cursor.execute("UPDATE farmers SET balance = balance - ? WHERE account_no = ?", (amount, account_no))
        elif t_type == "add_balance":
            cursor.execute("UPDATE farmers SET balance = balance + ? WHERE account_no = ?", (amount, account_no))
        elif t_type == "settled":
            cursor.execute("UPDATE farmers SET balance = ? WHERE account_no = ?", (amount, account_no))
        elif t_type =="payment_take":
            cursor.execute("UPDATE farmers SET balance = balance + ? WHERE account_no = ?", (amount, account_no))
        conn.commit()
        conn.close()

        print(f"✅ Transaction added: {t_type} ₹{amount} to acc {account_no}")
        return True
    except Exception as e:
        print("❌ Error in add_transaction:", e)
        return False



def add_farmer_manual(account_no, name, phone):
    try:
        conn = sqlite3.connect("data/dairy_management.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO farmers (account_no, name, phone, balance) VALUES (?, ?, ?, ?)",
            (account_no, name, phone, 0.0)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("❌ Error in add_farmer_manual:", e)
        return False

def get_farmer(account_no):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM farmers WHERE account_no = ?", (account_no,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return {
                "account_no": result[0],
                "name": result[1],
                "phone": result[2],
                "balance": result[3]
            }
        return None
    except Exception as e:
        print("❌ Error in get_farmer:", e)
        return None


def get_all_farmers():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT account_no, name, phone FROM farmers ORDER BY account_no ASC")
        rows = cursor.fetchall()
        conn.close()
        return [
            {"account_no": row[0], "name": row[1], "phone": row[2]} for row in rows
        ]
    except Exception as e:
        print("❌ Error in get_all_farmers:", e)
        return []


def update_farmer(account_no, name, phone):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE farmers SET name = ?, phone = ? WHERE account_no = ?",
            (name, phone, account_no)
        )
        conn.commit()
        updated = cursor.rowcount
        conn.close()
        return updated > 0
    except Exception as e:
        print("❌ Error in update_farmer:", e)
        return False


def delete_farmer(account_no):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM farmers WHERE account_no = ?", (account_no,))
        conn.commit()
        deleted = cursor.rowcount
        conn.close()
        return deleted > 0
    except Exception as e:
        print("❌ Error in delete_farmer:", e)
        return False