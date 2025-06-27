from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QDateEdit, QMessageBox, QHeaderView
)
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QFont
from database import db_manager
from utils.thermal_printer import print_report

class ShowAllReportWidget(QWidget):
    def __init__(self):
        super().__init__()
        # self.mobile_label = None
        # self.table = None
        # self.name_label = None
        # self.fetch_btn = None
        # self.start_date = None
        # self.end_date = None
        # self.acc_input = None
        self.setWindowTitle("🧾 फ़िल्टर की गई रिपोर्ट")
        self.showMaximized()
        self.init_ui()

    def init_ui(self):
        try:
            main_layout = QVBoxLayout()
            main_layout.setContentsMargins(30, 20, 30, 20)
            main_layout.setSpacing(20)

            font = QFont("Segoe UI", 12)

            # Filter layout
            filter_layout = QHBoxLayout()
            filter_layout.setSpacing(10)

            self.acc_input = QLineEdit()
            self.acc_input.setPlaceholderText("खाता नंबर")
            self.acc_input.setFixedWidth(120)
            self.acc_input.setFont(font)
            self.acc_input.returnPressed.connect(self.load_data)

            self.start_date = QDateEdit()
            self.start_date.setCalendarPopup(True)
            self.start_date.setDate(QDate.currentDate())
            self.start_date.setFont(font)

            self.end_date = QDateEdit()
            self.end_date.setCalendarPopup(True)
            self.end_date.setDate(QDate.currentDate())
            self.end_date.setFont(font)

            self.fetch_btn = QPushButton("🔍 विवरण देखें")
            self.fetch_btn.setFont(font)
            self.fetch_btn.clicked.connect(self.load_data)

            filter_layout.addWidget(QLabel("खाता नंबर:", font=font))
            filter_layout.addWidget(self.acc_input)
            filter_layout.addStretch()
            filter_layout.addWidget(QLabel("शुरुआत दिनांक:", font=font))
            filter_layout.addWidget(self.start_date)
            filter_layout.addWidget(QLabel("अंतिम दिनांक:", font=font))
            filter_layout.addWidget(self.end_date)
            filter_layout.addWidget(self.fetch_btn)

            main_layout.addLayout(filter_layout)

            # Name and phone display
            info_layout = QHBoxLayout()
            self.name_label = QLabel("👤 नाम: —")
            self.name_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
            self.mobile_label = QLabel("📞 मोबाइल: —")
            self.mobile_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
            info_layout.addWidget(self.name_label)
            info_layout.addSpacing(40)
            info_layout.addWidget(self.mobile_label)
            info_layout.addStretch()
            main_layout.addLayout(info_layout)

            # Table
            self.table = QTableWidget()
            self.table.setColumnCount(5)
            self.table.setHorizontalHeaderLabels([
                "📅 तारीख", "प्रकार", "उत्पाद", "प्रमाण/अवधि", "राशि ₹"
            ])
            self.table.horizontalHeader().setStretchLastSection(True)
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.table.setFont(font)
            self.table.setMinimumHeight(500)
            self.table.setAlternatingRowColors(True)
            self.table.verticalHeader().setVisible(False)
            main_layout.addWidget(self.table)

            # Print button
            self.print_btn = QPushButton("🖨️ प्रिंट करें")
            self.print_btn.setFont(font)
            self.print_btn.clicked.connect(self.print_report_in)
            main_layout.addWidget(self.print_btn, alignment=Qt.AlignRight)

            self.setLayout(main_layout)

        except Exception as e:
            import traceback
            print("❌ ERROR:", traceback.format_exc())
            QMessageBox.critical(self, "Crash", f"त्रुटि:\n{str(e)}")

    def load_data(self):
        try:
            acc_no = self.acc_input.text().strip()
            if not acc_no.isdigit():
                QMessageBox.warning(self, "त्रुटि", "कृपया मान्य खाता संख्या दर्ज करें।")
                return

            acc_no = int(acc_no)
            start = self.start_date.date().toString("yyyy-MM-dd")
            end = self.end_date.date().toString("yyyy-MM-dd")

            farmer = db_manager.get_farmer(acc_no)
            if not farmer:
                QMessageBox.warning(self, "❌", "किसान नहीं मिला।")
                return

            self.name_label.setText(f"👤 नाम: {farmer['name']}")
            self.mobile_label.setText(f"📞 मोबाइल: {farmer['phone'] or '—'}")

            tx_list = db_manager.get_filtered_transactions(acc_no, start, end)
            self.table.setRowCount(0)


            for row, (date, tx_type, product, proof, amount) in enumerate(tx_list):
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(date))
                self.table.setItem(row, 1, QTableWidgetItem(self.get_hindi_type(tx_type)))
                self.table.setItem(row, 2, QTableWidgetItem(product or "—"))
                self.table.setItem(row, 3, QTableWidgetItem(proof or "—"))
                self.table.setItem(row, 4, QTableWidgetItem(f"₹{amount:.2f}"))

        except Exception as e:
            import traceback
            print("❌ ERROR:", traceback.format_exc())
            QMessageBox.critical(self, "Crash", f"त्रुटि:\n{str(e)}")

    def get_hindi_type(self, tx_type):
        return {
            "purchase": "खरीद",
            "payment_give": "नकद दी गई राशि",
            "payment_take": "नकद किसान द्वारा/बाकी",
            "add_balance": "हफ़्ता",
            "settled": "सेटल"
        }.get(tx_type, tx_type)

    def print_report_in(self):
        try:
            acc_no = int(self.acc_input.text().strip())
            farmer = db_manager.get_farmer(acc_no)
            start = self.start_date.date().toString("yyyy-MM-dd")
            end = self.end_date.date().toString("yyyy-MM-dd")
            tx_list = db_manager.get_filtered_transactions(acc_no, start, end)
            print_report(acc_no, farmer['name'], farmer['phone'], tx_list,farmer['balance'])
        except Exception as e:
            import traceback
            print("❌ ERROR:", traceback.format_exc())
            QMessageBox.critical(self, "Crash", f"त्रुटि:\n{str(e)}")