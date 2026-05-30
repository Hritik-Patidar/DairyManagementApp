import sqlite3
from pathlib import Path

DB_PATH = Path("data/dairy_management.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def get_connection():
    return sqlite3.connect(DB_PATH)

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

def get_transactions(account_no, limit=500):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT date, type, product_name, proof ,amount
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

def get_all_products():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, price FROM products")
    results = cursor.fetchall()
    conn.close()
    return results

def add_product(name, price):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO products (name, price) VALUES (?, ?)", (name, price))
        conn.commit()
        conn.close()
        print(f" Product added: {name} ₹{price}")
        return True
    except Exception as e:
        print(" Error in add_product:", e)
        return False


def add_transaction(account_no, t_type, amount, product_name=None, proof=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        from datetime import datetime

        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            INSERT INTO transactions (account_no, date, type, product_name, amount, proof)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (account_no, date_str, t_type, product_name, amount, proof))


        if t_type == "purchase":
            cursor.execute("UPDATE farmers SET balance = balance - ? WHERE account_no = ?", (amount, account_no))
        elif t_type == "payment_give":
            cursor.execute("UPDATE farmers SET balance = balance - ? WHERE account_no = ?", (amount, account_no))
        elif t_type == "add_balance":
            cursor.execute("UPDATE farmers SET balance = balance + ? WHERE account_no = ?", (amount, account_no))
        elif t_type == "settled":
            cursor.execute("UPDATE farmers SET previous_balance = balance WHERE account_no = ?", (account_no,))
            cursor.execute("UPDATE farmers SET balance = 0 WHERE account_no = ?", (account_no,))
        elif t_type =="payment_take":
            cursor.execute("UPDATE farmers SET balance = balance + ? WHERE account_no = ?", (amount, account_no))
        conn.commit()

        print(f"✅ Transaction added: {t_type} ₹{amount} to acc {account_no}")
        return True
    except Exception as e:
        print("❌ Error in add_transaction:", e)
        conn.rollback()
        return False
    finally:
        conn.close()


def add_farmer_manual(account_no, name, phone,milk_type,HindiName=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO farmers (account_no, name, phone, balance, milk_type,HindiName) VALUES (?, ?, ?, ?,?,?)",
            (account_no, name, phone, 0.0,milk_type,HindiName)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("❌ Error in add_farmer_manual:", e)
        conn.rollback()
        return False
    finally:
        conn.close()

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
                "balance": result[3],
                "milk_type":result[4],
                "hindiname":result[5]
            }
        return None
    except Exception as e:
        print("❌ Error in get_farmer:", e)
        return None

def get_all_farmers():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM farmers ORDER BY account_no ASC")
        rows = cursor.fetchall()
        conn.close()
        # return [
        #     {"account_no": row[0], "name": row[1], "phone": row[2],"balance":row[3]} for row in rows
        # ]
        return rows
    except Exception as e:
        print("❌ Error in get_all_farmers:", e)
        return []

def update_farmer(account_no, name, phone,hindiname):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE farmers SET name = ?, phone = ?, HindiName = ? WHERE account_no = ?",
            (name, phone,hindiname,account_no)
        )
        conn.commit()
        updated = cursor.rowcount
        conn.close()
        return updated > 0
    except Exception as e:
        print("❌ Error in update_farmer:", e)
        conn.rollback()
        return False
    finally:
        conn.close()

def delete_farmer(account_no,with_tx=False):
    try:
        def delete_transaction_ac():
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transactions WHERE account_no = ?", (account_no,))
            conn.commit()
            conn.close()
        if with_tx:
            delete_transaction_ac()
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM farmers WHERE account_no = ?", (account_no,))
            conn.commit()
            deleted = cursor.rowcount
            conn.close()
            return deleted > 0

        else:
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

