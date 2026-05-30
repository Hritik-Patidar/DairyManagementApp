from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import QMessageBox, QPushButton
from database import db_manager
from database.db_manager import make_entry


class DailyCollectionDashboard(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧾 Dairy Milk Collection Dashboard")
        self.showMaximized()
        self.setStyleSheet("background-color: #f3f6f9; font-family: 'Segoe UI';")
        self.setup_ui()

    def setup_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(20)

        # -------- HEADER --------
        header = QtWidgets.QLabel("🐄 दैनिक दूध संकलन (Daily Milk Collection)")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("font-size: 28px; font-weight: bold; color: #2e7d32;")
        main_layout.addWidget(header)

        # -------- CONTENT (Form + Table) --------
        content_layout = QtWidgets.QHBoxLayout()
        content_layout.setSpacing(25)
        content_layout.setStretch(0, 65)  # left form area
        content_layout.setStretch(1, 35)  # right table area

        # -------- LEFT FORM PANEL --------
        form_box = QtWidgets.QFrame()
        form_box.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 16px;
                border: 1px solid #ccc;
                padding: 35px;
            }
            QLabel {
                font-size: 17px;
                font-weight: 600;
            }
            QLineEdit, QComboBox, QDateEdit {
                font-size: 17px;
                padding: 10px;
                border-radius: 6px;
                border: 1px solid #ccc;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
                border: 1px solid #4CAF50;
                background: #f7fff7;
            }
        """)
        form_layout = QtWidgets.QGridLayout(form_box)
        form_layout.setHorizontalSpacing(30)
        form_layout.setVerticalSpacing(18)

        style_box = "min-height:36px; font-size:17px;"

        # -------- Input Fields --------
        self.date = QtWidgets.QDateEdit()
        self.date.setCalendarPopup(True)
        self.date.setDate(QDate.currentDate())
        self.date.setStyleSheet(style_box)

        self.shift = QtWidgets.QComboBox()
        self.shift.addItems(["Morning", "Evening"])
        self.shift.setStyleSheet(style_box)

        self.account_no = QtWidgets.QLineEdit(); self.account_no.setPlaceholderText("Account No")
        self.name = QtWidgets.QLineEdit(); self.name.setReadOnly(True)
        self.qty = QtWidgets.QLineEdit(); self.qty.setPlaceholderText("Litres")
        self.fat = QtWidgets.QLineEdit(); self.fat.setPlaceholderText("Fat %")
        self.clr = QtWidgets.QLineEdit(); self.clr.setPlaceholderText("CLR")
        self.rate = QtWidgets.QLineEdit(); self.rate.setReadOnly(True)
        self.total = QtWidgets.QLineEdit(); self.total.setReadOnly(True)
        self.type = QtWidgets.QComboBox(); self.type.addItems(["Cow", "Buffalo"])

        for field in [self.account_no, self.name, self.qty, self.fat, self.clr, self.rate, self.total]:
            field.setStyleSheet(style_box)
        self.type.setStyleSheet(style_box)

        # --- Layout (2 columns) ---
        row = 0
        def add_row(label, widget1, label2=None, widget2=None):
            nonlocal row
            form_layout.addWidget(QtWidgets.QLabel(label), row, 0)
            form_layout.addWidget(widget1, row, 1)
            if label2:
                form_layout.addWidget(QtWidgets.QLabel(label2), row, 2)
                form_layout.addWidget(widget2, row, 3)
            row += 1

        add_row("Date:", self.date, "Shift:", self.shift)
        add_row("Account No:", self.account_no, "Name:", self.name)
        add_row("Quantity (L):", self.qty, "Fat %:", self.fat)
        add_row("CLR:", self.clr, "Rate ₹/L:", self.rate)
        add_row("Total ₹:", self.total, "Type:", self.type)

        # --- Submit button ---
        self.submit_btn = QtWidgets.QPushButton("💾 Save Entry")
        self.submit_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #2e7d32;
                color: white;
                font-size: 18px;
                font-weight: bold;
                padding: 12px 24px;
                border-radius: 10px;
            }
            QPushButton:hover { background-color: #256428; }
        """)
        form_layout.addWidget(self.submit_btn, row, 0, 1, 4, alignment=Qt.AlignCenter)

        # -------- RIGHT TABLE PANEL --------
        table_box = QtWidgets.QFrame()
        table_box.setStyleSheet("""
            QFrame { background: white; border-radius: 16px; border:1px solid #ccc; padding: 20px; }
            QLabel { font-size:18px; font-weight:bold; color:#1e88e5; }
            QHeaderView::section { background:#f0f0f0; padding:8px; border: none; }
        """)
        table_layout = QtWidgets.QVBoxLayout(table_box)
        table_layout.setSpacing(10)

        lbl = QtWidgets.QLabel("📊 Today’s Records")
        lbl.setAlignment(Qt.AlignCenter)
        table_layout.addWidget(lbl)

        self.table = QtWidgets.QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(["Date", "Shift", "Qty", "Fat", "CLR", "Rate", "Total ₹", "Type"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("font-size:15px; background:#fafafa; gridline-color:#ddd;")
        self.table.setAlternatingRowColors(True)
        table_layout.addWidget(self.table)

        # -------- Combine panels --------
        content_layout.addWidget(form_box)
        content_layout.addWidget(table_box)
        main_layout.addLayout(content_layout)

        # -------- BOTTOM PANEL --------
        bottom_box = QtWidgets.QFrame()
        bottom_box.setStyleSheet("""
            QFrame { background: white; border-radius: 14px; border:1px solid #ccc; padding:20px; }
            QLabel { font-size:17px; font-weight:600; }
            QLineEdit { font-size:17px; border:1px solid #ccc; border-radius:6px; padding:8px; background:#f9f9f9; }
        """)
        bottom_layout = QtWidgets.QHBoxLayout(bottom_box)
        bottom_layout.setSpacing(25)

        self.back_btn = QPushButton("◀️ Back")
        self.back_btn.clicked.connect(self.close)
        self.back_btn.setStyleSheet("background:#ddd; font-weight:600; padding:8px 15px; border-radius:8px;")
        bottom_layout.addWidget(self.back_btn, alignment=Qt.AlignLeft)

        self.total_litre = QtWidgets.QLineEdit(); self.total_litre.setReadOnly(True)
        self.total_amount = QtWidgets.QLineEdit(); self.total_amount.setReadOnly(True)
        self.avg_rate = QtWidgets.QLineEdit(); self.avg_rate.setReadOnly(True)

        bottom_layout.addWidget(QtWidgets.QLabel("Total Litre:")); bottom_layout.addWidget(self.total_litre)
        bottom_layout.addWidget(QtWidgets.QLabel("Total Amount ₹:")); bottom_layout.addWidget(self.total_amount)
        bottom_layout.addWidget(QtWidgets.QLabel("Avg Rate ₹/L:")); bottom_layout.addWidget(self.avg_rate)

        main_layout.addWidget(bottom_box)

        # ---------- Connections ----------
        self.account_no.textChanged.connect(self.fetch_name)
        self.qty.textChanged.connect(self.calculate_total)
        self.fat.textChanged.connect(self.calculate_rate)
        self.clr.textChanged.connect(self.calculate_rate)
        self.submit_btn.clicked.connect(self.submit_data)

        # ---------- Focus & Shortcuts ----------
        self.account_no.returnPressed.connect(lambda: self.qty.setFocus())
        self.qty.returnPressed.connect(lambda: self.fat.setFocus())
        self.fat.returnPressed.connect(lambda: self.clr.setFocus())
        self.clr.returnPressed.connect(self.submit_data)

    # ---------------- LOGIC ----------------
    def fetch_name(self):
        try:
            acc = self.account_no.text().strip()
            if not acc or not acc.isdigit():
                self.name.clear()
                return
            data = db_manager.get_farmer_main(int(acc))
            if data:
                self.name.setText(data[1])
                milk_type = data[4]
                if milk_type == "C":
                    self.type.setCurrentText("Cow")
                elif milk_type == "B":
                    self.type.setCurrentText("Buffalo")
            else:
                self.name.clear()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def calculate_rate(self):
        try:
            if not self.fat.text() or not self.clr.text():
                self.rate.clear()
                return
            rate = db_manager.get_rate_by_fat_clr(float(self.fat.text()), float(self.clr.text()))
            if rate:
                self.rate.setText(f"{float(rate):.2f}")
                self.calculate_total()
        except Exception as e:
            print("Rate error:", e)

    def calculate_total(self):
        try:
            if not self.qty.text() or not self.rate.text():
                self.total.clear()
                return
            total = float(self.qty.text()) * float(self.rate.text())
            self.total.setText(f"{total:.2f}")
        except:
            self.total.clear()

    def submit_data(self):
        try:
            qty = float(self.qty.text())
            rate = float(self.rate.text())
            total = float(self.total.text())
        except:
            QMessageBox.warning(self, "Invalid", "Please enter valid numeric values.")
            return

        date_str = self.date.date().toString("yyyy-MM-dd")
        shift = "M" if self.shift.currentText() == "Morning" else "E"
        milk_type = "C" if self.type.currentText() == "Cow" else "B"

        # Database में save करें (मान लें account_no fix है या कोई input field है)
        account_no = int(self.account_no.text())  # अगर UI में field है
        result = make_entry(account_no, qty, float(self.fat.text()), int(self.clr.text()),
                  rate, total, date_str, shift, milk_type)
        # check result
        if isinstance(result, Exception):
            if "UNIQUE constraint failed" in str(result):
                QMessageBox.warning(self, "Duplicate Entry ⚠️",
                                    "This account already has an entry for this date and shift.")
            else:
                QMessageBox.critical(self, "Database Error", f"Error inserting data:\n{result}")
            return

        # Table widget
        row = self.table.rowCount()
        self.table.insertRow(row)
        values = [
            date_str, shift, self.qty.text(), self.fat.text(), self.clr.text(),
            self.rate.text(), self.total.text(), self.type.currentText()
        ]
        for col, val in enumerate(values):
            self.table.setItem(row, col, QtWidgets.QTableWidgetItem(val))


        total_l = sum(float(self.table.item(i, 2).text()) for i in range(self.table.rowCount()))
        total_a = sum(float(self.table.item(i, 6).text()) for i in range(self.table.rowCount()))
        self.total_litre.setText(f"{total_l:.2f}")
        self.total_amount.setText(f"{total_a:.2f}")
        self.avg_rate.setText(f"{(total_a / total_l):.2f}" if total_l else "0.00")

        # Fields clear
        for field in [self.qty, self.fat, self.clr, self.rate, self.total]:
            field.clear()
        self.qty.setFocus()

        QMessageBox.information(self, "Saved ✅", "Entry added successfully!")


# ---------- Run ----------
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = DailyCollectionDashboard()
    w.show()
    sys.exit(app.exec_())
