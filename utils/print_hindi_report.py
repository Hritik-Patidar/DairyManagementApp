# import sqlite3
# from PIL import Image, ImageDraw, ImageFont
# from datetime import datetime
# import os
# import win32api
#
# DB_PATH = "data/dairy_management.db"
# FONT_PATH = "C:\\Windows\\Fonts\\Mangal.ttf"  # Hindi supported font

# def print_hindi_report():
#     try:
#         width, height = 800, 1200
#         img = Image.new("RGB", (width, height), "white")
#         draw = ImageDraw.Draw(img)
#
#         # ✅ Load Hindi font
#         font = ImageFont.truetype(FONT_PATH, 24)
#         small_font = ImageFont.truetype(FONT_PATH, 20)
#
#         y = 20
#         def draw_line(text, font=font):
#             nonlocal y
#             draw.text((40, y), text, font=font, fill="black")
#             y += 40
#
#         date_today = datetime.now().strftime("%Y-%m-%d")
#         draw_line("🧾 डेयरी रिपोर्ट", font)
#         draw_line(f"📅 दिनांक: {date_today}", font)
#         draw_line("=" * 40, small_font)
#
#         conn = sqlite3.connect(DB_PATH)
#         cursor = conn.cursor()
#         cursor.execute("SELECT account_no, name, phone, balance FROM farmers ORDER BY account_no")
#         farmers = cursor.fetchall()
#
#         total_balance = 0
#         for acc_no, name, phone, balance in farmers:
#             total_balance += balance
#             draw_line(f"👤 खाता: {acc_no} | नाम: {name} | ₹{balance:.2f}", small_font)
#
#             cursor.execute("""
#                 SELECT date, type, product_name, amount, proof
#                 FROM transactions
#                 WHERE account_no=? AND date LIKE ?
#                 ORDER BY date
#             """, (acc_no, date_today + "%"))
#             txs = cursor.fetchall()
#
#             if not txs:
#                 draw_line("   🛈 आज कोई लेनदेन नहीं।", small_font)
#             else:
#                 for d, t, p, a, pr in txs:
#                     time = d[11:16]
#                     draw_line(f"   [{time}] {t.upper()} - {p or 'N/A'} - ₹{a:.2f}", small_font)
#
#             draw_line("-" * 40, small_font)
#
#         draw_line(f"👥 कुल किसान: {len(farmers)}", font)
#         draw_line(f"💰 कुल बकाया राशि: ₹{total_balance:.2f}", font)
#
#         conn.close()
#
#         # ✅ Save image and print
#         out_path = "hindi_report.png"
#         img.save(out_path)
#
#         # Print using default image viewer
#         win32api.ShellExecute(0, "print", out_path, None, ".", 0)
#         print("✅ Report sent to printer successfully.")
#
#     except Exception as e:
#         print("❌ Hindi print failed:", e)

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

            write("-" * 40)

        write(f"👥 कुल किसान: {len(farmers)}")
        write(f"💰 कुल बकाया राशि: ₹{total_balance:.2f}")

        conn.close()

        # Footer
        write("-" * 50)
        write("🙏 धन्यवाद!")

        pdc.EndPage()
        pdc.EndDoc()
        pdc.DeleteDC()
        print("✅ Report sent to printer.")

    except Exception as e:
        print("❌ Printing failed:", e)

if __name__ == "__main__":
    print_hindi_report()