def get_last_transactions(limit=15):
    """
    Get the latest N transactions for a given account number.
    Returns a list of tuples: (date, type, product_name, proof, amount)
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT account_no, date , type, product_name, proof, amount
            FROM transactions
            ORDER BY date DESC
            LIMIT ?
        """, ( limit,))
        results = cursor.fetchall()
        conn.close()
        return results
    except Exception as e:
        print("❌ Error fetching recent transactions:", e)
        return []

def delete_product(name):
    """
    Delete a product by its name.
    Returns True if deleted, False if not found.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE name = ?", (name,))
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        return deleted
    except Exception as e:
        print("❌ Error deleting product:", e)
        return False

def get_all_products_with_id():
    """
    Returns a list of all products as (id, name, price)
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price FROM products")
    results = cursor.fetchall()
    conn.close()
    return results

def delete_product_by_id(product_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        return deleted
    except Exception as e:
        print("❌ Error deleting product by ID:", e)
        return False


def delete_transaction(tx_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT account_no, type, amount FROM transactions WHERE id = ?", (tx_id,))


        row = cursor.fetchone()
        if not row:
            conn.close()
            return False

        account_no, tx_type, amount = row
        cursor.execute("SELECT balance, previous_balance FROM farmers WHERE account_no = ?", (account_no,))
        frow=cursor.fetchone()
        balance,previous_balance=frow

        # 🧮 Balance reverse करना based on type
        if tx_type == "purchase" or tx_type == "payment_give":
            cursor.execute("UPDATE farmers SET balance = balance + ? WHERE account_no = ?", (amount, account_no))
        elif tx_type == "add_balance" or tx_type == "payment_take":
            cursor.execute("UPDATE farmers SET balance = balance - ? WHERE account_no = ?", (amount, account_no))
        elif tx_type == "settled":
            cursor.execute("UPDATE farmers SET balance = balance + ? WHERE account_no = ?", (previous_balance, account_no))

        cursor.execute("DELETE FROM transactions WHERE id = ?", (tx_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("❌ Error in delete_transaction:", e)
        return False

def get_transactions_with_id(account_no, limit=999):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, date, type, product_name, amount, proof FROM transactions WHERE account_no = ? ORDER BY date DESC LIMIT ?",
        (account_no, limit)
    )
    result = cursor.fetchall()
    conn.close()
    return result


def get_transaction_by_id(tx_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions WHERE id = ?", (tx_id,))
    result = cursor.fetchone()
    conn.close()
    return result


def update_transaction(tx_id, product, new_amount, new_proof):
    conn = get_connection()
    cursor = conn.cursor()
    try:

        cursor.execute("SELECT account_no, amount, type FROM transactions WHERE id = ?", (tx_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return False

        account_no, old_amount, tx_type = row
        difference = new_amount - old_amount


        if tx_type == "purchase" or tx_type == "payment_give":
            cursor.execute("UPDATE farmers SET balance = balance - ? WHERE account_no = ?", (difference, account_no))
        elif tx_type == "add_balance" or tx_type == "payment_take":
            cursor.execute("UPDATE farmers SET balance = balance + ? WHERE account_no = ?", (difference, account_no))
        elif tx_type == "settled":
            # Settled में normally exact balance सेट होता है, तो update से अलग logic बनाना होगा
            print("⚠️ Warning: Cannot edit 'settled' amount safely. Skipping balance update.")
            return


        cursor.execute(
            "UPDATE transactions SET product_name = ?, amount = ?, proof = ? WHERE id = ?",
            (product, new_amount, new_proof, tx_id)
        )

        conn.commit()
        return True
    except Exception as e:
        print("❌ Error in update_transaction:", e)
        conn.rollback()
        return False
    finally:
        conn.close()


def get_rate_by_fat_clr(fat, clr):
    try:
        conn = sqlite3.connect("data/dairy_management.db")
        cur = conn.cursor()
        cur.execute("SELECT Rate FROM FatCLRRate WHERE Fat=? AND CLR=?", (fat, clr))
        row = cur.fetchone()
        conn.close()
        return row[0] if row else None
    except Exception as e:
        print(e)


def update_or_insert_rate(fat, clr, rate):
    conn = sqlite3.connect("data/dairy_management.db")
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO FatCLRRate (Fat, CLR, Rate) VALUES (?, ?, ?)", (fat, clr, rate))
    conn.commit()
    conn.close()


def make_entry(account_no, quantity, fat, clr, rate, total_amount, date, shift, milk_type):
    conn = get_connection()

    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    insert_query = """
        INSERT INTO DailyEntry (
            account_no, quantity, fat, clr, rate, total_amount, date, shift, milk_type
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    try:
        cursor.execute(insert_query, (account_no, quantity, fat, clr, rate, total_amount, date, shift, milk_type))
        conn.commit()
        print("✅ Data inserted successfully.")
    except Exception as e:
        print("❌ Error inserting data:", e)
        conn.rollback()
        return e
    finally:
        conn.close()


def get_entries_by_date_shift(date_str, shift):

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id,account_no, date, shift, quantity, fat, clr, rate, total_amount, milk_type
            FROM DailyEntry
            WHERE date = ? AND shift = ?
            ORDER BY account_no
        """, (date_str, shift))
        rows = cursor.fetchall()

        return rows
    except Exception as e:
        print(e)
    finally:
        conn.close()

def delete_entry(entry_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM DailyEntry WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()

def calculate_hafta(from_date, to_date, account_no=None):
    conn = get_connection()
    cur = conn.cursor()
    try:
        query = """
            SELECT account_no,
                   ROUND(AVG(fat),1) AS avg_fat,
                   ROUND(AVG(clr),1) AS avg_clr,
                   ROUND(AVG(rate),2) AS avg_rate,
                   ROUND(SUM(quantity),2) AS total_qty,
                   SUM(total_amount) AS total_amount
            FROM DailyEntry
            WHERE is_settled = 0
              AND date BETWEEN ? AND ?
        """
        params = [from_date, to_date]
        if account_no:
            query += " AND account_no = ?"
            params.append(account_no)
        query += " GROUP BY account_no"

        cur.execute(query, params)
        results = cur.fetchall()
        print(results)
        # Insert into hafta_summary
        proof = f"{from_date} - {to_date}"
        for acc,total_qty, fat, clr, rate, total in results:
            cur.execute("""
                INSERT INTO hafta_summary (account_no, from_date, to_date, total_amount)
                VALUES (?, ?, ?, ?)
            """, (acc, from_date, to_date, total))
            print("date between",from_date,to_date)
            cur.execute("""
                UPDATE DailyEntry
                SET is_settled = 1
                WHERE account_no = ? AND date BETWEEN ? AND ?
            """, (acc, from_date, to_date))
        conn.commit()
        conn.close()
        for acc, total_qty, fat, clr, rate, total in results:
            add_transaction(acc,"add_balance",total,"लेन-देन",proof)
        return results
    except Exception as e:
        print(e)


def fetch_hafta_summary(from_date, to_date, account_no=None):
    conn = get_connection()
    cur = conn.cursor()
    query = """
        SELECT account_no,
               ROUND(AVG(fat),1) AS avg_fat,
               ROUND(AVG(clr),1) AS avg_clr,
               ROUND(AVG(rate),2) AS avg_rate,
               ROUND(SUM(quantity),2) AS total_qty,
               ROUND(SUM(total_amount),2) AS total_amount
        FROM DailyEntry
        WHERE date BETWEEN ? AND ?
    """
    params = [from_date, to_date]
    if account_no:
        query += " AND account_no = ?"
        params.append(account_no)
    query += " GROUP BY account_no"
    cur.execute(query, params)
    results = cur.fetchall()
    conn.close()
    return results

def fetch_farmer_entries(account_no, from_date, to_date):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT date, shift, milk_type, fat, clr, rate, quantity, total_amount
        FROM DailyEntry
        WHERE account_no = ? AND date BETWEEN ? AND ?
        ORDER BY date
    """, (account_no, from_date, to_date))
    data = cur.fetchall()
    conn.close()
    return data
