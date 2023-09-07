import random
import time



from PyQt5 import QtCore
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap, QIcon, QPainter
from PyQt5.QtWidgets import  QApplication,QMainWindow

from . import settings
from .model import Pet

class DesktopPet(QMainWindow):
    """桌宠核心类"""

    def __init__(self):
        super(DesktopPet, self).__init__(None)
        self.pet=Pet()
        self.initUI()
        self.play()


    def initUI(self):
        self.desktop = QApplication.desktop()
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )
        self.move(settings.INIT_POS_X,settings.INIT_POS_Y)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(settings.WINDOW_WIDTH,settings.WINDOW_HEIGHT)


    def move(self, ax: int, ay: int) -> None:
        super().move(ax,ay)
        self.pet.move(ax,ay)





    def mousePressEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        pass

    def mouseDoubleClickEvent(self, QMouseEvent):
        pass

    def closeEvent(self, QCloseEvent):
        pass

    def contextMenuEvent(self, e):
        pass

    def paintEvent(self, QPaintEvent):
        """绘图"""
        painter = QPainter(self)
        if hasattr(self, "pixmap"):
            painter.drawPixmap(self.rect(), self.pixmap)

        # painter.drawPixmap(self.rect(), self.pixmap)



    def play(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.one_action)
        self.timer.start()

    def one_action(self):
        self.timer.stop()
        action=self.pet.next_action() #type:BaseAction
        last_graph_duration=0
        for graph in action.graph_list:
            # time.sleep(graph.duration / 1000)
            self.pixmap = graph.pixmap
            print(graph)
            QApplication.processEvents()
            self.update()
            QApplication.processEvents()
            time.sleep(last_graph_duration / 1000)
            last_graph_duration=graph.duration


        print("====")

        self.timer.start()
        # self.setPix(str(self.imgDir + "/摸头_000_125.png"))


