from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox
)
from PyQt5.QtGui import QFont
from database import db_manager

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
        self.name_input.setPlaceholderText("किसान का नाम अंग्रेजी में")
        self.name_input.setFont(font)
        layout.addWidget(self.create_label("नाम:", font))
        layout.addWidget(self.name_input)

        self.hindiname_input = QLineEdit()
        self.hindiname_input.setPlaceholderText("किसान का नाम हिंदी में")
        self.hindiname_input.setFont(font)
        layout.addWidget(self.create_label("नाम हिंदी में:", font))
        layout.addWidget(self.hindiname_input)

        # --- Phone Input ---
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("फोन नंबर")
        self.phone_input.setFont(font)
        layout.addWidget(self.create_label("फोन नंबर:", font))
        layout.addWidget(self.phone_input)
        #type of milk
        self.milk_type = QLineEdit()
        self.milk_type.setPlaceholderText("दूध का प्रकार")
        self.milk_type.setFont(font)
        layout.addWidget(self.create_label("दूध का प्रकार", font))
        layout.addWidget(self.milk_type)

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
        try:
            acc = self.account_input.text().strip()
            if not acc.isdigit():
                self.name_input.clear()
                self.hindiname_input.clear()
                self.phone_input.clear()
                self.milk_type.clear()
                return

            farmer = db_manager.get_farmer(int(acc))
            if farmer:
                self.name_input.setText(farmer["name"])
                self.phone_input.setText(farmer["phone"] or "")
                self.milk_type.setText(farmer["milk_type"] or "")
                self.hindiname_input.setText(farmer["hindiname"] or "")
            else:
                self.name_input.clear()
                self.hindiname_input.clear()
                self.phone_input.clear()
                self.milk_type.clear()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to save rates:\n{e}")


    def perform_action(self):
        acc = self.account_input.text().strip()
        name = self.name_input.text().strip()
        hindiname = self.hindiname_input.text().strip()
        phone = self.phone_input.text().strip()
        fmilk_type=self.milk_type.text().strip()

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
            if db_manager.add_farmer_manual(acc, name, phone,fmilk_type,hindiname):
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
            if db_manager.update_farmer(acc, name, phone,hindiname):
                QMessageBox.information(self, "✅ अपडेट", f"खाता {acc} अपडेट कर दिया गया।")
                self.clear_fields()
            else:
                QMessageBox.critical(self, "❌ असफल", "अपडेट करने में त्रुटि हुई।")

        elif self.current_action == "delete":
            confirm = QMessageBox.question(self, "पुष्टि करें", f"क्या आप खाता {acc} हटाना चाहते हैं?",
                                         QMessageBox.Yes | QMessageBox.No)

            include_tx = QMessageBox.question(self, "पुष्टि करें", f"क्या आप खाता {acc} के लेनदेन भी हटाना चाहते हैं?",
                                           QMessageBox.Yes | QMessageBox.No)

            if include_tx == QMessageBox.Yes:
                if db_manager.delete_farmer(acc,with_tx=True):
                    QMessageBox.information(self, "✅ हटाया गया", f"खाता {acc} का लेनदेन भी हटा दिया गया।")
                    self.clear_fields()
                else:
                    QMessageBox.critical(self, "❌ असफल", "हटाने में त्रुटि हुई।")

            elif confirm == QMessageBox.Yes:
                if db_manager.delete_farmer(acc):
                    QMessageBox.information(self, "✅ हटाया गया", f"खाता {acc} हटा दिया गया।")
                    self.clear_fields()
                else:
                    QMessageBox.critical(self, "❌ असफल", "हटाने में त्रुटि हुई।")

    def clear_fields(self):
        self.account_input.clear()
        self.name_input.clear()
        self.phone_input.clear()



