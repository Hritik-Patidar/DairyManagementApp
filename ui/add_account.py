# ui/add_account.py

from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QVBoxLayout, QLineEdit,
    QPushButton, QMessageBox
)
from database import db_manager

class AddAccountDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Farmer Account")
        self.setFixedSize(400, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.account_input = QLineEdit()
        self.name_input = QLineEdit()
        self.phone_input = QLineEdit()

        self.account_input.setPlaceholderText("e.g. 101")
        self.name_input.setPlaceholderText("Farmer name")
        self.phone_input.setPlaceholderText("Phone number")

        form_layout.addRow("Account Number (manual):", self.account_input)
        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Phone:", self.phone_input)

        self.submit_btn = QPushButton("Create Account")
        self.submit_btn.clicked.connect(self.create_account)

        layout.addLayout(form_layout)
        layout.addWidget(self.submit_btn)
        self.setLayout(layout)

    def create_account(self):
        acc_no = self.account_input.text().strip()
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()

        if not acc_no.isdigit() or not name:
            QMessageBox.warning(self, "Error", "Please enter a valid account number and name.")
            return

        acc_no = int(acc_no)

        if db_manager.get_farmer(acc_no):
            QMessageBox.warning(self, "Exists", f"Account No {acc_no} already exists.")
            return

        success = db_manager.add_farmer_manual(acc_no, name, phone)

        if success:
            QMessageBox.information(self, "Success", f"Account No {acc_no} created successfully.")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to add farmer.")
