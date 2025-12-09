import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
import AppKit
def get_application():
    argv = sys.argv
    info = AppKit.NSBundle.mainBundle().infoDictionary()
    info["LSUIElement"] = "1"
    # QApplication.setAttribute(Qt.AA_DontShowIconsInMenus, True)
    app = QApplication(argv)
    return app
