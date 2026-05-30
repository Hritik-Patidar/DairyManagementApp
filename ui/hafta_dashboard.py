from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QDateEdit, QMessageBox, QHeaderView
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor, QPalette
from database.db_manager import calculate_hafta, fetch_hafta_summary


class HaftaWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dairy Hafta Calculation")
        self.setMinimumWidth(950)
        self.showMaximized()
        self.setup_ui()
        self.apply_styles()

    # ---------------- UI Setup ---------------- #
    def setup_ui(self):
        title = QLabel("🧮 Hafta Calculation Panel")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2E8B57; margin-bottom: 10px;")

        # --- Inputs ---
        self.acc_label = QLabel("Account No (optional):")
        self.acc_input = QLineEdit()
        self.acc_input.setPlaceholderText("Enter account number (optional)")

        self.from_label = QLabel("From Date:")
        self.from_date = QDateEdit(calendarPopup=True)
        self.from_date.setDate(QDate.currentDate().addDays(-9))

        self.to_label = QLabel("To Date:")
        self.to_date = QDateEdit(calendarPopup=True)
        self.to_date.setDate(QDate.currentDate())


        calendar1 = self.from_date.calendarWidget()
        calendar2 = self.to_date.calendarWidget()

        # Apply style to popup calendar text color
        calendar_style = """
                QCalendarWidget QAbstractItemView {
                    color: white;            /* Text color */
                    background-color: #2d2d2d; /* Background color */
                    selection-background-color: #2d2d2d; /* Selected date background */
                    selection-color: white;  /* Selected text color */
                }
                QCalendarWidget QWidget#qt_calendar_navigationbar {
                    background-color: #444444;
                }
                QCalendarWidget QToolButton {
                    color: white;
                    background: transparent;
                }
                """

        calendar1.setStyleSheet(calendar_style)
        calendar2.setStyleSheet(calendar_style)
        # --- Buttons ---
        self.show_btn = QPushButton("📊 Show Hafta")
        self.calc_btn = QPushButton("💰 Calculate Now")

        # --- Table (6 columns now) ---
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["Account No", "Avg Fat", "Avg CLR", "Avg Rate", "Quantity", "Total Amount"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setFont(QFont("Segoe UI", 11))

        # --- Layouts ---
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.acc_label)
        input_layout.addWidget(self.acc_input)
        input_layout.addWidget(self.from_label)
        input_layout.addWidget(self.from_date)
        input_layout.addWidget(self.to_label)
        input_layout.addWidget(self.to_date)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.show_btn)
        button_layout.addWidget(self.calc_btn)

        main_layout = QVBoxLayout()
        main_layout.addWidget(title)
        main_layout.addLayout(input_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.table)

        self.setLayout(main_layout)

        # --- Signals ---
        self.show_btn.clicked.connect(self.on_show_hafta)
        self.calc_btn.clicked.connect(self.on_calculate_hafta)

    # ---------------- Style Setup ---------------- #
    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f9f9f9;
                font-family: "Segoe UI";
                font-size: 12pt;
            }
            QLabel {
                color: #333;
                font-weight: 500;
            }
            QLineEdit, QDateEdit {
                border: 1px solid #aaa;
                border-radius: 6px;
                padding: 6px;
                background-color: #fff;
            }
            QPushButton {
                background-color: #2E8B57;
                color: white;
                padding: 8px 16px;
                font-size: 13pt;
                font-weight: 600;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #3CB371;
            }
            QTableWidget {
                background-color: #fff;
                border: 1px solid #ccc;
                gridline-color: #ddd;
                alternate-background-color: #f2f2f2;
            }
            QHeaderView::section {
                background-color: #2E8B57;
                color: white;
                font-size: 13pt;
                padding: 4px;
            }
        """)

    # ---------------- Helper Methods ---------------- #
    def get_inputs(self):
        acc_no = self.acc_input.text().strip()
        acc_no = int(acc_no) if acc_no else None
        from_date = self.from_date.date().toString("yyyy-MM-dd")
        to_date = self.to_date.date().toString("yyyy-MM-dd")
        return acc_no, from_date, to_date

    # ---------------- Events ---------------- #
    def on_show_hafta(self):
        acc_no, from_date, to_date = self.get_inputs()
        data = fetch_hafta_summary(from_date, to_date, acc_no)
        self.populate_table(data)

    def on_calculate_hafta(self):
        acc_no, from_date, to_date = self.get_inputs()
        data = calculate_hafta(from_date, to_date, acc_no)
        if data:
            QMessageBox.information(self, "✅ Success", "Hafta calculated and saved successfully!")
        else:
            QMessageBox.warning(self, "⚠️ No Data", "No eligible entries found for calculation.")
        self.populate_table(data)

    # ---------------- Table Fill ---------------- #
    def populate_table(self, data):
        self.table.setRowCount(0)
        if not data:
            self.table.setRowCount(1)
            self.table.setItem(0, 0, QTableWidgetItem("No data found for selected range"))
            return

        for row_idx, row_data in enumerate(data):
            self.table.insertRow(row_idx)
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_idx, col_idx, item)
