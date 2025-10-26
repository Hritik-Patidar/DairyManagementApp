from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt
from database import db_manager


class RateChartManager(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🐄 Rate Chart Manager")
        self.showMaximized()
        self.setStyleSheet("background:#f4f6f9; font-family:'Segoe UI';")
        self.setup_ui()

    def setup_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(40, 25, 40, 25)
        main_layout.setSpacing(15)

        # ---------- Header ----------
        title = QtWidgets.QLabel("💰 Milk Rate Chart Manager")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size:30px;
            font-weight:700;
            color:#1b5e20;
        """)
        main_layout.addWidget(title)

        # ---------- Top Controls ----------
        top_bar = QtWidgets.QHBoxLayout()
        top_bar.setSpacing(10)

        lbl = QtWidgets.QLabel("Milk Type:")
        lbl.setStyleSheet("font-size:16px; font-weight:600; color:#333; margin-right:6px;")

        self.milk_type = QtWidgets.QComboBox()
        self.milk_type.addItems(["Cow", "Buffalo"])
        self.milk_type.setFixedWidth(200)
        self.milk_type.setStyleSheet("""
            QComboBox {
                background:white;
                border:1px solid #ccc;
                border-radius:6px;
                padding:6px 10px;
                font-size:16px;
            }
            QComboBox:hover { border-color:#2e7d32; }
        """)

        # Buttons
        self.load_btn = QtWidgets.QPushButton("🔄 Load Rates")
        self.save_btn = QtWidgets.QPushButton("💾 Save Changes")
        self.back_btn = QtWidgets.QPushButton("⬅ Back")

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
        btn_gray = """
            QPushButton {
                background:#9e9e9e;
                color:white;
                font-size:16px;
                font-weight:bold;
                border-radius:6px;
                padding:8px 20px;
            }
            QPushButton:hover { background:#7d7d7d; }
        """

        self.load_btn.setStyleSheet(btn_green)
        self.save_btn.setStyleSheet(btn_green)
        self.back_btn.setStyleSheet(btn_gray)

        top_bar.addWidget(lbl)
        top_bar.addWidget(self.milk_type)
        top_bar.addStretch()
        top_bar.addWidget(self.load_btn)
        top_bar.addWidget(self.save_btn)
        top_bar.addWidget(self.back_btn)
        main_layout.addLayout(top_bar)

        # ---------- Table ----------
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Fat %", "CLR 25", "CLR 26", "CLR 27", "CLR 28"])
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        # Table Style
        self.table.setStyleSheet("""
            QTableWidget {
                background:white;
                alternate-background-color:#f9f9f9;
                font-size:18px;
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

        # Header resizing: proportionally stretch
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        for i in range(1, 5):
            header.setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)
        header.setDefaultAlignment(Qt.AlignCenter)

        # Center table in layout
        table_container = QtWidgets.QHBoxLayout()
        table_container.addWidget(self.table)
        main_layout.addLayout(table_container, stretch=1)

        # ---------- Connect ----------
        self.load_btn.clicked.connect(self.load_data)
        self.save_btn.clicked.connect(self.save_data)
        self.back_btn.clicked.connect(self.close)

        # Default load
        self.load_data()

    # ---------- Logic ----------
    def load_data(self):
        self.table.setRowCount(0)
        milk_type = self.milk_type.currentText()

        if milk_type == "Cow":
            fat_start, fat_end = 3.3, 5.5
        else:
            fat_start, fat_end = 5.6, 10.0

        clr_values = [25, 26, 27, 28]
        fat = fat_start
        row = 0

        while fat <= fat_end + 0.001:
            self.table.insertRow(row)
            fat_item = QtWidgets.QTableWidgetItem(f"{fat:.1f}")
            fat_item.setFlags(fat_item.flags() & ~Qt.ItemIsEditable)
            fat_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, fat_item)

            for j, clr in enumerate(clr_values):
                rate = db_manager.get_rate_by_fat_clr(fat, clr)
                cell = QtWidgets.QTableWidgetItem(f"{rate:.2f}" if rate else "")
                cell.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, j + 1, cell)

            fat += 0.1
            fat = round(fat, 1)
            row += 1

    def save_data(self):
        clr_values = [25, 26, 27, 28]
        try:
            for i in range(self.table.rowCount()):
                fat = float(self.table.item(i, 0).text())
                for j, clr in enumerate(clr_values):
                    cell = self.table.item(i, j + 1)
                    if cell and cell.text().strip():
                        try:
                            rate = float(cell.text())
                            db_manager.update_or_insert_rate(fat, clr, rate)
                        except ValueError:
                            pass

            QtWidgets.QMessageBox.information(self, "✅ Saved", "Rates updated successfully!")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to save rates:\n{e}")
