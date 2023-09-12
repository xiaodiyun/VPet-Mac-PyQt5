import random
import time

from PyQt6 import QtCore
from PyQt6.QtCore import QTimer, QPoint,QThread,pyqtSignal,Qt
from PyQt6.QtGui import QPainter,QColor,QCursor,QPen,QBrush
from PyQt6.QtWidgets import QApplication, QMainWindow

from . import settings
from .model import Pet
from .dict import ActionType,ActionStatus,AnimatType




class DesktopPet(QMainWindow):
    """桌宠核心类"""

    def __init__(self):
        super(DesktopPet, self).__init__(None)

        self.initUI()


        self.pet=Pet()

        # 长按也能触发提起
        self.long_press_timer = QTimer()
        self.long_press_timer.setSingleShot(True)
        self.long_press_timer.setInterval(500)
        self.long_press_timer.timeout.connect(self.raise_pet)

        self.raise_thread=None

        self.drag_flag=False
        # self.long_press_flag=False
        self.play()

    def initUI(self):
        # self.desktop = QApplication.instance().screens()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        self.move(QPoint(settings.INIT_POS_X, settings.INIT_POS_Y))
        # self.setAttribute(Qt.WindowTranslucentBackground)
        # self.setWindowOpacity(0)
        self.setStyleSheet("background-color: transparent;")
        self.resize(settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)

    def move(self, a0: QtCore.QPoint) -> None:
        super().move(a0)
        # 撞墙

    def raise_pet(self):



        rel_cursor_pos=self.mapFromGlobal(QCursor.pos())
        abs_window_pos=self.pos()
        #346*346 203*86
        x=int(-settings.WINDOW_WIDTH/346*203+rel_cursor_pos.x()+abs_window_pos.x())
        y=int(-settings.WINDOW_WIDTH/346*86+rel_cursor_pos.y()+abs_window_pos.y())
        self.move(QPoint(x,y))

        # self.move(QCursor.pos())
        # if self.pet.cur_action.action_type not in (ActionType.RAISED_DYNAMIC,ActionType.RAISED_STATIC):
            #此处需要立刻进入提起状态，但是行动信号可能还在sleep，所以此时需要接管行动信号来立刻进入下一个动作
        self.pet.change_action_status(ActionStatus.RAISE)
        # self.pet.change_action(random.choice([ActionType.RAISED_STATIC,ActionType.RAISED_STATIC]))
        self.pet.change_action(ActionType.RAISED)
        self.action_thread.close(force=True)
        self.raise_thread = PetThread(self.pet)
        # if self.pet.cur_action.animat_type==AnimatType.SINGLE:
        #     self.raise_thread.next_animat_type=AnimatType.SINGLE
        self.raise_thread.signal.connect(self.one_action)
        self.raise_thread.start()
        # else:
        #     self.pet.next_action(AnimatType.B_LOOP)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if not self.drag_flag:
                self.long_press_timer.start()

            # else:
            #     self.pet.next_action(AnimatType.B_LOOP)
            self.drag_flag=True
            # self.pet.change_action_status(ActionStatus.MOVE)
            self.offset = event.pos()
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.raise_thread and not self.raise_thread.closed:
                self.raise_thread.close()
                self.pet.change_action_status()
                self.play()
            self.long_press_timer.stop()
            self.drag_flag=False



    def mouseMoveEvent(self, event):
        if self.drag_flag :
            rel_cursor_pos = self.mapFromGlobal(event.globalPosition().toPoint())
            abs_window_pos = self.pos()
            delta_x=int(-settings.WINDOW_WIDTH / 346 * 203 + rel_cursor_pos.x())
            delta_y=int(-settings.WINDOW_WIDTH / 346 * 88 + rel_cursor_pos.y())
            delta_point=QPoint(delta_x,delta_y)
            if self.raise_thread and self.raise_thread.closed:

                # 346*346 203*86
                # x = int(delta_x + abs_window_pos.x())
                # y = int(delta_y + abs_window_pos.y())
                self.move(delta_point+abs_window_pos)
                self.raise_pet()
                self.long_press_timer.stop()
            else:

                self.move( abs_window_pos+delta_point)
            event.accept()


    def mouseDoubleClickEvent(self, QMouseEvent):
        pass

    def closeEvent(self, QCloseEvent):
        pass

    def contextMenuEvent(self, e):
        pass

    def paintEvent(self, event):
        """绘图"""

        if hasattr(self, "pixmap"):
            painter = QPainter(self)

            # painter.fillRect(self.rect(),Qt.white)
            # painter.fillRect(self.rect(), Qt.transparent)
            # painter.end()
            # QApplication.processEvents()
            # painter = QPainter(self)
            #
            # painter.eraseRect(self.rect())
            painter.drawPixmap(self.rect(), self.pixmap)
            painter.end()
            QApplication.processEvents()
            # painter.end()
            # time.sleep(0.5)


    def play(self):
        self.action_thread = PetThread(self.pet)
        self.action_thread.signal.connect(self.one_action)
        self.action_thread.start()





    def one_action(self,pixmap):
        self.pixmap=pixmap

        self.update()
        # time.sleep(0.5)
        QApplication.processEvents()


class PetThread(QThread):
    signal = pyqtSignal(object)
    def __init__(self,pet):
        super().__init__()
        self.pet=pet
        self.closed=False
        self.next_animat_type=None

    def run(self):
        while not self.closed:
            graph=self.pet.next_gragh()
            if not graph:
                self.pet.next_action(self.next_animat_type)
                continue
            if self.pet.action_count == 0 and self.pet.cur_action.graph_index==1:
                time.sleep(0.5)  # 感觉像是什么东西没有加载完全？总之添加这个可以有效解决第一个图片有边缘覆盖不了的问题，也许只有垃圾mac会遇到这样的问题
            pixmap = graph.pixmap

            self.signal.emit(pixmap)
            QThread.msleep(graph.duration)
    def close(self,force=False):
        if not force:
            self.pet.next_action(AnimatType.C_END)
        self.closed=True





