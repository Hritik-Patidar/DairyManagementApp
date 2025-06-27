# ui/view_history.py

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit
from database import db_manager

class ViewHistoryDialog(QDialog):
    def __init__(self, account_no, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Full Transaction History")
        self.setFixedSize(700, 600)

        layout = QVBoxLayout()
        self.text = QTextEdit()
        self.text.setReadOnly(True)

        history = db_manager.get_transactions(account_no, limit=999)
        content = ""
        for tx in history:
            date, t_type, product, amount, proof = tx
            content += f"{date} - {self.get_hindi_type(t_type)} - {product or ''} - ₹{amount} - {proof or ''}\n"

        self.text.setText(content or "No transactions found.")
        layout.addWidget(self.text)
        self.setLayout(layout)
    def get_hindi_type(self, tx_type):
        return {
            "purchase": "खरीद",
            "payment_give": "नकद दी गई राशि",
            "payment_take": "नकद किसान द्वारा",
            "add_balance": "हफ़्ता",
            "settled": "सेटल"
        }.get(tx_type, tx_type)