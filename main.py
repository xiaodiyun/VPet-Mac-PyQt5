import sys

from modules.share import app




from  modules.ui import DesktopPet
import traceback


def exception_hook(type, value, tb):

    traceback.print_exception(type, value, tb)

    # 退出应用程序
    sys.exit(1)




if __name__ == '__main__':
    sys.excepthook = exception_hook
    pet = DesktopPet()

    pet.show()

    sys.exit(app.exec_())

