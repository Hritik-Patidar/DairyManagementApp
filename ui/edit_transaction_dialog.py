# ui/edit_transaction_dialog.py

from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QPushButton, QDialogButtonBox, QMessageBox
)
from database import db_manager


class EditTransactionDialog(QDialog):
    def __init__(self, tx_id, parent=None):
        super().__init__(parent)
        self.tx_id = tx_id
        self.setWindowTitle("लेन-देन संपादित करें")
        self.setFixedSize(400, 300)

        tx = db_manager.get_transaction_by_id(tx_id)
        if not tx:
            QMessageBox.critical(self, "Error", "लेन-देन नहीं मिला!")
            self.reject()
            return

        # Fixed unpacking
        _, self.account_no, self.date, self.t_type, self.product_name, self.amount, self.proof = tx

        layout = QFormLayout()

        self.product_input = QLineEdit(self.product_name)
        self.amount_input = QLineEdit(str(self.amount))
        self.proof_input = QLineEdit(self.proof or "")

        layout.addRow("उत्पाद:", self.product_input)
        layout.addRow("राशि:", self.amount_input)
        layout.addRow("प्रमाण:", self.proof_input)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.save_changes)
        self.buttons.rejected.connect(self.reject)

        layout.addWidget(self.buttons)
        self.setLayout(layout)

    def save_changes(self):
        try:
            product = self.product_input.text()
            amount = float(self.amount_input.text())
            proof = self.proof_input.text()

            db_manager.update_transaction(self.tx_id, product, amount, proof)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save: {str(e)}")
