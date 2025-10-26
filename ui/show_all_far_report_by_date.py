# ui/show_all_farmers_report.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QDateEdit, QMessageBox, QSizePolicy
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from database import db_manager
import sqlite3


class ShowAllFarmersReportWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📊 Farmers Report (Avg Fat/CLR/Rate & Total Amount)")
        self.showMaximized()
        self.setStyleSheet("background:#f4f6f9; font-family:'Segoe UI';")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 25, 40, 25)
        layout.setSpacing(20)

        # ---------- Title ----------
        title = QLabel("🐄 Farmers Report (Average Fat / CLR / Rate & Total Amount)")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size:28px;
            font-weight:700;
            color:#1b5e20;
        """)
        layout.addWidget(title)

        # ---------- Date selection ----------
        date_layout = QHBoxLayout()
        date_layout.setSpacing(10)

        lbl_style = "font-size:16px; font-weight:600; color:#333;"
        date_edit_style = """
            QDateEdit {
                background:white;
                border:1px solid #ccc;
                border-radius:6px;
                padding:6px 10px;
                font-size:16px;
                min-width:130px;
            }
            QDateEdit:hover { border-color:#2e7d32; }
        """

        lbl_from = QLabel("From:")
        lbl_from.setStyleSheet(lbl_style)
        lbl_to = QLabel("To:")
        lbl_to.setStyleSheet(lbl_style)

        self.from_date = QDateEdit(QDate.currentDate())
        self.from_date.setCalendarPopup(True)
        self.from_date.setStyleSheet(date_edit_style)

        self.to_date = QDateEdit(QDate.currentDate())
        self.to_date.setCalendarPopup(True)
        self.to_date.setStyleSheet(date_edit_style)

        # Buttons
        self.load_button = QPushButton("🔄 Load Report")
        self.print_btn = QPushButton("🖨️ Print Report")

        btn_green = """
            QPushButton {
                background:#2e7d32;
                color:white;
                font-size:16px;
                font-weight:bold;
                border-radius:6px;
                padding:8px 20px;
            }
            QPushButton:hover { background:#256428; }
        """

        self.load_button.setStyleSheet(btn_green)
        self.print_btn.setStyleSheet(btn_green)

        date_layout.addWidget(lbl_from)
        date_layout.addWidget(self.from_date)
        date_layout.addWidget(lbl_to)
        date_layout.addWidget(self.to_date)
        date_layout.addStretch()
        date_layout.addWidget(self.load_button)
        date_layout.addWidget(self.print_btn)
        layout.addLayout(date_layout)

        # ---------- Table ----------
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Account No", "Name", "Milk Type", "Avg Fat", "Avg CLR",
            "Avg Rate ₹/L", "Total Qty (L)", "Total Amount ₹"
        ])
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Table styling
        self.table.setStyleSheet("""
            QTableWidget {
                background:white;
                alternate-background-color:#f9f9f9;
                font-size:17px;
                gridline-color:#d0d0d0;
                border:1px solid #ccc;
                border-radius:8px;
            }
            QHeaderView::section {
                background:#dce4dc;
                color:#1b5e20;
                padding:8px;
                border:none;
                font-weight:700;
                font-size:17px;
            }
            QTableWidget::item {
                padding:5px;
            }
        """)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, self.table.horizontalHeader().ResizeToContents)
        for i in range(1, 8):
            header.setSectionResizeMode(i, self.table.horizontalHeader().Stretch)
        header.setDefaultAlignment(Qt.AlignCenter)

        layout.addWidget(self.table, stretch=1)

        # ---------- Connections ----------
        self.load_button.clicked.connect(self.load_report)
        self.print_btn.clicked.connect(self.print_report)

    # ---------- Load Report ----------
    def load_report(self):
        try:
            from_date = self.from_date.date().toString("dd-MM-yyyy")
            to_date = self.to_date.date().toString("dd-MM-yyyy")

            conn = sqlite3.connect(db_manager.DB_PATH)
            cursor = conn.cursor()

            query = """
            SELECT f.account_no, f.name, f.milk_type,
                AVG(d.fat) as avg_fat,
                AVG(d.clr) as avg_clr,
                AVG(d.rate) as avg_rate,
                SUM(d.quantity) as total_qty,
                SUM(d.total_amount) as total_amount
            FROM DailyEntry d
            JOIN farmers f ON f.account_no = d.account_no
            WHERE date BETWEEN ? AND ?
            GROUP BY f.account_no, f.name, f.milk_type
            ORDER BY f.account_no
            """
            cursor.execute(query, (from_date, to_date))
            records = cursor.fetchall()
            conn.close()

            self.table.setRowCount(0)
            for row_idx, row_data in enumerate(records):
                self.table.insertRow(row_idx)
                for col_idx, val in enumerate(row_data):
                    if isinstance(val, float):
                        val = f"{val:.2f}"
                    item = QTableWidgetItem(str(val))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row_idx, col_idx, item)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load report:\n{str(e)}")

    # ---------- Print ----------
    def print_report(self):
        try:
            printer = QPrinter(QPrinter.HighResolution)
            printer.setPageSize(QPrinter.A4)
            printer.setOrientation(QPrinter.Portrait)

            dialog = QPrintDialog(printer, self)
            if dialog.exec_() == QPrintDialog.Accepted:
                self.table.render(dialog.printer())
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Printing failed:\n{str(e)}")
