# ui/view_history.py

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QWidget, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt
from database import db_manager
from utils.hindi_type import get_hindi_type
from functools import partial




class ViewHistoryDialog(QDialog):
    def __init__(self, account_no, parent=None):
        super().__init__(parent)
        self.setWindowTitle("लेन-देन इतिहास")
        self.setFixedSize(1200, 600)
        self.account_no = account_no

        layout = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["दिनांक", "प्रकार", "उत्पाद", "राशि", "प्रमाण", "कार्रवाई"])

        layout.addWidget(self.table)
        self.setLayout(layout)

        self.load_data()

    def load_data(self):
        self.transactions = db_manager.get_transactions_with_id(self.account_no, limit=999)
        self.table.setRowCount(len(self.transactions))

        for row, tx in enumerate(self.transactions):
            tx_id, date, t_type, product, amount, proof = tx

            self.table.setItem(row, 0, QTableWidgetItem(date))
            self.table.setItem(row, 1, QTableWidgetItem(get_hindi_type(t_type)))
            self.table.setItem(row, 2, QTableWidgetItem(product or "लेनदेन"))
            self.table.setItem(row, 3, QTableWidgetItem(f"₹{amount:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(proof or ""))

            # Actions
            btn_widget = QWidget()
            h_layout = QHBoxLayout()
            h_layout.setContentsMargins(0, 0, 0, 0)

            edit_btn = QPushButton("बदलाव करे")
            del_btn = QPushButton("हटाएँ")

            edit_btn.clicked.connect(partial(self.edit_transaction, row))
            del_btn.clicked.connect(partial(self.delete_transaction, row))

            h_layout.addWidget(edit_btn)
            h_layout.addWidget(del_btn)
            btn_widget.setLayout(h_layout)
            self.table.setCellWidget(row, 5, btn_widget)

        self.table.resizeColumnsToContents()

    def get_transaction_id(self, row):
        if row < len(self.transactions):
            return self.transactions[row][0]
        return None

    def edit_transaction(self, row):
        try:
            tx_id = self.get_transaction_id(row)
            if tx_id:
                from ui.edit_transaction_dialog import EditTransactionDialog
                dialog = EditTransactionDialog(tx_id, self)
                if dialog.exec_():  # refresh if saved
                    self.load_data()
            else:
                QMessageBox.warning(self, "Error", "Transaction ID not found.")
        except Exception as e:
            import traceback
            print("❌ ERROR:", traceback.format_exc())
            QMessageBox.critical(self, "Crash", f"त्रुटि:\n{str(e)}")

    def delete_transaction(self, row):
        try:
            tx_id = self.get_transaction_id(row)
            if tx_id:
                reply = QMessageBox.question(self, "Confirm", "क्या आप इस लेन-देन को हटाना चाहते हैं?", QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    db_manager.delete_transaction(tx_id)
                    self.load_data()
            else:
                QMessageBox.warning(self, "Error", "Transaction ID not found.")
        except Exception as e:
            import traceback
            print("❌ ERROR:", traceback.format_exc())
            QMessageBox.critical(self, "Crash", f"त्रुटि:\n{str(e)}")