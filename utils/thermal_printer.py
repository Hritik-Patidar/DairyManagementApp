# utils/thermal_printer.py

def print_report(account_no, farmer_name, phone, transactions, balance, height_font=34,notfull=False):
    import win32print
    import win32ui

    printer_name = win32print.GetDefaultPrinter()
    hPrinter = win32print.OpenPrinter(printer_name)
    pdc = win32ui.CreateDC()
    pdc.CreatePrinterDC(printer_name)

    pdc.StartDoc("Filtered Report")
    pdc.StartPage()  # ✅ Required to suppress driver issues

    # Font settings for 58mm paper
    font = win32ui.CreateFont({
        "name": "Mangal",
        "height": height_font,
        "weight": 500,
    })
    pdc.SelectObject(font)

    y = 50  # ✅ Start from very top
    line_height = height_font + 2  # line spacing

    def write(text):
        nonlocal y
        pdc.TextOut(22, y, text)
        y += line_height

    # --- Header ---
    write("🧾 किसान रिपोर्ट")
    write(f"खाता: {account_no}")
    write(f"नाम: {farmer_name}")
    write(f"मोबाइल: {phone}")
    write("-" * 32)

    for tx in transactions:
        date, tx_type, product, proof, amount = tx
        date_short = "-".join(date.split(" ")[0].split("-")[2::-1][:2])

        hindi_type = {
            "purchase": "खरीद",
            "payment_give": "नकद दी गई/बाकी ",
            "payment_take": "किसान/देना",
            "add_balance": "हफ़्ता           ",
            "settled": "खाता सेटल"
        }.get(tx_type, tx_type)

        try:
            amt = float(amount)
        except:
            amt = 0.0

        prod=''
        if product is None:
            prod='T'

        elif tx_type=="settled":
            prod='S'
        else:
            prod='P'

        line = f"{date_short:<5}->{hindi_type[:7]:<7} -:₹{amt:.2f} {prod}"
        write(line)
        if notfull and tx_type == "settled":
            break


    write("-" * 32)
    write(f"{'Avl Balance':<19}₹{balance:.2f}")
    write("T->लेनदेन")
    write("P->घी/सुदना/खली/अन्य ")
    write("S->खाता सेटल")
    write("🙏 धन्यवाद!")
    stop_feed_lq310()
    pdc.EndPage()   # ✅ This ensures correct flushing without page eject
    pdc.EndDoc()
    pdc.DeleteDC()

def stop_feed_lq310():
    import win32print

    printer_name = win32print.GetDefaultPrinter()
    hPrinter = win32print.OpenPrinter(printer_name)
    try:
        hJob = win32print.StartDocPrinter(hPrinter, 1, ("Stop Feed", None, "RAW"))
        win32print.StartPagePrinter(hPrinter)

        # ESC @ (initialize), ESC C 0 (set page length to 0), ESC 3 16 (set small line spacing)
        commands = b"\x1B@"       # Initialize
        commands += b"\x1BC\x00"  # Page length = 0 (continuous feed)
        commands += b"\x1B3\x10"  # Line spacing 16/216 inch

        win32print.WritePrinter(hPrinter, commands)
        win32print.EndPagePrinter(hPrinter)
        win32print.EndDocPrinter(hPrinter)
    finally:
        win32print.ClosePrinter(hPrinter)


