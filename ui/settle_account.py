# settle_account.py
# ui/settle_account.py

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox
from database import db_manager

class SettleAccountDialog(QDialog):
    def __init__(self, account_no,balance, parent=None):
        super().__init__(parent)
        self.account_no = account_no
        self.balance=balance
        self.setWindowTitle("Settle Account")
        self.setFixedSize(300, 150)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("This will reset the balance to ₹0."))

        self.settle_button = QPushButton("Confirm Settle")
        self.settle_button.clicked.connect(self.settle)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        layout.addWidget(self.settle_button)
        layout.addWidget(self.cancel_button)
        self.setLayout(layout)

    def settle(self):
        db_manager.add_transaction(
            account_no=self.account_no,
            t_type="settled",
            amount=self.balance,
            product_name="Settled",
            proof=f"Marked as settled And last balance is {self.balance}"
        )
        QMessageBox.information(self, "Settled", "Account marked as settled.")
        self.accept()
