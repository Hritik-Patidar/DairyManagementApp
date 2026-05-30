from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit,
    QVBoxLayout, QHBoxLayout, QGridLayout, QMessageBox, QFrame, QAction
)
from PyQt5.QtCore import Qt, QTimer
from ui.all_farmers_info import ShowAllFarmersWidget
from ui.manage_account import ManageAccountWidget
from ui.daily_entry import DailyCollectionDashboard
from ui.rateChartManage import RateChartManager
from ui.show_all_report_of_hafta import ShowAllReportWidget
from ui.show_indiv_farmer_entry_widget import FarmerEntryWidget
from utils.send_whatsapp_bill import send_bill_to_whatsapp
from ui.add_product import AddProductDialog
from ui.add_transaction import AddTransactionDialog
from ui.settle_account import SettleAccountDialog
from ui.bill_print import BillPrintDialog
from ui.view_history import ViewHistoryDialog
from ui.add_account import AddAccountDialog
from ui.show_all_far_report_by_date import ShowAllFarmersReportWidget
from ui.hafta_dashboard import HaftaWidget
from database import db_manager
from utils.hindi_type import get_hindi_type


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🐄 Dairy Management Dashboard")
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f4f6f9;
                font-family: 'Segoe UI';
            }
            QLabel {
                color: #2b2b2b;
                font-size: 20px;
            }
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 19px;
                background: white;
            }
            QPushButton {
                background: #2e7d32;
                color: white;
                font-weight: bold;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 19px;
            }
            QPushButton:hover { background: #256428; }
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 6px;
                background: #ffffff;
                font-size: 19px;
                line-height: 1.5;
                padding: 8px;
            }
            QMenuBar {
                background: #2e7d32;
                color: white;
                font-weight: 600;
                font-size: 18px;
            }
            QMenuBar::item:selected {
                background: #256428;
            }
        """)
        QTimer.singleShot(100, self.showMaximized)
        self.init_ui()

    def init_ui(self):
        # ---------- Central Layout ----------
        central = QWidget()
        self.setCentralWidget(central)
        self.main_layout = QVBoxLayout(central)
        self.main_layout.setContentsMargins(30, 20, 30, 20)
        self.main_layout.setSpacing(15)

        # ---------- Menu ----------
        self._setup_menu()

        # ---------- Title ----------
        title = QLabel("🐮 डेयरी प्रबंधन डैशबोर्ड")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:28px; font-weight:700; color:#1b5e20; margin-bottom:10px;")
        self.main_layout.addWidget(title)

        # ---------- Account Input ----------
        account_row = QHBoxLayout()
        account_row.setSpacing(10)
        acc_label = QLabel("खाता नंबर:")
        acc_label.setStyleSheet("font-weight:600; font-size:19px;")
        self.account_input = QLineEdit()
        self.account_input.setPlaceholderText("खाता नंबर दर्ज करें...")
        self.account_input.returnPressed.connect(self.fetch_account_info)

        fetch_button = QPushButton("🔍 खाता देखे")
        fetch_button.clicked.connect(self.fetch_account_info)

        account_row.addWidget(acc_label)
        account_row.addWidget(self.account_input)
        account_row.addWidget(fetch_button)
        self.main_layout.addLayout(account_row)
        self.main_layout.addWidget(self._separator())

        # ---------- Info Labels ----------
        info_row = QHBoxLayout()
        self.name_label = QLabel("किसान का नाम: —")
        self.name_label.setStyleSheet("font-weight:bold; font-size:19px; color:#1b5e20;")
        self.balance_label = QLabel("शेष राशि: ₹0.00")
        self.balance_label.setStyleSheet("font-weight:bold; font-size:22px; color:#b71c1c;")
        info_row.addWidget(self.name_label)
        info_row.addStretch()
        info_row.addWidget(self.balance_label)
        self.main_layout.addLayout(info_row)

        # ---------- Transaction Section ----------
        tx_layout = QHBoxLayout()
        tx_layout.setSpacing(20)

        left_box = QVBoxLayout()
        left_label = QLabel("📦 हफ़्ता विवरण:")
        left_label.setStyleSheet("font-weight:bold; font-size:19px;")
        self.purchase_display = QTextEdit()
        self.purchase_display.setReadOnly(True)
        self.purchase_display.setMinimumHeight(220)
        left_box.addWidget(left_label)
        left_box.addWidget(self.purchase_display)

        right_box = QVBoxLayout()
        right_label = QLabel("💵 नकद / 🛒 खरीद / सेटलमेंट:")
        right_label.setStyleSheet("font-weight:bold; font-size:19px;")
        self.payment_display = QTextEdit()
        self.payment_display.setReadOnly(True)
        self.payment_display.setMinimumHeight(220)
        right_box.addWidget(right_label)
        right_box.addWidget(self.payment_display)

        tx_layout.addLayout(left_box, 1)
        tx_layout.addLayout(right_box, 1)
        self.main_layout.addLayout(tx_layout)

        # ---------- Recent Transactions ----------
        self.main_layout.addWidget(self._separator())
        recent_label = QLabel("📅 हाल के लेनदेन:")
        recent_label.setStyleSheet("font-weight:bold; font-size:17px; margin-top:10px;")
        self.recent_display = QTextEdit()
        self.recent_display.setReadOnly(True)
        self.recent_display.setMinimumHeight(200)
        self.recent_display.setStyleSheet("background-color:#fafafa; border:1px solid #ccc; border-radius:8px;")
        self.main_layout.addWidget(recent_label)
        self.main_layout.addWidget(self.recent_display)
        self.main_layout.addWidget(self._separator())

        # ---------- Buttons Grid ----------
        button_grid = QGridLayout()
        button_grid.setSpacing(15)
        button_style = """
            QPushButton {
                background: #43a047;
                color: white;
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 19px;
                font-weight: 600;
            }
            QPushButton:hover { background: #388e3c; }
        """

        buttons = {
            "🧾 खरीद जोड़ें": lambda: self.open_transaction("purchase"),
            "💰 हफ़्ता जोड़ें": lambda: self.open_transaction("add_balance"),
            "📤 बाकी/नकद दी गई राशि": lambda: self.open_transaction("payment_give"),
            "📥 किसान से नकद प्राप्त": lambda: self.open_transaction("payment_take"),
            "✅ खाता सेटल करें": self.open_settle_account,
            "🧺 उत्पाद जोड़ें/हटाएं": self.open_add_product,
            "📜 लेनदेन प्रबंधन": self.open_view_history,
            "🖨️ बिल प्रिंट करें": self.open_small_bill,
        }

        for i, (label, func) in enumerate(buttons.items()):
            btn = QPushButton(label)
            btn.setStyleSheet(button_style)
            btn.clicked.connect(func)
            btn.setMinimumWidth(180)
            button_grid.addWidget(btn, i // 4, i % 4)
        self.main_layout.addLayout(button_grid)

        # ---------- Load Initial Transactions ----------
        self.recent_display.setText(self.recent_tnx() or "कोई हालिया लेनदेन नहीं मिला।")

    # ---------- Menubar ----------
    def _setup_menu(self):
        menubar = self.menuBar()
        menubar.setStyleSheet("QMenu { background:#f5f5f5; font-size:19px; } QMenu::item:selected { background:#c8e6c9; }")

        entry_menu = menubar.addMenu(" डेयरी संकलन ")
        entry_menu.addAction("संकलन शुरू करें", self.start_entry)
        entry_menu.addAction("संकलन हफ़्ता डैशबोर्ड", self.show_hafta_dashboard)
        entry_menu.addAction("संकलन रिपोर्ट", self.open_farmers_report)
        entry_menu.addAction("1 किसान रिपोर्ट संकलन रिपोर्ट", self.on_show_indivi_far_entry)

        report_menu = menubar.addMenu("हफ़्ता रिपोर्ट रजिस्टर ")
        report_menu.addAction("1 किसान रिपोर्ट", self.show_all_report)
        report_menu.addAction("बैलेंस रिपोर्ट", self.all_farmer)

        rate_menu = menubar.addMenu("रेट चार्ट")
        rate_menu.addAction("रेट चार्ट प्रबंधन", self.open_rate_chart)

        account_menu = menubar.addMenu("👤 खाता प्रबंधन")
        account_menu.addAction("किसान खाता प्रबंधन", self.manage_account)

    # ---------- Utilities ----------
    def _separator(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color:#ccc; margin:10px 0;")
        return line



    # ---------- Functional Methods ----------
    def get_account_no(self):
        acc = self.account_input.text().strip()
        return int(acc) if acc.isdigit() else None

    def fetch_account_info(self):
        try:
            acc_no = self.get_account_no()
            if acc_no is None:
                QMessageBox.warning(self, "Invalid", "कृपया सही खाता संख्या दर्ज करें.")
                return

            farmer = db_manager.get_farmer_main(acc_no)
            if not farmer:
                QMessageBox.information(self, "Not Found", "किसान नहीं मिला। कृपया पहले उन्हें जोड़ें।")
                self.name_label.setText("किसान का नाम: —")
                self.balance_label.setText("शेष राशि: ₹0.00")
                self.purchase_display.clear()
                self.payment_display.clear()
                return

            name = farmer[1]
            hindiname=farmer[6]
            balance = farmer[3]
            self.balance = balance
            self.name_label.setText(f"किसान का नाम: {name} | {hindiname}")
            self.balance_label.setText(f"शेष राशि: ₹{balance:.2f}")

            transactions = db_manager.get_transactions(acc_no, limit=600)
            purchase_text = ""
            payment_text = ""
            purchase_amount = 0
            payment_amount = 0

            for date, t_type, product, proof, amount in transactions:
                entry = f"[{date[:16]}] | {get_hindi_type(t_type):<17} - {product or 'लेनदेन':<14} -> ₹{amount:<9} | ({proof or ' '})\n"
                if t_type == "add_balance":
                    purchase_text += entry
                    purchase_amount += amount
                elif t_type == "purchase":
                    payment_text += entry
                    payment_amount += amount
                elif t_type == "payment_take":
                    purchase_text += entry
                    purchase_amount += amount
                elif t_type == "settled":
                    payment_text += entry
                    break
                else:
                    payment_text += entry
                    payment_amount += amount

            purchase_text += f"----------------------------------------------\n :-> योगफल :₹{purchase_amount} "
            payment_text += f"----------------------------------------------\n :-> योगफल :₹{payment_amount} "
            self.purchase_display.setText(purchase_text or "कोई अन्य लेन-देन नहीं मिला।")
            self.payment_display.setText(payment_text or "कोई  नकद /🛒 खरीद लेनदेन / सेटलमेंट: नहीं मिली।")
            self.recent_display.setText(self.recent_tnx() or "कोई हालिया लेनदेन नहीं मिला।")
        except Exception as e:
            QMessageBox.critical(self, "त्रुटि", f"जानकारी प्राप्त करते समय त्रुटि हुई:\n{str(e)}")

    def recent_tnx(self):
        tnx = db_manager.get_last_transactions(limit=200)
        entry = ""
        for account_no, date, type, product, proof, amount in tnx:
            entry += f"AC No. {account_no:<6} | {get_hindi_type(type):<32} - {product or 'लेनदेन':<19} -> ₹{amount:<12} | ({proof or 'No Proof':<33}) [जोड़ने की दिनांक : {date[:16]}]\n"
        return entry

    # ---------- Open Dialogs ----------
    def start_entry(self):
        self.dash = DailyCollectionDashboard()
        self.dash.setWindowModality(Qt.ApplicationModal)
        self.dash.show()

    def open_add_account(self):
        dialog = AddAccountDialog(self)
        dialog.setModal(True)
        dialog.exec_()

    def open_transaction(self, t_type):
        acc_no = self.get_account_no()
        if acc_no is None:
            QMessageBox.warning(self, "Invalid", "कृपया पहले एक मान्य खाता संख्या दर्ज करें।")
            return
        dialog = AddTransactionDialog(account_no=acc_no, tx_type=t_type, parent=self)
        if dialog.exec_():
            self.fetch_account_info()

    def open_settle_account(self):
        acc_no = self.get_account_no()
        balance = getattr(self, "balance", 0)
        if acc_no is not None:
            dialog = SettleAccountDialog(account_no=acc_no, balance=balance, parent=self)
            if dialog.exec_():
                self.fetch_account_info()

    def open_add_product(self):
        dialog = AddProductDialog(self)
        dialog.setModal(True)
        dialog.exec_()

    def open_small_bill(self):
        try:
            acc_no = self.get_account_no()
            if acc_no is not None:
                dialog = BillPrintDialog(account_no=acc_no)
                dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Crash", f"त्रुटि:\n{str(e)}")

    def open_view_history(self):
        try:
            acc_no = self.get_account_no()
            if acc_no is not None:
                dialog = ViewHistoryDialog(account_no=acc_no, parent=self)
                dialog.setModal(True)
                dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Crash", f"त्रुटि:\n{str(e)}")

    def send_whatsapp_bill(self):
        acc_no = self.get_account_no()
        if acc_no is None:
            QMessageBox.warning(self, "Invalid", "कृपया एक मान्य खाता संख्या दर्ज करें।")
            return
        farmer = db_manager.get_farmer(acc_no)
        if not farmer:
            QMessageBox.warning(self, "Not Found", "किसान नहीं मिला। कृपया पहले खाता जोड़ें।")
            return
        phone = farmer['phone']
        if not phone or len(phone.strip()) < 10:
            QMessageBox.warning(self, "Missing", "इस किसान के पास वैध फ़ोन नंबर उपलब्ध नहीं है।")
            return
        try:
            send_bill_to_whatsapp(acc_no, phone)
            QMessageBox.information(self, " Success", f"{phone} पर बिल भेज दिया गया।")
        except Exception as e:
            QMessageBox.critical(self, " Error", f"बिल भेजने में विफल:\n{str(e)}")

    def manage_account(self):
        self.manage_window = ManageAccountWidget()
        self.manage_window.setWindowModality(Qt.ApplicationModal)
        self.manage_window.show()

    def show_all_report(self):
        self.report_win = ShowAllReportWidget()
        self.report_win.setWindowModality(Qt.ApplicationModal)
        self.report_win.show()

    def all_farmer(self):
        self.farmer_win = ShowAllFarmersWidget()
        self.farmer_win.setWindowModality(Qt.ApplicationModal)
        self.farmer_win.show()

    def open_farmers_report(self):
        self.report_window = ShowAllFarmersReportWidget()
        self.report_window.setWindowModality(Qt.ApplicationModal)  # Main window lock
        self.report_window.show()

    def show_hafta_dashboard(self):
        self.window = HaftaWidget()
        self.window.setWindowModality(Qt.ApplicationModal)
        self.window.show()
    def open_rate_chart(self):
        self.win = RateChartManager()
        self.win.setWindowModality(Qt.ApplicationModal)
        self.win.show()
    def on_show_indivi_far_entry(self):
        self.wid=FarmerEntryWidget()
        self.wid.setWindowModality(Qt.ApplicationModal)
        self.wid.show()