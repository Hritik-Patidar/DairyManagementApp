# ui/view_history.py

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit
from database import db_manager

class ViewHistoryDialog(QDialog):
    def __init__(self, account_no, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Full Transaction History")
        self.setFixedSize(600, 500)

        layout = QVBoxLayout()
        self.text = QTextEdit()
        self.text.setReadOnly(True)

        history = db_manager.get_transactions(account_no, limit=999)
        content = ""
        for tx in history:
            date, t_type, product, amount, proof = tx
            content += f"{date} - {t_type.upper()} - {product or ''} - ₹{amount} - {proof or ''}\n"

        self.text.setText(content or "No transactions found.")
        layout.addWidget(self.text)
        self.setLayout(layout)
