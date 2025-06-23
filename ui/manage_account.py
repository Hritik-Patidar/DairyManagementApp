from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QMessageBox, QLabel
)
from database import db_manager


class ManageAccountWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manage Farmer Accounts")
        self.setMinimumSize(600, 400)
        self.init_ui()
        self.load_accounts()

    def init_ui(self):
        layout = QVBoxLayout()

        # --- Form Inputs ---
        form_layout = QHBoxLayout()
        self.account_input = QLineEdit()
        self.account_input.setPlaceholderText("Account No")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Farmer Name")
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Phone Number")

        form_layout.addWidget(QLabel("Acc No:"))
        form_layout.addWidget(self.account_input)
        form_layout.addWidget(QLabel("Name:"))
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(QLabel("Phone:"))
        form_layout.addWidget(self.phone_input)

        layout.addLayout(form_layout)

        # --- Buttons ---
        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add")
        self.edit_btn = QPushButton("Edit")
        self.delete_btn = QPushButton("Delete")

        self.add_btn.clicked.connect(self.add_account)
        self.edit_btn.clicked.connect(self.edit_account)
        self.delete_btn.clicked.connect(self.delete_account)

        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)

        layout.addLayout(button_layout)

        # --- Table ---
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Account No", "Name", "Phone"])
        self.table.cellClicked.connect(self.populate_fields)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_accounts(self):
        self.table.setRowCount(0)
        farmers = db_manager.get_all_farmers()
        for row, farmer in enumerate(farmers):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(farmer["account_no"])))
            self.table.setItem(row, 1, QTableWidgetItem(farmer["name"]))
            self.table.setItem(row, 2, QTableWidgetItem(farmer["phone"] or ""))

    def populate_fields(self, row, column):
        self.account_input.setText(self.table.item(row, 0).text())
        self.name_input.setText(self.table.item(row, 1).text())
        self.phone_input.setText(self.table.item(row, 2).text())

    def add_account(self):
        acc = self.account_input.text().strip()
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()

        if not acc.isdigit() or not name:
            QMessageBox.warning(self, "Input Error", "Enter valid account number and name.")
            return

        acc = int(acc)
        if db_manager.get_farmer(acc):
            QMessageBox.warning(self, "Exists", f"Account No {acc} already exists.")
            return

        if db_manager.add_farmer_manual(acc, name, phone):
            QMessageBox.information(self, "Success", f"Account {acc} added.")
            self.load_accounts()
        else:
            QMessageBox.critical(self, "Error", "Failed to add account.")

    def edit_account(self):
        acc = self.account_input.text().strip()
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()

        if not acc.isdigit() or not name:
            QMessageBox.warning(self, "Input Error", "Enter valid account number and name.")
            return

        acc = int(acc)
        if not db_manager.get_farmer(acc):
            QMessageBox.warning(self, "Not Found", f"No account found for {acc}")
            return

        if db_manager.update_farmer(acc, name, phone):
            QMessageBox.information(self, "Updated", f"Account {acc} updated.")
            self.load_accounts()
        else:
            QMessageBox.critical(self, "Error", "Failed to update.")

    def delete_account(self):
        acc = self.account_input.text().strip()
        if not acc.isdigit():
            QMessageBox.warning(self, "Input Error", "Enter valid account number.")
            return

        acc = int(acc)
        confirm = QMessageBox.question(self, "Confirm", f"Delete account {acc}?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            if db_manager.delete_farmer(acc):
                QMessageBox.information(self, "Deleted", f"Account {acc} deleted.")
                self.load_accounts()
            else:
                QMessageBox.critical(self, "Error", "Failed to delete.")


