from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QTextEdit,
    QVBoxLayout, QHBoxLayout, QGridLayout, QMessageBox, QFrame
)
from PyQt5.QtCore import Qt, QTimer
from ui.all_farmers_info import ShowAllFarmersWidget
from ui.manage_account import ManageAccountWidget
from ui.show_all_report import ShowAllReportWidget
from utils.send_whatsapp_bill import send_bill_to_whatsapp
from ui.add_product import AddProductDialog
from ui.add_transaction import AddTransactionDialog
from ui.settle_account import SettleAccountDialog
from ui.bill_print import BillPrintDialog
from ui.view_history import ViewHistoryDialog
from ui.add_account import AddAccountDialog
from database import db_manager
from utils.hindi_type import get_hindi_type


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dairy Management Dashboard")#
        # self.setGeometry(200, 200, 1500, 700)
        self.setStyleSheet("font-family: 'Segoe UI'; font-size: 13pt;")
        self.init_ui()

        QTimer.singleShot(100, self.showMaximized)


    def init_ui(self):
        main_layout = QVBoxLayout()

        # Top: Account input
        account_row = QHBoxLayout()
        self.account_input = QLineEdit()
        self.account_input.setPlaceholderText("खाता नंबर दर्ज करे")
        self.account_input.returnPressed.connect(self.fetch_account_info)
        self.fetch_button = QPushButton("खाता देखे ")
        self.fetch_button.clicked.connect(self.fetch_account_info)

        account_row.addWidget(QLabel("Account No:"))
        account_row.addWidget(self.account_input)
        account_row.addWidget(self.fetch_button)

        main_layout.addLayout(account_row)
        main_layout.addWidget(self._separator())

        # Info Display
        self.name_label = QLabel("किसान का नाम: —")
        self.name_label.setStyleSheet("font-weight: bold; font-size: 12pt;")

        self.balance_label = QLabel("शेष राशि: ₹0.00")
        self.balance_label.setStyleSheet("font-weight: bold; font-size: 12pt;")

        main_layout.addWidget(self.name_label)
        main_layout.addWidget(self.balance_label)

        # 🔁 Horizontal transaction display boxes
        tx_layout = QHBoxLayout()

        left_box = QVBoxLayout()
        left_label = QLabel(" हफ़्ता :")
        self.purchase_display = QTextEdit()
        self.purchase_display.setReadOnly(True)
        self.purchase_display.setMinimumHeight(200)
        left_box.addWidget(left_label)
        left_box.addWidget(self.purchase_display)

        right_box = QVBoxLayout()
        right_label = QLabel("💵 नकद /🛒 खरीद लेनदेन / सेटलमेंट:")
        self.payment_display = QTextEdit()
        self.payment_display.setReadOnly(True)
        self.payment_display.setMinimumHeight(200)
        right_box.addWidget(right_label)
        right_box.addWidget(self.payment_display)

        tx_layout.addLayout(left_box)
        tx_layout.addLayout(right_box)
        main_layout.addLayout(tx_layout)

        # Recent Transactions Section
        recent_label = QLabel("📅 हाल के लेन-देन:")
        recent_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        self.recent_display = QTextEdit()
        self.recent_display.setReadOnly(True)
        self.recent_display.setMinimumHeight(190)
        self.recent_display.setMaximumHeight(210)
        self.recent_display.setStyleSheet("background-color: #f9f9f9;")
        main_layout.addWidget(recent_label)
        main_layout.addWidget(self.recent_display)






        main_layout.addWidget(self._separator())

        # Button Grid (same as before)
        button_grid = QGridLayout()
        button_grid.setSpacing(12)

        buttons = {
            "👨‍🌾 किसान खाता प्रबंधन": self.manage_account,
            "🛒 खरीद जोड़ें": lambda: self.open_transaction("purchase"),
            "📥 हफ़्ता जोड़ें": lambda: self.open_transaction("add_balance"),
            "💵 बाकी/नकद दी गई राशि जोड़ें": lambda: self.open_transaction("payment_give"),
            "💵 देना/नकद किसान द्वारा जोड़ें": lambda: self.open_transaction("payment_take"),
            "✅ खाता सेटल करें": self.open_settle_account,
            "📦 उत्पाद जोड़ें/हटाएं": self.open_add_product,
            "🖨️ बिल प्रिंट करें": self.open_small_bill,
            "📜 लेनदेन देखें": self.open_view_history,
            "💰  बैलेंस रिपोर्ट": self.all_farmer,
            "🗓️ रिपोर्ट दिनाँक के आधार पर": self.show_all_report,
            "📤 व्हाट्सएप बिल भेजें": self.send_whatsapp_bill,
        }

        for i, (label, func) in enumerate(buttons.items()):
            btn = QPushButton(label)
            btn.setMinimumWidth(140)
            btn.clicked.connect(func)
            button_grid.addWidget(btn, i // 4, i % 4)

        main_layout.addLayout(button_grid)
        self.setLayout(main_layout)
        self.recent_display.setText(self.recent_tnx() or "कोई हालिया लेनदेन नहीं मिला।")
    def _separator(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        return line

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
                QMessageBox.information(self, "Not Found", "किसान नहीं मिला। कृपया पहले उन्हें जोड़ें.")
                self.name_label.setText("किसान का नाम: —")
                self.balance_label.setText("शेष राशि: ₹0.00")
                self.purchase_display.clear()
                self.payment_display.clear()
                return

            name = farmer[1]
            balance = farmer[3]
            self.name_label.setText(f"किसान का नाम: {name}")
            self.balance_label.setText(f"शेष राशि: ₹{balance:.2f}")

            transactions = db_manager.get_transactions(acc_no,limit=600)
            purchase_text = ""
            payment_text = ""

            for date, t_type, product, proof, amount in transactions:


                entry = f"[{date[:16]}] | {get_hindi_type(t_type):<17} - {product or 'लेनदेन':<14} -> ₹{amount:<9} | ({proof or ' '})\n"

                if t_type == "add_balance":
                    purchase_text += entry

                elif t_type=="purchase":
                    payment_text += entry

                elif t_type=="payment_take":
                    purchase_text += entry
                elif t_type=="settled":
                    payment_text += entry
                    break
                else :
                    payment_text += entry

            self.purchase_display.setText(purchase_text or "कोई अन्य लेन-देन नहीं मिला।")
            self.payment_display.setText(payment_text or "कोई 💵 नकद /🛒 खरीद लेनदेन / सेटलमेंट: नहीं मिली।")
            self.recent_display.setText(self.recent_tnx() or "कोई हालिया लेनदेन नहीं मिला।")
        except Exception as e:
            QMessageBox.critical(self, "त्रुटि", f"जानकारी प्राप्त करते समय त्रुटि हुई:\n{str(e)}")

    def open_add_account(self):
        dialog = AddAccountDialog(self)
        dialog.exec_()

    def open_transaction(self, t_type):
        acc_no = self.get_account_no()
        if acc_no is None:
            QMessageBox.warning(self, "Invalid", "कृपया पहले एक मान्य खाता संख्या दर्ज करें।.")
            return
        dialog = AddTransactionDialog(account_no=acc_no, tx_type=t_type, parent=self)
        if dialog.exec_():
            self.fetch_account_info()

    def open_settle_account(self):
        acc_no = self.get_account_no()
        if acc_no is not None:
            dialog = SettleAccountDialog(account_no=acc_no, parent=self)
            if dialog.exec_():
                self.fetch_account_info()

    def open_add_product(self):
        dialog = AddProductDialog(self)
        dialog.exec_()

    def open_small_bill(self):
        try:
            acc_no = self.get_account_no()
            if acc_no is not None:
                dialog = BillPrintDialog(account_no=acc_no)
                dialog.exec_()
        except Exception as e:
            import traceback
            print("❌ ERROR:", traceback.format_exc())
            QMessageBox.critical(self, "Crash", f"त्रुटि:\n{str(e)}")
        # except Exception as e:
        #     QMessageBox.critical(self, "Error", f"Failed:\n{str(e)}")

    def open_view_history(self):
        acc_no = self.get_account_no()
        if acc_no is not None:
            dialog = ViewHistoryDialog(account_no=acc_no, parent=self)
            dialog.exec_()

    # def generate_report(self):
    #     try:
    #         print_balance_report()
    #         QMessageBox.information(self, "Success", "Daily report generated successfully.")
    #     except Exception as e:
    #         QMessageBox.critical(self, "Error", f"Failed to generate report:\n{str(e)}")

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
            QMessageBox.information(self, "✅ Success", f"{phone} पर बिल भेज दिया गया।")
        except Exception as e:
            QMessageBox.critical(self, "❌ Error", f"बिल भेजने में विफल:\n{str(e)}")

    def manage_account(self):
        self.manage_window = ManageAccountWidget()
        self.manage_window.show()

    def show_all_report(self):
        self.report_win = ShowAllReportWidget()
        self.report_win.show()

    def all_farmer(self):
        self.farmer_win = ShowAllFarmersWidget()
        self.farmer_win.show()



    def recent_tnx(self):
        tnx = db_manager.get_last_transactions()
        entry = ""
        for account_no, date, type, product, proof, amount in tnx:
            entry += f"AC No. {account_no:<6} | {get_hindi_type(type):<32} - {product or 'लेनदेन':<19} -> ₹{amount:<12} | ({proof or 'No Proof':<33}) [जोड़ने की दिनांक : {date[:16]}]\n"
        return entry