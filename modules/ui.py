import random
import time

from PyQt5 import QtCore
from PyQt5.QtCore import QTimer, Qt, QPoint,QThread,pyqtSignal
from PyQt5.QtGui import QPainter,QColor
from PyQt5.QtWidgets import QApplication, QMainWindow

from . import settings
from .model import Pet
from .dict import ActionType


class DesktopPet(QMainWindow):
    """桌宠核心类"""

    def __init__(self):
        super(DesktopPet, self).__init__(None)

        self.initUI()

        self.last_graph_duration = 0
        self.draggable = False

        # 长按也能触发提起
        self.long_press_timer = QTimer()  #QTimer竟然仍然在主线程处理
        self.long_press_timer.setInterval(500)
        self.long_press_timer.timeout.connect(self.on_long_press)

        self.play()

    def initUI(self):
        self.desktop = QApplication.desktop()
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )
        self.move(QPoint(settings.INIT_POS_X, settings.INIT_POS_Y))
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)

    def move(self, a0: QtCore.QPoint) -> None:
        super().move(a0)
        # 撞墙

    def on_long_press(self):
        print("long_press")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.long_press_timer.start()
            self.draggable = True
            self.offset = event.pos()
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.draggable = False
            self.long_press_timer.stop()

    def mouseMoveEvent(self, event):
        print("move")
        if self.draggable:
            self.move(event.globalPos() - self.offset)
            event.accept()

    def mouseDoubleClickEvent(self, QMouseEvent):
        pass

    def closeEvent(self, QCloseEvent):
        pass

    def contextMenuEvent(self, e):
        pass

    def paintEvent(self, QPaintEvent):
        """绘图"""

        if hasattr(self, "pixmap"):
            painter = QPainter(self)
            painter.drawPixmap(self.rect(), self.pixmap)


    def play(self):
        self.action_thread = PetThread()
        self.action_thread.signal.connect(self.one_action)
        self.action_thread.start()





    def one_action(self,pixmap):
        self.pixmap=pixmap
        self.update()


class PetThread(QThread):
    signal = pyqtSignal(object)
    def __init__(self):
        super().__init__()
        self.pet=Pet()




    def run(self):
        while True:
            action = self.pet.next_action()  # type:BaseAction
            print(action)
            if self.pet.action_count==1:
                time.sleep(0.3)  #感觉像是什么东西没有加载完全？总之添加这个可以有效解决第一个图片有边缘覆盖不了的问题
            for graph in action.graph_list:  # 如何立刻中断这里的动画，或者说需要打断这里吗？暂时不打断
                pixmap = graph.pixmap
                self.signal.emit(pixmap)
                QThread.msleep(graph.duration)






