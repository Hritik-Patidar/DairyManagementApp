from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import QMessageBox, QPushButton, QHeaderView
from database import db_manager
from database.db_manager import make_entry


class DailyCollectionDashboard(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧾 Dairy Milk Collection Dashboard")
        self.showMaximized()
        self.setStyleSheet("background-color: #f2f5f9; font-family: 'Segoe UI';")
        self.setup_ui()

    def setup_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(20)

        # -------- HEADER --------
        header = QtWidgets.QLabel("🐄 दैनिक दूध संकलन (Daily Milk Collection)")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #1b5e20;
            background: #e8f5e9;
            padding: 10px;
            border-radius: 8px;
        """)
        main_layout.addWidget(header)

        # -------- CONTENT --------
        content_layout = QtWidgets.QHBoxLayout()
        content_layout.setSpacing(25)
        content_layout.setStretch(0, 55)
        content_layout.setStretch(1, 45)

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
        form_layout.setHorizontalSpacing(25)
        form_layout.setVerticalSpacing(15)

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
            QFrame {
                background: white;
                border-radius: 16px;
                border: 1px solid #ccc;
                padding: 10px;
            }
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #1565c0;
            }
        """)

        table_layout = QtWidgets.QVBoxLayout(table_box)
        table_layout.setSpacing(5)
        table_layout.setContentsMargins(15, 10, 15, 10)

        lbl = QtWidgets.QLabel("📊 Records for Selected Date & Shift")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("""
            background: #e3f2fd;
            border-radius: 8px;
            padding: 8px;
            font-size: 19px;
            font-weight: 600;
        """)
        table_layout.addWidget(lbl)
        self.table = QtWidgets.QTableWidget(0, 10)
        self.table.setHorizontalHeaderLabels([
            "Account No", "Date", "Shift", "Qty (L)", "Fat", "CLR",
            "Rate ₹/L", "Total ₹", "Type", "Action"
        ])
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background: #ffffff;
                font-size: 16px;
                gridline-color: #ccc;
                border: none;
            }
            QHeaderView::section {
                background-color: #1976d2;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border: none;
                padding: 8px;
                height:60px;
            }
            QTableWidget::item {
                padding: 6px;
            }
        """)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setVisible(True)
        table_layout.addWidget(self.table)

        # -------- Combine Panels --------
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
        self.date.dateChanged.connect(self.load_previous_records)
        self.shift.currentIndexChanged.connect(self.load_previous_records)

        self.account_no.returnPressed.connect(lambda: self.qty.setFocus())
        self.qty.returnPressed.connect(lambda: self.fat.setFocus())
        self.fat.returnPressed.connect(lambda: self.clr.setFocus())
        self.clr.returnPressed.connect(self.submit_data)
        # initial load
        self.load_previous_records()

    # ---------------- LOGIC ----------------
    def fetch_name(self):
        try:
            acc = self.account_no.text().strip()
            if not acc.isdigit():
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

        date_str = self.date.date().toString("dd-MM-yyyy")
        shift = "M" if self.shift.currentText() == "Morning" else "E"
        milk_type = "C" if self.type.currentText() == "Cow" else "B"

        try:
            account_no = int(self.account_no.text())
        except:
            QMessageBox.warning(self, "Invalid", "Enter valid Account Number.")
            return

        result = make_entry(account_no, qty, float(self.fat.text()), int(self.clr.text()),
                            rate, total, date_str, shift, milk_type)
        if isinstance(result, Exception):
            if "UNIQUE constraint failed" in str(result):
                QMessageBox.warning(self, "Duplicate Entry ⚠️",
                                    "This account already has an entry for this date and shift.")
            else:
                QMessageBox.critical(self, "Database Error", f"Error inserting data:\n{result}")
            return

        QMessageBox.information(self, "Saved ✅", "Entry added successfully!")
        self.load_previous_records()

        for field in [self.account_no,self.name,self.qty, self.fat, self.clr, self.rate, self.total]:
            field.clear()
        self.account_no.setFocus()

    def load_previous_records(self):
        try:
            date_str = self.date.date().toString("dd-MM-yyyy")
            shift = "M" if self.shift.currentText() == "Morning" else "E"
            records = db_manager.get_entries_by_date_shift(date_str, shift)
            self.table.setRowCount(0)

            from functools import partial

            for row_data in records:
                entry_id = row_data[0]
                row = self.table.rowCount()
                self.table.insertRow(row)
                for col, val in enumerate(row_data[1:]):
                    self.table.setItem(row, col, QtWidgets.QTableWidgetItem(str(val)))

                del_btn = QtWidgets.QPushButton("🗑 Delete")
                del_btn.setCursor(Qt.PointingHandCursor)
                del_btn.setStyleSheet("color:white; background:#e53935; border-radius:6px; padding:4px 10px;")
                del_btn.clicked.connect(partial(self.delete_record, entry_id))
                self.table.setCellWidget(row, 9, del_btn)

            if records:
                total_l = sum(float(r[4]) for r in records)
                total_a = sum(float(r[8]) for r in records)
                self.total_litre.setText(f"{total_l:.2f}")
                self.total_amount.setText(f"{total_a:.2f}")
                self.avg_rate.setText(f"{(total_a / total_l):.2f}" if total_l else "0.00")
            else:
                self.total_litre.setText("0.00")
                self.total_amount.setText("0.00")
                self.avg_rate.setText("0.00")
        except Exception as e:
            print(e)

    def delete_record(self, entry_id):
        confirm = QMessageBox.question(self, "Confirm Delete",
                                       "Are you sure you want to delete this record?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            db_manager.delete_entry(entry_id)
            QMessageBox.information(self, "Deleted ✅", "Record deleted successfully.")
            self.load_previous_records()


# ---------- Run ----------
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = DailyCollectionDashboard()
    w.show()
    sys.exit(app.exec_())
