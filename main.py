import sys

from PyQt5.QtWidgets import QApplication




from  modules.ui import DesktopPet






if __name__ == '__main__':
    argv = sys.argv

    app = QApplication(argv)
    pet = DesktopPet()

    pet.show()

    sys.exit(app.exec())

