import sqlite3
import win32print
import win32ui
from datetime import datetime

DB_PATH = "data/dairy_management.db"

def generate_daily_report():
    try:
        # Get default printer
        printer_name = win32print.GetDefaultPrinter()
        pdc = win32ui.CreateDC()
        pdc.CreatePrinterDC(printer_name)
        pdc.StartDoc("Full Page Dairy Report")
        pdc.StartPage()

        # Set Font
        font = win32ui.CreateFont({
            "name": "Consolas",
            "height": 18,
            "weight": 500
        })
        pdc.SelectObject(font)

        y = 100
        line_height = 30

        def draw(text):
            nonlocal y
            pdc.TextOut(100, y, text)
            y += line_height

        # Header
        today = datetime.now().strftime("%Y-%m-%d")
        draw("🧾 DAIRY FULL REPORT".center(80))
        draw(f"📅 Date: {today}")
        draw("=" * 100)

        # DB Fetch
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT account_no, name, phone, balance FROM farmers ORDER BY account_no")
        farmers = cursor.fetchall()

        total_balance = 0
        for acc_no, name, phone, balance in farmers:
            total_balance += balance
            draw(f"🧑‍🌾 Acc:{acc_no} | {name} | 📞 {phone or 'N/A'} | 💰 ₹{balance:.2f}")
            cursor.execute("""
                SELECT date, type, product_name, amount, proof
                FROM transactions
                WHERE account_no=? AND date LIKE ?
                ORDER BY date
            """, (acc_no, today + "%"))
            txs = cursor.fetchall()
            if not txs:
                draw("   No transactions today.")
            else:
                for d, t, p, a, pr in txs:
                    time = d[11:16]
                    draw(f"   [{time}] {t.upper():<10} {p or 'N/A':<10} ₹{a:.2f}  {pr or ''}")
            draw("-" * 100)

        # Summary
        draw("=" * 100)
        draw(f"👥 Total Farmers: {len(farmers)}")
        draw(f"💰 Total Outstanding Balance: ₹{total_balance:.2f}")

        conn.close()

        pdc.EndPage()
        pdc.EndDoc()
        pdc.DeleteDC()

        print("✅ Full A4 report sent to printer")

    except Exception as e:
        print("❌ Print failed:", e)
