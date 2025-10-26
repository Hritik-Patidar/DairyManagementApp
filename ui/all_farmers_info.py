from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from database import db_manager
from utils.print_hindi_report import print_balance_report


class ShowAllFarmersWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("सभी किसानों की सूची")
        self.showMaximized()
        self.init_ui()
        self.load_data()  # ⬅️ Load data immediately on start

    def init_ui(self):
        try:
            font = QFont("Segoe UI", 12)

            main_layout = QVBoxLayout()
            main_layout.setContentsMargins(30, 20, 30, 20)
            main_layout.setSpacing(20)

            # Title
            title_label = QLabel("📋 सभी किसानों की रिपोर्ट")
            title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
            title_label.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(title_label)

            # Buttons Layout (Back + Print)
            button_layout = QHBoxLayout()
            button_layout.setSpacing(20)

            # ⬅️ Back Button (Left-aligned)
            self.back_btn = QPushButton("◀️ वापस जाएं")
            self.back_btn.setFont(font)
            self.back_btn.clicked.connect(self.close)
            button_layout.addWidget(self.back_btn, alignment=Qt.AlignLeft)

            # 🖨️ Print Button (Right-aligned)
            self.print_btn = QPushButton("🖨️ प्रिंट करें")
            self.print_btn.setFont(font)
            self.print_btn.clicked.connect(self.print_report_in)
            button_layout.addWidget(self.print_btn, alignment=Qt.AlignRight)

            main_layout.addLayout(button_layout)

            # Table setup
            self.table = QTableWidget()
            self.table.setColumnCount(4)
            self.table.setHorizontalHeaderLabels(["AC No", "नाम", "मोबाइल", "राशि ₹"])
            self.table.horizontalHeader().setStretchLastSection(True)
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.table.verticalHeader().setVisible(False)
            self.table.setAlternatingRowColors(True)
            self.table.setFont(font)
            self.table.setMinimumHeight(500)

            main_layout.addWidget(self.table)

            self.setLayout(main_layout)

        except Exception as e:
            self.handle_exception("UI Initialization", e)

    def load_data(self):
        try:
            farmers = db_manager.get_all_farmers()

            self.table.setRowCount(0)

            if not farmers:
                QMessageBox.information(self, "कोई डेटा नहीं", "कोई किसान नहीं मिला।")
                return

            for row, (account_no, name, phone, balance,milk_type,_) in enumerate(farmers):
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(account_no)))
                self.table.setItem(row, 1, QTableWidgetItem(name))
                self.table.setItem(row, 2, QTableWidgetItem(phone))
                self.table.setItem(row, 3, QTableWidgetItem(f"₹{balance}"))
                self.table.setItem(row, 4, QTableWidgetItem(milk_type))

        except Exception as e:
            self.handle_exception("डेटा लोड करते समय", e)

    def print_report_in(self):
        try:
            print_balance_report()
        except Exception as e:
            self.handle_exception("प्रिंट करते समय", e)

    def handle_exception(self, context, exception):
        import traceback
        print(f"❌ ERROR in {context}:\n", traceback.format_exc())
        QMessageBox.critical(self, "क्रैश", f"{context} में त्रुटि:\n{str(exception)}")
