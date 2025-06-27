# utils/a4_hindi_report.py

import sqlite3
import win32print
import win32ui
from datetime import datetime

DB_PATH = "data/dairy_management.db"

def print_hindi_report():
    try:
        printer_name = win32print.GetDefaultPrinter()
        hPrinter = win32print.OpenPrinter(printer_name)
        pdc = win32ui.CreateDC()
        pdc.CreatePrinterDC(printer_name)

        pdc.StartDoc("Hindi Dairy Report")
        pdc.StartPage()

        font = win32ui.CreateFont({
            "name": "Mangal",   # ✅ Hindi font
            "height": 24,       # Font size
            "weight": 400,
        })
        pdc.SelectObject(font)

        y = 100
        line_height = 40

        def write(text):
            nonlocal y
            pdc.TextOut(100, y, text)
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
            write(f"👤 खाता: {acc_no} | नाम: {name} | ₹{balance:.2f}")

            cursor.execute("""
                SELECT date, type, product_name, amount, proof
                FROM transactions
                WHERE account_no = ? AND date LIKE ?
                ORDER BY date
            """, (acc_no, today + "%"))
            transactions = cursor.fetchall()

            if not transactions:
                write("   🛈 आज कोई लेनदेन नहीं।")
            else:
                for tx in transactions[:10]:  # max 10 entries per farmer
                    date, tx_type, product, amount, proof = tx
                    time = date[11:16]

                    # Hindi Type Mapping
                    hindi_type = {
                        "purchase": "खरीद",
                        "payment": "नकद",
                        "add_balance": "जमा",
                        "settled": "सेटल"
                    }.get(tx_type, tx_type)

                    write(f"   [{time}] {hindi_type:<6} {product or '—'} ₹{amount:.2f}")

            # write("-" * 40)

        write(f"👥 कुल किसान: {len(farmers)}")
        write(f"💰 कुल बकाया राशि: ₹{total_balance:.2f}")

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

if __name__ == "__main__":
    print_hindi_report()

