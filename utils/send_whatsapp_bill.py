import sqlite3
import socket
from datetime import datetime, timedelta

DB_PATH = "data/dairy_management.db"

def is_connected():
    """Check if internet is available (non-crashing)"""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except OSError:
        return False

def send_bill_to_whatsapp(account_no, phone):
    if not is_connected():
        raise RuntimeError("❌ इंटरनेट उपलब्ध नहीं है। कृपया पहले कनेक्शन जांचें।")

    try:
        # ✅ Only import pywhatkit here
        import pywhatkit as kit
    except ImportError:
        raise RuntimeError("📦 pywhatkit module लोड नहीं हो पाया।")

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        two_months_ago = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")
        cursor.execute("""
            SELECT date, type, product_name, amount
            FROM transactions
            WHERE account_no=? AND date >= ?
            ORDER BY date
        """, (account_no, two_months_ago))
        txs = cursor.fetchall()
        conn.close()

        if not txs:
            message = "पिछले 2 महीनों में कोई लेन-देन नहीं हुआ।"
        else:
            message = f"🧾 खाता संख्या {account_no} का 2 महीने का बिल:\n"
            for date, tx_type, product, amount in txs:
                hindi_type = {
                    "purchase": "खरीद",
                    "payment": "नकद दी गई राशि",
                    "add_balance": "हफ़्ता",
                    "settled": "खाता सेटल"
                }.get(tx_type, tx_type)
                date_short = date.split(" ")[0]
                message += f"{date_short} - {hindi_type} - {product or 'N/A'} - ₹{amount:.2f}\n"

        phone_number = f"+91{phone.strip()}"
        kit.sendwhatmsg_instantly(phone_number, message, wait_time=10, tab_close=False)

    except Exception as e:
        raise RuntimeError(f"❌ WhatsApp भेजने में समस्या हुई:\n{str(e)}")

