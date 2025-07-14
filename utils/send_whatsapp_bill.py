import sqlite3
import socket
from datetime import datetime, timedelta
from database.db_manager import get_farmer_main
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
        farmer=get_farmer_main(account_no)
        two_months_ago = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")
        cursor.execute("""
            SELECT date, type, product_name, amount
            FROM transactions
            WHERE account_no=? AND date >= ?
            ORDER BY date DESC
        """, (account_no, two_months_ago))
        txs = cursor.fetchall()
        conn.close()

        if not txs:
            message = "पिछले 2 महीनों में कोई लेन-देन नहीं हुआ।"
        else:
            message = f"🧾 खाता संख्या {account_no} का बिल:\n  बैलेंस :-> {farmer[3]} \n  किसान :{farmer[1]}\n"
            from utils.hindi_type import get_hindi_type
            for date, tx_type, product, amount in txs:
                date_short = date.split(" ")[0]
                message += f"{date_short} - {get_hindi_type(tx_type)} - {product or 'लेनदेन'} - ₹{amount:.2f}\n"
                if tx_type == "settled":
                    break
        phone_number = f"+91{phone.strip()}"
        kit.sendwhatmsg_instantly(phone_number, message, wait_time=10, tab_close=False)

    except Exception as e:
        raise RuntimeError(f"❌ WhatsApp भेजने में समस्या हुई:\n{str(e)}")

