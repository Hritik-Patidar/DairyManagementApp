from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QVBoxLayout, QLineEdit, QPushButton,
    QComboBox, QMessageBox, QLabel, QDateEdit
)
from PyQt5.QtCore import QDate
from database import db_manager
from utils.hindi_type import get_hindi_type


class AddTransactionDialog(QDialog):
    def __init__(self, account_no, tx_type, parent=None):
        super().__init__(parent)
        self.account_no = account_no
        self.tx_type = tx_type
        self.setWindowTitle(f"{tx_type.title()} Entry")
        self.setFixedSize(400, 350)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.amount_input = QLineEdit()
        self.proof_input = QLineEdit()

        # 🛒 Product dropdown only for purchase
        self.product_dropdown = QComboBox()
        if self.tx_type == "purchase":
            products = db_manager.get_all_products()
            for name, price in products:
                self.product_dropdown.addItem(f"{name} - ₹{price}", name)
            form_layout.addRow("🛒 उत्पाद:", self.product_dropdown)

        form_layout.addRow("💰 राशि (₹):", self.amount_input)

        if self.tx_type.title() == "Add_Balance":
            # 📅 Date range input for "add_balance"
            self.from_date = QDateEdit()
            self.from_date.setCalendarPopup(True)
            self.from_date.setDisplayFormat("dd-MM-yyyy")
            self.from_date.setDate(QDate.currentDate())
            self.from_date.dateChanged.connect(self.update_date_range_field)

            self.to_date = QDateEdit()
            self.to_date.setCalendarPopup(True)
            self.to_date.setDisplayFormat("dd-MM-yyyy")
            self.to_date.setDate(QDate.currentDate())
            self.to_date.dateChanged.connect(self.update_date_range_field)

            self.date_range_field = QLineEdit()
            self.date_range_field.setReadOnly(True)

            form_layout.addRow("📅 शुरू की तारीख:", self.from_date)
            form_layout.addRow("📅 अंतिम तारीख:", self.to_date)
            form_layout.addRow("🗓️ चयनित अवधि:", self.date_range_field)

            self.update_date_range_field()

        else:
            # 📎 Proof field for other types
            form_layout.addRow("📎 प्रमाण / नोट:", self.proof_input)


        self.submit_btn = QPushButton(f"{get_hindi_type(self.tx_type)} जोड़ें")
        self.submit_btn.clicked.connect(self.submit)

        layout.addLayout(form_layout)
        layout.addWidget(self.submit_btn)
        self.setLayout(layout)

    def update_date_range_field(self):
        from_str = self.from_date.date().toString("dd-MM-yyyy")
        to_str = self.to_date.date().toString("dd-MM-yyyy")
        self.date_range_field.setText(f"{from_str} - {to_str}")

    def submit(self):
        try:
            amount = float(self.amount_input.text().strip())
            if amount <= 0:
                raise ValueError("राशि शून्य से अधिक होनी चाहिए।")

            product = None
            if self.tx_type == "purchase":
                product = self.product_dropdown.currentData()

            # ✅ Proof / Note handling based on tx_type
            if self.tx_type.title() == "Add_Balance":
                proof = self.date_range_field.text().strip()
            else:
                proof = self.proof_input.text().strip()

            # Save to database
            success = db_manager.add_transaction(
                self.account_no, self.tx_type, amount, product, proof
            )


            if success:
                QMessageBox.information(self, "✅ सफल", f"{get_hindi_type(self.tx_type)} सफलतापूर्वक जोड़ा गया।")
                self.accept()
            else:
                QMessageBox.critical(self, "❌ त्रुटि", "लेन-देन असफल रहा। लॉग जांचें।")

        except ValueError as ve:
            QMessageBox.warning(self, "⚠️ इनपुट त्रुटि", str(ve))
        except Exception as e:
            print("❌ Unexpected Error:", e)
            QMessageBox.critical(self, "Crash", f"❌ अप्रत्याशित त्रुटि: {e}")
