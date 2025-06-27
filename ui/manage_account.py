# from PyQt5.QtWidgets import (
#     QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
#     QPushButton, QLineEdit, QMessageBox, QLabel
# )
# from database import db_manager
#
#
# class ManageAccountWidget(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("👨‍🌾 किसान खाता प्रबंधन")
#         self.setMinimumSize(600, 400)
#         self.init_ui()
#         self.load_accounts()
#
#     def init_ui(self):
#         layout = QVBoxLayout()
#
#         # --- इनपुट फॉर्म ---
#         form_layout = QHBoxLayout()
#         self.account_input = QLineEdit()
#         self.account_input.setPlaceholderText("खाता नंबर")
#         self.name_input = QLineEdit()
#         self.name_input.setPlaceholderText("किसान का नाम")
#         self.phone_input = QLineEdit()
#         self.phone_input.setPlaceholderText("फोन नंबर")
#
#         form_layout.addWidget(QLabel("खाता नंबर:"))
#         form_layout.addWidget(self.account_input)
#         form_layout.addWidget(QLabel("नाम:"))
#         form_layout.addWidget(self.name_input)
#         form_layout.addWidget(QLabel("फोन:"))
#         form_layout.addWidget(self.phone_input)
#
#         layout.addLayout(form_layout)
#
#         # --- बटन ---
#         button_layout = QHBoxLayout()
#         self.add_btn = QPushButton("➕ जोड़ें")
#         self.edit_btn = QPushButton("✏️ संशोधन")
#         self.delete_btn = QPushButton("🗑️ हटाएं")
#
#         self.add_btn.clicked.connect(self.add_account)
#         self.edit_btn.clicked.connect(self.edit_account)
#         self.delete_btn.clicked.connect(self.delete_account)
#
#         button_layout.addWidget(self.add_btn)
#         button_layout.addWidget(self.edit_btn)
#         button_layout.addWidget(self.delete_btn)
#
#         layout.addLayout(button_layout)
#
#         # --- तालिका ---
#         self.table = QTableWidget()
#         self.table.setColumnCount(3)
#         self.table.setHorizontalHeaderLabels(["खाता नंबर", "किसान का नाम", "फोन नंबर"])
#         self.table.cellClicked.connect(self.populate_fields)
#         layout.addWidget(self.table)
#
#         self.setLayout(layout)
#
#     def load_accounts(self):
#         self.table.setRowCount(0)
#         farmers = db_manager.get_all_farmers()
#         for row, farmer in enumerate(farmers):
#             self.table.insertRow(row)
#             self.table.setItem(row, 0, QTableWidgetItem(str(farmer["account_no"])))
#             self.table.setItem(row, 1, QTableWidgetItem(farmer["name"]))
#             self.table.setItem(row, 2, QTableWidgetItem(farmer["phone"] or ""))
#
#     def populate_fields(self, row, column):
#         self.account_input.setText(self.table.item(row, 0).text())
#         self.name_input.setText(self.table.item(row, 1).text())
#         self.phone_input.setText(self.table.item(row, 2).text())
#
#     def add_account(self):
#         acc = self.account_input.text().strip()
#         name = self.name_input.text().strip()
#         phone = self.phone_input.text().strip()
#
#         if not acc.isdigit() or not name:
#             QMessageBox.warning(self, "⚠️ त्रुटि", "कृपया सही खाता नंबर और नाम दर्ज करें।")
#             return
#
#         acc = int(acc)
#         if db_manager.get_farmer(acc):
#             QMessageBox.warning(self, "⚠️ मौजूद है", f"खाता नंबर {acc} पहले से मौजूद है।")
#             return
#
#         if db_manager.add_farmer_manual(acc, name, phone):
#             QMessageBox.information(self, "✅ सफल", f"खाता {acc} जोड़ दिया गया।")
#             self.load_accounts()
#         else:
#             QMessageBox.critical(self, "❌ असफल", "खाता जोड़ने में त्रुटि हुई।")
#
#     def edit_account(self):
#         acc = self.account_input.text().strip()
#         name = self.name_input.text().strip()
#         phone = self.phone_input.text().strip()
#
#         if not acc.isdigit() or not name:
#             QMessageBox.warning(self, "⚠️ त्रुटि", "कृपया सही खाता नंबर और नाम दर्ज करें।")
#             return
#
#         acc = int(acc)
#         if not db_manager.get_farmer(acc):
#             QMessageBox.warning(self, "🔍 नहीं मिला", f"खाता {acc} मौजूद नहीं है।")
#             return
#
#         if db_manager.update_farmer(acc, name, phone):
#             QMessageBox.information(self, "✅ अपडेट", f"खाता {acc} अपडेट कर दिया गया।")
#             self.load_accounts()
#         else:
#             QMessageBox.critical(self, "❌ असफल", "खाता अपडेट करने में त्रुटि हुई।")
#
#     def delete_account(self):
#         acc = self.account_input.text().strip()
#         if not acc.isdigit():
#             QMessageBox.warning(self, "⚠️ त्रुटि", "कृपया सही खाता नंबर दर्ज करें।")
#             return
#
#         acc = int(acc)
#         confirm = QMessageBox.question(self, "पुष्टि करें", f"क्या आप खाता {acc} हटाना चाहते हैं?",
#                                        QMessageBox.Yes | QMessageBox.No)
#         if confirm == QMessageBox.Yes:
#             if db_manager.delete_farmer(acc):
#                 QMessageBox.information(self, "✅ हटाया गया", f"खाता {acc} हटा दिया गया।")
#                 self.load_accounts()
#             else:
#                 QMessageBox.critical(self, "❌ असफल", "खाता हटाने में त्रुटि हुई।")

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox
)
from PyQt5.QtGui import QFont
from database import db_manager  # ensure your db_manager has required functions


class ManageAccountWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("👨‍🌾 किसान खाता प्रबंधन")
        self.setMinimumSize(450, 350)
        self.current_action = "add"  # default
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        font = QFont("Arial", 11)

        # --- Action Buttons ---
        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("➕ जोड़ें")
        self.edit_btn = QPushButton("✏️ संशोधित करें")
        self.delete_btn = QPushButton("🗑️ हटाएं")

        for btn in [self.add_btn, self.edit_btn, self.delete_btn]:
            btn.setFont(font)
            button_layout.addWidget(btn)

        self.add_btn.clicked.connect(lambda: self.set_action("add"))
        self.edit_btn.clicked.connect(lambda: self.set_action("edit"))
        self.delete_btn.clicked.connect(lambda: self.set_action("delete"))

        layout.addLayout(button_layout)

        # --- Account No Input ---
        self.account_input = QLineEdit()
        self.account_input.setPlaceholderText("खाता नंबर")
        self.account_input.setFont(font)
        self.account_input.textChanged.connect(self.autofill_fields)

        layout.addWidget(self.create_label("खाता नंबर:", font))
        layout.addWidget(self.account_input)

        # --- Name Input ---
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("किसान का नाम")
        self.name_input.setFont(font)
        layout.addWidget(self.create_label("नाम:", font))
        layout.addWidget(self.name_input)

        # --- Phone Input ---
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("फोन नंबर")
        self.phone_input.setFont(font)
        layout.addWidget(self.create_label("फोन नंबर:", font))
        layout.addWidget(self.phone_input)

        # --- Action Button ---
        self.action_btn = QPushButton("✅ कार्रवाई करें")
        self.action_btn.setFont(font)
        self.action_btn.clicked.connect(self.perform_action)
        layout.addWidget(self.action_btn)

        self.setLayout(layout)
        self.set_action("add")  # default mode

    def create_label(self, text, font):
        label = QLabel(text)
        label.setFont(font)
        return label

    def set_action(self, action_type):
        """Set current action and adjust UI based on action."""
        self.current_action = action_type

        if action_type == "delete":
            self.name_input.setReadOnly(True)
            self.phone_input.setReadOnly(True)
        else:
            self.name_input.setReadOnly(False)
            self.phone_input.setReadOnly(False)

        self.name_input.show()
        self.phone_input.show()

        self.clear_fields()

        self.action_btn.setText({
            "add": "✅ किसान जोड़ें",
            "edit": "🔄 अपडेट करें",
            "delete": "❌ खाता हटाएं"
        }[action_type])

    def autofill_fields(self):
        """Auto-fill name and phone from account number."""
        acc = self.account_input.text().strip()
        if not acc.isdigit():
            self.name_input.clear()
            self.phone_input.clear()
            return

        farmer = db_manager.get_farmer(int(acc))
        if farmer:
            self.name_input.setText(farmer["name"])
            self.phone_input.setText(farmer["phone"] or "")
        else:
            self.name_input.clear()
            self.phone_input.clear()

    def perform_action(self):
        acc = self.account_input.text().strip()
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()

        if not acc.isdigit():
            QMessageBox.warning(self, "⚠️ त्रुटि", "कृपया सही खाता नंबर दर्ज करें।")
            return

        acc = int(acc)

        if self.current_action == "add":
            if not name:
                QMessageBox.warning(self, "⚠️ त्रुटि", "कृपया नाम दर्ज करें।")
                return
            if db_manager.get_farmer(acc):
                QMessageBox.warning(self, "⚠️ मौजूद है", f"खाता {acc} पहले से मौजूद है।")
                return
            if db_manager.add_farmer_manual(acc, name, phone):
                QMessageBox.information(self, "✅ सफल", f"खाता {acc} जोड़ दिया गया।")
                self.clear_fields()
            else:
                QMessageBox.critical(self, "❌ असफल", "खाता जोड़ने में त्रुटि हुई।")

        elif self.current_action == "edit":
            if not name:
                QMessageBox.warning(self, "⚠️ त्रुटि", "कृपया नाम दर्ज करें।")
                return
            if not db_manager.get_farmer(acc):
                QMessageBox.warning(self, "🔍 नहीं मिला", f"खाता {acc} मौजूद नहीं है।")
                return
            if db_manager.update_farmer(acc, name, phone):
                QMessageBox.information(self, "✅ अपडेट", f"खाता {acc} अपडेट कर दिया गया।")
                self.clear_fields()
            else:
                QMessageBox.critical(self, "❌ असफल", "अपडेट करने में त्रुटि हुई।")

        elif self.current_action == "delete":
            confirm = QMessageBox.question(self, "पुष्टि करें", f"क्या आप खाता {acc} हटाना चाहते हैं?",
                                           QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                if db_manager.delete_farmer(acc):
                    QMessageBox.information(self, "✅ हटाया गया", f"खाता {acc} हटा दिया गया।")
                    self.clear_fields()
                else:
                    QMessageBox.critical(self, "❌ असफल", "हटाने में त्रुटि हुई।")

    def clear_fields(self):
        self.account_input.clear()
        self.name_input.clear()
        self.phone_input.clear()
