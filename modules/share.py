import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

def get_application():
    argv = sys.argv
    # QApplication.setAttribute(Qt.AA_DontShowIconsInMenus, True)
    app = QApplication(argv)
    return app
