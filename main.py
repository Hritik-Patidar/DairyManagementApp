# main.py
import sys
from pyinstrument import Profiler
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
# ✅ Import and setup DB before launching UI
from database.db_setup import setup_database, DB_PATH

# Ensure the /data directory exists
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Call setup to create tables if missing
setup_database()





if __name__ == "__main__":
    profiler = Profiler()
    profiler.start()
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(e)
    finally:
        pass
        # profiler.stop()
        # profiler.open_in_browser()
