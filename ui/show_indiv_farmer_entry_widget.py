import win32print
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QDateEdit, QMessageBox, QHeaderView, QFrame
)
from PyQt5.QtCore import Qt, QDate, QSizeF
from PyQt5.QtGui import QFont, QPainter, QTextDocument, QPageLayout, QPageSize
from database.db_manager import fetch_farmer_entries
import datetime


class FarmerEntryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🐄 Farmer Daily Entries")
        self.setMinimumWidth(900)
        # self.showFullScreen()
        self.showMaximized()
        self.setup_ui()
        self.apply_styles()

    # ---------------- UI SETUP ---------------- #
    def setup_ui(self):
        title = QLabel("🧾 Farmer Daily Entry Report")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2E8B57; margin-bottom: 10px;")

        # --- Inputs ---
        self.acc_label = QLabel("Account No:")
        self.acc_input = QLineEdit()
        self.acc_input.setPlaceholderText("Enter account number")

        self.from_label = QLabel("From Date:")
        self.from_date = QDateEdit(calendarPopup=True)
        self.from_date.setDate(QDate.currentDate().addDays(-9))

        self.to_label = QLabel("To Date:")
        self.to_date = QDateEdit(calendarPopup=True)
        self.to_date.setDate(QDate.currentDate())

        calendar1 = self.from_date.calendarWidget()
        calendar2 = self.to_date.calendarWidget()

        # Apply style to popup calendar text color
        calendar_style = """
        QCalendarWidget QAbstractItemView {
            color: white;            /* Text color */
            background-color: #2d2d2d; /* Background color */
            selection-background-color: #2d2d2d; /* Selected date background */
            selection-color: white;  /* Selected text color */
        }
        QCalendarWidget QWidget#qt_calendar_navigationbar {
            background-color: #444444;
        }
        QCalendarWidget QToolButton {
            color: white;
            background: transparent;
        }
        """

        calendar1.setStyleSheet(calendar_style)
        calendar2.setStyleSheet(calendar_style)



        # --- Buttons ---
        self.show_btn = QPushButton("📋 Show Entries")
        self.print_btn = QPushButton("🖨 Print Receipt")
        self.back_btn = QPushButton("🔙 वापस जाएं")
        self.back_btn.setObjectName("back_btn")

        # --- Table ---
        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(
            ["Date", "Shift", "Milk Type", "Qty (L)", "Fat", "CLR", "Rate", "Total Amount"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setFont(QFont("Segoe UI", 11))

        # --- Summary Bar ---
        self.summary_label = QLabel("Summary: 0 L | Avg Fat: 0 | Avg CLR: 0 | Avg Rate: 0 | Total: ₹0")
        self.summary_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.summary_label.setAlignment(Qt.AlignCenter)
        self.summary_label.setFrameShape(QFrame.Box)
        self.summary_label.setStyleSheet("background-color: #f0fff0; color: #333; padding: 6px;")

        # --- Layouts ---
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.acc_label)
        input_layout.addWidget(self.acc_input)
        input_layout.addWidget(self.from_label)
        input_layout.addWidget(self.from_date)
        input_layout.addWidget(self.to_label)
        input_layout.addWidget(self.to_date)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.show_btn)
        button_layout.addWidget(self.print_btn)
        button_layout.addWidget(self.back_btn)

        main_layout = QVBoxLayout()
        main_layout.addWidget(title)
        main_layout.addLayout(input_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.table)
        main_layout.addWidget(self.summary_label)

        self.setLayout(main_layout)

        # --- Signals ---
        self.show_btn.clicked.connect(self.on_show_entries)
        self.print_btn.clicked.connect(self.on_print_receipt)
        self.back_btn.clicked.connect(self.close)
        self.acc_input.returnPressed.connect(self.on_show_entries)


    # ---------------- STYLES ---------------- #
    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f9f9f9;
                font-family: "Segoe UI";
                font-size: 12pt;
            }
            QLabel {
                color: #333;
            }
            QLineEdit, QDateEdit {
                border: 1px solid #aaa;
                border-radius: 6px;
                padding: 6px;
                background-color: #fff;
            }
            QPushButton {
                background-color: #2E8B57;
                color: white;
                padding: 8px 16px;
                font-size: 13pt;
                font-weight: 600;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #3CB371;
            }
            QPushButton#back_btn {
                background-color: #c0392b;
            }
            QPushButton#back_btn:hover {
                background-color: #e74c3c;
            }
            QTableWidget {
                background-color: #fff;
                border: 1px solid #ccc;
                gridline-color: #ddd;
                alternate-background-color: #f2f2f2;
            }
            QHeaderView::section {
                background-color: #2E8B57;
                color: white;
                font-size: 13pt;
                padding: 4px;
            }
        """)

    # ---------------- INPUTS ---------------- #
    def get_inputs(self):
        acc_no = self.acc_input.text().strip()
        if not acc_no:
            QMessageBox.warning(self, "⚠️ Missing Input", "कृपया अकाउंट नंबर दर्ज करें।")
            return None, None, None
        from_date = self.from_date.date().toString("yyyy-MM-dd")
        to_date = self.to_date.date().toString("yyyy-MM-dd")
        return int(acc_no), from_date, to_date

    # ---------------- FETCH & POPULATE ---------------- #
    def on_show_entries(self):
        acc_no, from_date, to_date = self.get_inputs()
        if not acc_no:
            return
        data = fetch_farmer_entries(acc_no, from_date, to_date)
        self.populate_table(data)

    def populate_table(self, data):
        self.table.setRowCount(0)
        if not data:
            QMessageBox.information(self, "No Data", "इस किसान के लिए कोई एंट्री नहीं मिली।")
            return

        total_qty = total_amt = total_fat = total_clr = total_rate = 0
        for i, row in enumerate(data):
            date, shift, milk_type, fat, clr, rate, qty, total = row
            total_fat += fat
            total_clr += clr
            total_rate += rate
            total_qty += qty
            total_amt += total

            self.table.insertRow(i)
            for j, val in enumerate([date, shift, milk_type, qty, fat, clr, rate, total]):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, j, item)

        avg_fat = round(total_fat / len(data), 1)
        avg_clr = round(total_clr / len(data), 1)
        avg_rate = round(total_rate / len(data), 2)

        self.summary_label.setText(
            f"Summary: {total_qty:.2f} L | Avg Fat: {avg_fat} | Avg CLR: {avg_clr} | "
            f"Avg Rate: {avg_rate} | Total: ₹{total_amt:.2f}"
        )

    # ---------------- PRINT THERMAL RECEIPT (58mm) ---------------- #
    def on_print_receipt(self):
        acc_no, from_date, to_date = self.get_inputs()
        if not acc_no:
            return
        data = fetch_farmer_entries(acc_no, from_date, to_date)
        if not data:
            QMessageBox.warning(self, "No Data", "No entries available to print.")
            return

        html = self.build_receipt_html(acc_no, from_date, to_date, data)
        self.print_html_58mm(html)

    def build_receipt_html(self, acc_no, from_date, to_date, data):
        total_qty = total_amt = total_fat = total_clr = total_rate = 0
        rows_html = ""
        for d, s, m, f, c, r, q, t in data:
            total_fat += f
            total_clr += c
            total_rate += r
            total_qty += q
            total_amt += t
            rows_html += f"<tr><td>{d}</td><td>{s}</td><td>{m}</td><td>{f}</td><td>{r}</td><td>{t}</td></tr>"

        avg_fat = round(total_fat / len(data), 1)
        avg_clr = round(total_clr / len(data), 1)
        avg_rate = round(total_rate / len(data), 2)

        return f"""
        <div style='font-family: monospace; text-align:center; width:220px;'>
            <h3>🐄 डेयरी रसीद</h3>
            <p>Account No: {acc_no}</p>
            <p>{from_date} से {to_date}</p>
            <hr>
            <table width='100%' style='font-size:10pt;'>
                <tr><th>तारीख</th><th>शि</th><th>टाइप</th><th>फैट</th><th>रेट</th><th>राशि</th></tr>
                {rows_html}
            </table>
            <hr>
            <p>मात्रा: {total_qty:.2f}L | फैट: {avg_fat} | CLR: {avg_clr} | रेट: {avg_rate}</p>
            <h4>कुल राशि: ₹{total_amt:.2f}</h4>
            <p style='font-size:9pt;'>प्रिंटेड: {datetime.datetime.now().strftime('%d-%m-%Y %H:%M')}</p>
            <hr>
            <p>धन्यवाद 🙏</p>
        </div>
        """

    def print_html_58mm(self, html):
        try:
            doc = QTextDocument()
            doc.setHtml(html)

            printer = QPrinter()
            printer.setPageSize(QPageSize(QSizeF(58, 200), QPageSize.Millimeter))
            printer.setPageMargins(2, 2, 2, 2, QPrinter.Millimeter)
            printer.setOutputFormat(QPrinter.NativeFormat)
            printer.setPrinterName(win32print.GetDefaultPrinter())  # Default printer

            painter = QPainter(printer)
            doc.drawContents(painter)
            painter.end()

            QMessageBox.information(self, "प्रिंट हुआ ✅", "रसीद सफलतापूर्वक प्रिंट हो गई।")
        except Exception as e:
            print(e)