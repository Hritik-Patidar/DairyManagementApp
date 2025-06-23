# ui/add_product.py

from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QVBoxLayout,
    QLineEdit, QPushButton, QMessageBox
)
from database import db_manager

class AddProductDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Product")
        self.setFixedSize(400, 200)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.price_input = QLineEdit()

        self.name_input.setPlaceholderText("e.g. Ghee")
        self.price_input.setPlaceholderText("e.g. 120")

        form_layout.addRow("Product Name:", self.name_input)
        form_layout.addRow("Price (₹):", self.price_input)

        self.submit_btn = QPushButton("Add Product")
        self.submit_btn.clicked.connect(self.add_product)

        layout.addLayout(form_layout)
        layout.addWidget(self.submit_btn)
        self.setLayout(layout)

    def add_product(self):
        name = self.name_input.text().strip()
        price_text = self.price_input.text().strip()

        try:
            if not name or not price_text:
                raise ValueError("All fields are required.")

            price = float(price_text)

            if price <= 0:
                raise ValueError("Price must be positive.")

            success = db_manager.add_product(name, price)

            if success:
                QMessageBox.information(self, "Success", f"Product '{name}' added.")
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to add product.")

        except ValueError as ve:
            QMessageBox.warning(self, "Invalid", str(ve))
        except Exception as e:
            print("❌ Error in add_product:", e)
            QMessageBox.critical(self, "Error", str(e))
