# ui/bill_print.py

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QTextEdit,
    QPushButton, QFileDialog, QMessageBox, QHBoxLayout
)
from database import db_manager
from utils.thermal_printer import print_report

class BillPrintDialog(QDialog):
    def __init__(self, account_no, parent=None):
        super().__init__(parent)
        self.account_no = account_no
        self.setWindowTitle("Bill Preview")
        self.setFixedSize(500, 500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.text = QTextEdit()
        self.text.setReadOnly(True)

        farmer = db_manager.get_farmer(self.account_no)
        transactions = db_manager.get_transactions(self.account_no, limit=50)

        bill_text = f"Farmer: {farmer['name']}\nAccount No: {self.account_no}\nPhone: {farmer['phone']}\nBalance: ₹{farmer['balance']:.2f}\n\n"
        bill_text += "Recent Transactions:\n----------------------\n"

        for t in transactions:
            date, t_type, product, amount, proof = t
            bill_text += f"{date} - {t_type.upper()} - {product or 'लेनदेन'} - ₹{amount} - {proof or ' '}\n"

        self.text.setText(bill_text)
        self.farmer = farmer
        self.transactions = transactions

        # ✅ Buttons
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("💾 Save as TXT")
        self.print_btn = QPushButton("🖨️ Print Receipt")

        self.save_btn.clicked.connect(self.save_txt)
        self.print_btn.clicked.connect(self.print_receipt)

        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.print_btn)

        layout.addWidget(self.text)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def save_txt(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Bill", f"bill_{self.account_no}.txt", "Text Files (*.txt)")
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.text.toPlainText())
            QMessageBox.information(self, "Saved", f"Bill saved to {path}")

    def print_receipt(self):
        try:
            print_report(
                account_no=self.account_no,
                farmer_name=self.farmer['name'],
                phone=self.farmer['phone'],
                transactions=db_manager.get_transactions(self.account_no),
                balance=self.farmer['balance'],
                notfull=True
            )
            QMessageBox.information(self, "Printed", "Receipt sent to thermal printer.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to print receipt.\n{str(e)}")
