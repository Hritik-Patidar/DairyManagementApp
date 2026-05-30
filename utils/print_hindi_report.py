# utils/a4_hindi_report.py

import sqlite3
import win32print
import win32ui
from datetime import datetime

DB_PATH = "./data/dairy_management.db"

def print_balance_report():
    try:
        printer_name = win32print.GetDefaultPrinter()
        hPrinter = win32print.OpenPrinter(printer_name)
        pdc = win32ui.CreateDC()
        pdc.CreatePrinterDC(printer_name)

        pdc.StartDoc("Hindi Dairy Report")
        pdc.StartPage()

        font = win32ui.CreateFont({
            "name": "Mangal",   # ✅ Hindi font
            "height": 34,       # Font size
            "weight": 400,
        })
        pdc.SelectObject(font)

        y = 20
        line_height = 36

        def write(text):
            nonlocal y
            pdc.TextOut(22, y, text)
            y += line_height

        # Header
        today = datetime.now().strftime("%Y-%m-%d")
        write("🧾 डेयरी रिपोर्ट")
        write(f"📅 दिनांक: {today}")
        write("-" * 50)

        # DB Fetch
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT account_no, name, phone, balance FROM farmers ORDER BY account_no")
        farmers = cursor.fetchall()

        total_balance = 0
        for acc_no, name, phone, balance in farmers:
            total_balance += balance
            write(f"👤खाता:{acc_no:<3}|नाम:{name[:11]:<11}|₹{balance:.2f}")

            # cursor.execute("""
            #     SELECT date, type, product_name, amount, proof
            #     FROM transactions
            #     WHERE account_no = ? AND date LIKE ?
            #     ORDER BY date
            # """, (acc_no, today + "%"))
            # transactions = cursor.fetchall()

            # if not transactions:
            #     pass
            #     # write(" 🛈 आज कोई लेनदेन नहीं।")
            # else:
            #     for tx in transactions:
            #         date, tx_type, product, proof, amount = tx
            #         date_short = "-".join(date.split(" ")[0].split("-")[2::-1][:2])
            #
            #         hindi_type = {
            #             "purchase": "खरीद",
            #             "payment_give": "नकद दी गई/बाकी ",
            #             "payment_take": "किसान/देना",
            #             "add_balance": "हफ़्ता           ",
            #             "settled": "खाता सेटल"
            #         }.get(tx_type, tx_type)
            #
            #         try:
            #             amt = float(amount)
            #         except:
            #             amt = 0.0
            #
            #         prod = ''
            #         if product is None:
            #             prod = 'T'
            #
            #         elif tx_type == "settled":
            #             prod = 'S'
            #         else:
            #             prod = 'P'
            #
            #         line = f"  {date_short:<5}->{hindi_type[:7]:<7}-:₹{amt:.2f} {prod}"
            #         write(line)

            # write("-" * 40)
        write("-" * 50)
        write(f"👥 कुल किसान: {len(farmers)}")
        write(f"💰 कुल बकाया राशि: ₹{total_balance:.2f}")
        write("-" * 50)
        write("🙏 धन्यवाद!")

        conn.close()

        # # Footer
        # write("-" * 50)
        # write("🙏 धन्यवाद!")

        pdc.EndPage()
        pdc.EndDoc()
        pdc.DeleteDC()
        print("✅ Report sent to printer.")

    except Exception as e:
        print("❌ Printing failed:", e)

