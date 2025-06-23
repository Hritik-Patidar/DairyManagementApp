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
        "name": "Consolas",
        "height": 18,
        "weight": 400,
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
    write("-" * 32)
    write("Date        Type      Amt")
    write("-" * 32)

    # for tx in transactions[-5:]:
    #     date, tx_type, _, amount, _ = tx
    #     date_short = date.split(" ")[0]
    #     line = f"{date_short:<11}{tx_type:<6}₹{amount:.2f}"
    #     write(line)

    for tx in transactions[0:11]:
        date, tx_type, _, amount, _ = tx
        date_short = date.split(" ")[0]

        # ✅ हिंदी अनुवाद के लिए मैपिंग
        hindi_type = {
            "purchase": "खरीद",
            "payment_give": "नकद दी गई राशि",
            "payment_take": "नकद किसान द्वारा",
            "add_balance": "हफ़्ता",
            "settled": "खाता सेटल"
        }.get(tx_type, tx_type)  # default: original tx_type

        line = f"{date_short:<11}{hindi_type:<8}₹{amount:.2f}"
        write(line)

    write("-" * 32)
    write("Thank you!")

    pdc.EndPage()
    pdc.EndDoc()
    pdc.DeleteDC()
