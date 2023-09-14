import sys

from modules.share import app




from  modules.ui import DesktopPet







if __name__ == '__main__':


    pet = DesktopPet()

    pet.show()

    sys.exit(app.exec_())

