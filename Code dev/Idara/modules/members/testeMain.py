from PyQt6.QtWidgets import QApplication
from member_profile import MemberProfile
import sys

app = QApplication(sys.argv)
window = MemberProfile(1, None)
window.show()
sys.exit(app.exec())



