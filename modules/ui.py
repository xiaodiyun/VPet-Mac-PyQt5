import random
import time



from PyQt5 import QtCore
from PyQt5.QtCore import QTimer, Qt,QPoint
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import  QApplication,QMainWindow

from . import settings
from .model import Pet
from .dict import ActionType

class DesktopPet(QMainWindow):
    """桌宠核心类"""

    def __init__(self):
        super(DesktopPet, self).__init__(None)
        self.pet=Pet()
        self.initUI()
        self.play()
        self.last_graph_duration = 0
        self.draggable=False


        #长按也能触发提起
        self.long_press_timer = QTimer()
        self.long_press_timer.setInterval(500)
        self.long_press_timer.timeout.connect(self.on_long_press)


    def initUI(self):
        self.desktop = QApplication.desktop()
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )
        self.move(QPoint(settings.INIT_POS_X,settings.INIT_POS_Y))
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(settings.WINDOW_WIDTH,settings.WINDOW_HEIGHT)


    def move(self, a0: QtCore.QPoint) -> None:
        super().move(a0)
        #撞墙

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

    def mouseMoveEvent(self, event): #采样频率太低了，弃用
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
        painter = QPainter(self)
        if hasattr(self, "pixmap"):
            painter.drawPixmap(self.rect(), self.pixmap)




    def play(self):
        self.action_timer = QTimer(self)
        self.action_timer.timeout.connect(self.one_action)
        self.action_timer.start() #是否要改成随机，待测试



    def one_action(self):
        self.action_timer.stop()
        action=self.pet.next_action() #type:BaseAction
        # if action.action_type==ActionType.MOVE:

        for graph in action.graph_list: #如何立刻中断这里的动画，或者说需要打断这里吗？暂时不打断
            self.pixmap = graph.pixmap
            QApplication.processEvents()
            self.update()
            QApplication.processEvents()
            time.sleep(self.last_graph_duration / 1000) #因为sleep的存在，所以move应当单独
            self.last_graph_duration=graph.duration




        self.action_timer.start()


"""
交互：

- 跟qwindow的事件回调
    ui操作宠物 - 拖文件过去，播放吃的动作，回调移动文件脚本
    ui操作宠物 - 拖动移动，播放raise动画
    hover，不知道干啥
    ui操作宠物 - 点击，播放touch动画
    ui操作宠物 - 走到屏幕边缘时，中断walk动画，播放climb动画
    

- 跟机器的事件监控
    监控操作宠物 - 放音乐时，播放music动作
    监控操作宠物 - 电脑休眠时，播放sleep动作
    监控操作宠物 - 使用pycharm时，播放work动作
    监控操作宠物 - 机器接受到麦克风声响时，播放say动作

可能需要一个中间的触发器
"""

