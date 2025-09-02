
# main.py
import sys
import os
from PyQt6.QtWidgets import QApplication
from controller.app_controller import AppController

def main():
    app = QApplication(sys.argv)

    # Resolve caminho absoluto do arquivo .qss
    base_dir = os.path.dirname(os.path.abspath(__file__))
    qss_path = os.path.join(base_dir, "config", "styles.qss")

    if os.path.exists(qss_path):
        with open(qss_path, "r") as f:
            app.setStyleSheet(f.read())
    else:
        print(f"⚠️ File not find in: {qss_path}")

    window = AppController()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Error on start app: {e}")
