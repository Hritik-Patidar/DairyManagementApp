# ui/add_transaction.py

from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QVBoxLayout, QLineEdit, QPushButton,
    QComboBox, QMessageBox, QLabel
)
from database import db_manager

class AddTransactionDialog(QDialog):
    def __init__(self, account_no, tx_type, parent=None):
        super().__init__(parent)
        self.account_no = account_no
        self.tx_type = tx_type
        self.setWindowTitle(f"{tx_type.title()} Entry")
        self.setFixedSize(400, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.amount_input = QLineEdit()
        self.proof_input = QLineEdit()

        # Only for purchase
        self.product_dropdown = QComboBox()
        if self.tx_type == "purchase":
            products = db_manager.get_all_products()
            for name, price in products:
                self.product_dropdown.addItem(f"{name} - ₹{price}", name)
            form_layout.addRow("Product:", self.product_dropdown)

        form_layout.addRow("Amount/रुपया (₹):", self.amount_input)
        form_layout.addRow("Proof / Note:", self.proof_input)

        hindi_type = {
            "purchase": "खरीद",
            "payment_give": "नकद दी गई राशि",
            "payment_take": "नकद किसान द्वारा",
            "add_balance": "हफ़्ता",
            "settled": "खाता सेटल"
        }.get(self.tx_type.title(),self.tx_type.title())
        self.submit_btn = QPushButton(f"{hindi_type} जोड़ें")
        self.submit_btn.clicked.connect(self.submit)

        layout.addLayout(form_layout)
        layout.addWidget(self.submit_btn)
        self.setLayout(layout)

    def submit(self):
        try:
            amount = float(self.amount_input.text().strip())
            proof = self.proof_input.text().strip()

            if amount <= 0:
                raise ValueError("Amount must be positive.")

            product = None
            if self.tx_type == "purchase":
                product = self.product_dropdown.currentData()

            # Save to DB
            success = db_manager.add_transaction(
                self.account_no, self.tx_type, amount, product, proof
            )

            if success:
                QMessageBox.information(self, "Success", f"{self.tx_type.title()} added successfully.")
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Transaction failed. Check console/log.")

        except ValueError as ve:
            QMessageBox.warning(self, "Invalid Input", str(ve))
        except Exception as e:
            print("❌ Unexpected Error in submit():", e)
            QMessageBox.critical(self, "Crash", f"Unexpected error: {e}")
