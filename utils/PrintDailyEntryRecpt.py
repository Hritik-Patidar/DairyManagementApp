import win32print

def print_direct(text):
    """Print text directly to default printer (Epson LQ-310) without paper feed."""
    printer_name = win32print.GetDefaultPrinter()

    # Open printer
    hprinter = win32print.OpenPrinter(printer_name)
    try:
        win32print.StartDocPrinter(hprinter, 1, ("Milk Slip", None, "RAW"))
        win32print.StartPagePrinter(hprinter)

        # ESC/P2 setup: initialize + no feed
        esc_init = b'\x1B@'         # Initialize
        esc_spacing = b'\x1B\x33\x00'  # Line spacing = 0
        data = esc_init + esc_spacing

        # Replace \n with carriage return only (no line feed)
        data += text.encode('ascii', 'ignore').replace(b'\n', b'\x0D')
        data += b'\x0D'  # final carriage return

        # Send to printer
        win32print.WritePrinter(hprinter, data)

        win32print.EndPagePrinter(hprinter)
        win32print.EndDocPrinter(hprinter)
        print(f"Printed on default printer: {printer_name}")
        print(data)

    finally:
        win32print.ClosePrinter(hprinter)
