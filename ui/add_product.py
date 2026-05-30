from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QVBoxLayout,
    QLineEdit, QPushButton, QMessageBox, QHBoxLayout, QComboBox, QLabel
)
from database import db_manager


class AddProductDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("उत्पाद जोड़ें / हटाएं")
        self.setFixedSize(470, 260)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.price_input = QLineEdit()

        self.name_input.setPlaceholderText("उदाहरण: Ghee")
        self.price_input.setPlaceholderText("उदाहरण: 120")

        form_layout.addRow("उत्पाद का नाम:", self.name_input)
        form_layout.addRow("कीमत (₹):", self.price_input)

        layout.addLayout(form_layout)


        self.remove_label = QLabel("🗑️ हटाने के लिए उत्पाद चुनें:")
        self.product_dropdown = QComboBox()
        self.load_products()  # Dropdown fill

        btn_layout = QHBoxLayout()
        self.submit_btn = QPushButton("➕ उत्पाद जोड़ें")
        self.remove_btn = QPushButton("🗑️ उत्पाद हटाएं")

        self.submit_btn.clicked.connect(self.add_product)
        self.remove_btn.clicked.connect(self.remove_product_by_id)

        btn_layout.addWidget(self.submit_btn)
        btn_layout.addWidget(self.remove_btn)

        layout.addWidget(self.remove_label)
        layout.addWidget(self.product_dropdown)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def load_products(self):
        """
        Fill the dropdown with (name + price) labels but store product ID.
        """
        self.product_dropdown.clear()
        products = db_manager.get_all_products_with_id()
        for pid, name, price in products:
            display = f"{name} (₹{price})"
            self.product_dropdown.addItem(display, pid)

    def add_product(self):
        name = self.name_input.text().strip()
        price_text = self.price_input.text().strip()

        try:
            if not name or not price_text:
                raise ValueError("सभी फ़ील्ड आवश्यक हैं।")

            price = float(price_text)
            if price <= 0:
                raise ValueError("कीमत शून्य से अधिक होनी चाहिए।")

            success = db_manager.add_product(name, price)

            if success:
                QMessageBox.information(self, "✅ सफल", f"उत्पाद '{name}' जोड़ा गया।")
                self.load_products()  # Refresh dropdown
                self.accept()
            else:
                QMessageBox.critical(self, "❌ असफल", "उत्पाद जोड़ने में समस्या आई।")

        except ValueError as ve:
            QMessageBox.warning(self, "⚠️ अमान्य इनपुट", str(ve))
        except Exception as e:
            print("❌ Error in add_product:", e)
            QMessageBox.critical(self, "Error", str(e))

    def remove_product_by_id(self):
        if self.product_dropdown.count() == 0:
            QMessageBox.warning(self, "⚠️ कोई उत्पाद नहीं", "कोई उत्पाद हटाने के लिए उपलब्ध नहीं है।")
            return

        index = self.product_dropdown.currentIndex()
        product_id = self.product_dropdown.itemData(index)
        product_name = self.product_dropdown.currentText()

        confirm = QMessageBox.question(self, "पुष्टि करें",
                                       f"क्या आप '{product_name}' को हटाना चाहते हैं?",
                                       QMessageBox.Yes | QMessageBox.No)

        if confirm == QMessageBox.Yes:
            success = db_manager.delete_product_by_id(product_id)
            if success:
                QMessageBox.information(self, "✅ हटाया गया", f"'{product_name}' हटा दिया गया।")
                self.load_products()
            else:
                QMessageBox.warning(self, "❌ असफल", f"'{product_name}' को हटाया नहीं जा सका।")
