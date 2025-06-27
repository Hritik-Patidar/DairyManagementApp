# utils/thermal_printer.py

import win32print
import win32ui

def print_small_receipt(account_no, farmer_name, balance, transactions):
    printer_name = win32print.GetDefaultPrinter()
    hPrinter = win32print.OpenPrinter(printer_name)
    pdc = win32ui.CreateDC()
    pdc.CreatePrinterDC(printer_name)

    pdc.StartDoc("Dairy Receipt")
    pdc.StartPage()

    font = win32ui.CreateFont({
        "name": "mangal",
        "height": 22,
        "weight": 700,
    })
    pdc.SelectObject(font)

    y = 100  # Starting vertical position
    line_height = 30

    def write(text):
        nonlocal y
        pdc.TextOut(50, y, text)
        y += line_height

    # Content
    write("🧾 DAIRY RECEIPT")
    write(f"Acc No: {account_no}")
    write(f"Name: {farmer_name}")
    write(f"Balance: ₹{balance:.2f}")
    write("-" * 50)
    write("Date           Type     Amt")
    write("-" * 50)

    # for tx in transactions[-5:]:
    #     date, tx_type, _, amount, _ = tx
    #     date_short = date.split(" ")[0]
    #     line = f"{date_short:<11}{tx_type:<6}₹{amount:.2f}"
    #     write(line)

    for tx in transactions[0:11]:
        date, tx_type, product_name, amount, _ = tx
        date_short = "-".join(date.split(" ")[0].split("-")[2::-1][:2])

        # ✅ हिंदी अनुवाद के लिए मैपिंग
        hindi_type = {
            "purchase": "खरीद",
            "payment_give": "नकद दी गई ",
            "payment_take": "किसान/बाकी",
            "add_balance": "हफ़्ता           ",
            "settled": "खाता सेटल"
        }.get(tx_type, tx_type)  # default: original tx_type

        line = f"{date_short:<5}|{(hindi_type)[:13]:<13} {(product_name or 'लेनदेन')[:7]:<5} ₹{amount:.2f}"
        write(line)
        if tx_type == "settled":
            break

    write("-" * 50)
    write("Thank you!")

    # pdc.EndPage()
    pdc.EndDoc()
    pdc.DeleteDC()

def print_report(account_no, farmer_name, phone, transactions,balance):
    printer_name = win32print.GetDefaultPrinter()
    hPrinter = win32print.OpenPrinter(printer_name)
    pdc = win32ui.CreateDC()
    pdc.CreatePrinterDC(printer_name)

    pdc.StartDoc("Filtered Report")
    pdc.StartPage()

    # Font settings for 58mm paper
    font = win32ui.CreateFont({
        "name": "Mangal",
        "height": 22,
        "weight": 700,
    })
    pdc.SelectObject(font)

    y = 100
    line_height = 30

    def write(text):
        nonlocal y
        pdc.TextOut(30, y, text)
        y += line_height

    # --- Header ---
    write("🧾 किसान रिपोर्ट")
    write(f"खाता: {account_no}")
    write(f"नाम: {farmer_name}")
    write(f"मोबाइल: {phone}")
    write("-" * 32)
    # write(f"{'तारीख':<11}{'प्रकार':<7}{'उत्पा':<5}{'₹'}")
    # write("-" * 32)

    # total = 0.0
    for tx in transactions:
        date, tx_type, product, proof, amount = tx
        date_short = "-".join(date.split(" ")[0].split("-")[2::-1][:2])

        hindi_type = {
            "purchase":     "खरीद     ",
            "payment_give": "नकद दी   ",
            "payment_take": "किसान/बाकी",
            "add_balance":  "हफ़्ता      ",
            "settled":      "सेटल     "
        }.get(tx_type, tx_type)

        try:
            amt = float(amount)
        except:
            amt = 0.0

        line = f"{date_short:<5}{hindi_type[:7]:<7}{(product or 'लेनदेन')[:7]:<7}₹{amt:.2f}"
        write(line)

    write("-" * 32)
    write(f"{'Avl Balance':<24}₹{balance:.2f}")
    write("🙏 धन्यवाद!")

    # pdc.EndPage()
    pdc.EndDoc()
    pdc.DeleteDC()