import random, sys
import time

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QTimer, QPoint, QThread, pyqtSignal, Qt, QRect
from PyQt5.QtGui import QPainter, QCursor, QBrush,QMouseEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QSizePolicy

from . import settings
from .model import Pet, BaseAction,Graph
from .dict import ActionType, ActionStatus, AnimatType

import threading




class DesktopPet(QMainWindow):
    """桌宠核心类"""

    def __init__(self):
        super(DesktopPet, self).__init__(None)
        self.pet = Pet()

        # 长按定时器，长按或短按+移动会触发宠物提起动作
        self.long_press_timer = QTimer()
        self.long_press_timer.setSingleShot(True)
        self.long_press_timer.setInterval(250)  # 长按判断时间
        self.long_press_timer.timeout.connect(self.raise_pet)

        self.touch_head_timer=QTimer() #摸头定时器
        self.touch_head_timer.setTimerType(True)
        self.touch_head_timer.setInterval(1000)
        self.touch_head_timer.timeout.connect(self.touch_head)
        self.touch_head_count=0

        self.touch_body_timer = QTimer()  # 摸头定时器
        self.touch_body_timer.setTimerType(True)
        self.touch_body_timer.setInterval(1000)
        self.touch_body_timer.timeout.connect(self.touch_body)
        self.touch_body_count = 0


        self.move_thread = MoveThread(self.pet)  # 独立的移动动作信号线程
        self.move_thread.signal.connect(self.move)
        self.action_thread = PetThread(self.pet)
        self.action_thread.signal.connect(self.one_action)
        self.drag_flag = False  # 用于判断是否是点击后移动

        self.painter_offset_y = 0  # 绘图的y轴偏移量

        self.initUI()
        self.play()

    def initUI(self):
        # self.desktop = QApplication.instance().screens()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )

        self.move(QPoint(settings.INIT_POS_X, settings.INIT_POS_Y))

        self.setAttribute(Qt.WA_NoSystemBackground)

        self.resize(settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)
        self.setMouseTracking(True)  # 启用鼠标追踪功能
        self.setAcceptDrops(True) #启用拖文件检测


    def move(self, a0: QtCore.QPoint) -> None:
        # print(a0)
        current_pos = self.pos()

        new_pos = current_pos + a0
        self.move_to(new_pos)

    def move_to(self, a0: QtCore.QPoint) -> None:
        if not self.start_climb(a0):

            super().move(a0)

    def start_fall(self):
        cur_action=self.pet.cur_action
        self.pet.change_action(ActionType.FALL,direction=cur_action.direction)
        self.action_thread.wakeup()
        vx = random.uniform(*settings.FALL_VX)*cur_action.direction
        vy = random.uniform(*settings.FALL_VY)
        self.pet.vx = vx
        self.pet.vy = vy
        # self.move(QPoint(vx,vy))


    def start_climb(self, a0: QPoint):
        """
        如果移到边缘，且状态为move，则吸到边缘
        如果移到边缘，状态不为move，则在边缘挡住
        """
        vx = 0
        vy = 0
        self.painter_offset_y = 0
        if a0.x()>0 and a0.x()<settings.SCREEN_WIDTH-settings.WINDOW_WIDTH and self.pet.cur_action.action_type==ActionType.FALL:
            return False


        if a0.y() <= settings.SCREEN_Y_START:
            # 如果爬行爬到最上面，切换climb_top模式，并且调整速度方向
            a0.setY(settings.SCREEN_Y_START)



            if self.pet.cur_action.action_type==ActionType.CLIMB_TOP and a0.x()>=settings.SCREEN_WIDTH/6 and a0.x()<=settings.SCREEN_WIDTH*5/6:
                #规定宠物在什么位置什么方向才进入掉落概率判定，防止出现宠物在右边缘向右掉落一头撞墙的问题
                fall_guess=random.uniform(0,1)
                if fall_guess<=settings.FALL_GUESS:
                    self.start_fall()
                    return False
            self.painter_offset_y = -settings.WINDOW_HEIGHT * (120 / 450)


            if self.pet.cur_action.action_type != ActionType.CLIMB_TOP:  # 不是climb_top的话，切climb_top，被raise提上来的也会走这个逻辑
                self.pet.change_action(ActionType.CLIMB_TOP,
                                       -1 if self.pet.cur_action.direction == 0 else -self.pet.cur_action.direction)
                self.action_thread.wakeup()
            elif a0.x() <= -100 / 510 * settings.WINDOW_WIDTH:  # 说明爬到边缘了，转个方向
              # print('撞墙')
                self.pet.change_action(ActionType.CLIMB_TOP, 1,interrupt=3)

                self.pet.next_action(AnimatType.B_LOOP)
                # self.action_thread.wakeup()
                # a0.setX(-100 / 510 * settings.WINDOW_WIDTH)
            elif a0.x() >= settings.SCREEN_WIDTH - settings.WINDOW_WIDTH + 100 / 510 * settings.WINDOW_WIDTH:  # 说明爬到边缘了，转个方向
                self.pet.change_action(ActionType.CLIMB_TOP, -1,interrupt=3)
                self.pet.next_action(AnimatType.B_LOOP)
                self.action_thread.wakeup()
                # a0.setX(settings.SCREEN_WIDTH - settings.WINDOW_WIDTH + 100 / 510 * settings.WINDOW_WIDTH)
            vx = random.uniform(*settings.CLIMB_V) * self.pet.cur_action.direction

            vy = 0
        elif self.drag_flag and self.pet.cur_action.action_type not in (ActionType.RAISED,ActionType.CLIMB):
            self.pet.change_action(ActionType.RAISED)
            self.action_thread.wakeup()


        if self.pet.cur_action.action_type == ActionType.CLIMB_TOP:
            pass
        elif a0.x() <= 0:  # 如果撞到左墙

            cur_action = self.pet.cur_action
            # vx=0
            # vy=-random.uniform(*settings.CLIMB_V)
            if cur_action.action_type in( ActionType.MOVE,ActionType.FALL) and cur_action.direction == -1:
                vx = 0
                vy = -random.uniform(*settings.CLIMB_V)
                self.pet.change_action(ActionType.CLIMB, direction=-1)
                a0.setX(0)
            elif self.drag_flag and self.pet.cur_action.action_type!=ActionType.CLIMB:
                self.pet.change_action(ActionType.CLIMB, direction=-1)
                self.pet.next_action(AnimatType.B_LOOP)
                self.action_thread.wakeup()
                a0.setX(-140 / 480 * settings.WINDOW_WIDTH)
            elif cur_action.action_type not in (ActionType.CLIMB, ActionType.MOVE) or (
                    cur_action.action_type == ActionType.CLIMB and cur_action.animat_type == AnimatType.A_START):
                vx = 0
                vy = -random.uniform(*settings.CLIMB_V)
                a0.setX(-100 / 480 * settings.WINDOW_WIDTH)
            elif cur_action.action_type == ActionType.MOVE and cur_action.direction == 1:
                vx = random.uniform(*settings.MOVE_VX) * self.pet.cur_action.direction
                vy = random.uniform(*settings.MOVE_VY)
                # a0.setX(1)

            else:
                vx = 0
                vy = -random.uniform(*settings.CLIMB_V)
                a0.setX(-140 / 480 * settings.WINDOW_WIDTH)
        elif a0.x() + settings.WINDOW_WIDTH >= settings.SCREEN_WIDTH:  # 如果撞到右墙
            cur_action = self.pet.cur_action

            # print(vx,vy,a0,self.pet.cur_action.action_type)
            if cur_action.action_type in( ActionType.MOVE,ActionType.FALL) and cur_action.direction == 1:
                vx = 0
                vy = -random.uniform(*settings.CLIMB_V)
                self.pet.change_action(ActionType.CLIMB, 1)

                a0.setX(settings.SCREEN_WIDTH - settings.WINDOW_WIDTH)
            elif self.drag_flag and self.pet.cur_action.action_type!=ActionType.CLIMB:
                # print("aaa")
                self.pet.change_action(ActionType.CLIMB, direction=1)
                self.pet.next_action(AnimatType.B_LOOP)
                self.action_thread.wakeup()
                a0.setX(settings.SCREEN_WIDTH - 300 / 480 * settings.WINDOW_WIDTH)

            elif cur_action.action_type not in (ActionType.CLIMB, ActionType.MOVE) or (
                    cur_action.action_type == ActionType.CLIMB and cur_action.animat_type == AnimatType.A_START):
                vx = 0
                vy = -random.uniform(*settings.CLIMB_V) * cur_action.direction
                a0.setX(settings.SCREEN_WIDTH - 350 / 480 * settings.WINDOW_WIDTH)  # 有个小过度
            elif cur_action.action_type == ActionType.MOVE and cur_action.direction == -1:
                vx = random.uniform(*settings.MOVE_VX) * self.pet.cur_action.direction
                vy = random.uniform(*settings.MOVE_VY)
                # a0.setX(settings.SCREEN_WIDTH-settings.WINDOW_WIDTH-1)

            else:
                vx = 0
                vy = -random.uniform(*settings.CLIMB_V)
                a0.setX(settings.SCREEN_WIDTH - 300 / 480 * settings.WINDOW_WIDTH)
        elif self.drag_flag and self.pet.cur_action.action_type not in (ActionType.RAISED,):

            self.pet.change_action(ActionType.RAISED)
            self.action_thread.wakeup()
        else:  # 说明没撞墙，退出去不走climb逻辑
            return False

        # if not self.move_thread or self.move_thread.closed:
        #
        #     self.move_thread = MoveThread(self.pet)
        #     self.move_thread.signal.connect(self.move)
        #     self.move_thread.start()
        self.pet.vx = vx
        self.pet.vy = vy
        self.pet.move_flag=True

        super().move(a0)  # 这里需要等climb.start播完之后才能移位置，要不然看起来有点瞬移

        return True

    def raise_pet(self):

        rel_cursor_pos = self.mapFromGlobal(QCursor.pos())
        abs_window_pos = self.pos()

        x = int(-settings.WINDOW_WIDTH / 346 * 203 + rel_cursor_pos.x() + abs_window_pos.x())
        y = int(-settings.WINDOW_WIDTH / 346 * 86 + rel_cursor_pos.y() + abs_window_pos.y())


        self.pet.change_action(ActionType.RAISED,interrupt=3)
        self.action_thread.wakeup()
        self.move_to(QPoint(x, y))
        # self.action_thread.close(force=True)
        # if not self.raise_thread or self.raise_thread.closed:
        #     self.raise_thread = PetThread(self.pet)
        #
        #     self.raise_thread.signal.connect(self.one_action)
        #     self.raise_thread.start()

    def mousePressEvent(self, event):
        self.touch_head_count = 0
        self.touch_body_count = 0
        if event.button() == Qt.MouseButton.LeftButton:

            if not self.drag_flag:

                self.long_press_timer.start()

            self.drag_flag = True

            # event.accept()

    def mouseReleaseEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton:

            if  self.drag_flag and self.pet.cur_action.action_type == ActionType.RAISED and self.pet.cur_action.animat_type!=AnimatType.C_END:
                # self.raise_thread.close()

                self.pet.change_action(ActionType.DEFAULT,interrupt=2)
                self.action_thread.wakeup()
            self.drag_flag = False
            self.long_press_timer.stop()



    def mouseMoveEvent(self, event:QMouseEvent):
        if self.drag_flag:
            rel_cursor_pos = event.pos()

            abs_window_pos = self.pos()
            delta_x = int(-settings.WINDOW_WIDTH / 346 * 203 + rel_cursor_pos.x())
            delta_y = int(-settings.WINDOW_WIDTH / 346 * 88 + rel_cursor_pos.y())
            delta_point = QPoint(delta_x, delta_y)
            self.long_press_timer.stop()
            if self.pet.cur_action.action_type not in (ActionType.RAISED,ActionType.CLIMB,ActionType.CLIMB_TOP) or (self.pet.cur_action.action_type==ActionType.RAISED and self.pet.cur_action.animat_type==AnimatType.C_END):
                self.raise_pet()
            self.move_to(delta_point + abs_window_pos)
            event.accept()
        elif self.pet.cur_action.action_type in(ActionType.DEFAULT,ActionType.IDEL): #判断摸摸
            if event.pos().y()<=210/460*settings.WINDOW_HEIGHT:
                if self.touch_head_timer.isActive()==False:
                    self.touch_head_timer.start()
                else:
                    self.touch_head_count=self.touch_head_count+1
                    # print(self.touch_head_count)
            else:
                if self.touch_body_timer.isActive()==False:
                    self.touch_body_timer.start()
                else:
                    self.touch_body_count=self.touch_body_count+1
                    # print(self.touch_body_count)

    def touch_head(self):
        if self.touch_head_count>60:
            self.pet.change_action(ActionType.TOUCH_HEAD)
            self.touch_head_count=0
            self.touch_body_count = 0
            self.touch_head_timer.stop()
    def touch_body(self):
        if self.touch_body_count>60:
            self.pet.change_action(ActionType.TOUCH_BODY)
            self.touch_head_count = 0
            self.touch_body_count = 0
            self.touch_body_timer.stop()


    def focusOutEvent(self, event):
      # print("失焦")
        pass


    def mouseDoubleClickEvent(self, QMouseEvent):
        pass

    def closeEvent(self, QCloseEvent):
        pass

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        file_path = event.mimeData().urls()[0].toLocalFile()
      # print(f"File dropped: {file_path}")



    def contextMenuEvent(self, e):
        pass

    def paintEvent(self, event):
        """绘图"""

        if hasattr(self, "graqhs"):
            painter = QPainter(self)

            painter.translate(0, self.painter_offset_y)
            # print(self.graqhs)
            for graqh in self.graqhs: # type:Graph
                if graqh.width==0 or graqh.height==0:
                    return
                x=graqh.x or 0
                y=graqh.y or 0
                w=graqh.width or settings.WINDOW_WIDTH
                h=graqh.height or settings.WINDOW_HEIGHT
                cut_area=graqh.cut_area
                if len(cut_area)==4:
                    print(graqh.path)
                    painter.drawImage(QRect(x, y, w, h), graqh.qimage,QRect(*cut_area))
                else:
                    # print()
                    painter.drawImage(QRect(x, y, w, h), graqh.qimage)



        # self.update()
        # super().update()
        # QApplication.processEvents()



    def play(self):
        if self.action_thread.closed:
            self.action_thread.start()
        if self.move_thread.closed:
            self.move_thread.start()

    def one_action(self, graqhs):

        self.graqhs = graqhs
        # import datetime
        # print(datetime.datetime.now())
        self.update()

        if self.pet.cur_action.action_type == ActionType.MOVE and not self.pet.move_flag:

            self.pet.move_flag = True
            self.pet.vx=random.uniform(*settings.MOVE_VX)
            self.pet.vy=random.uniform(*settings.MOVE_VY)


        elif self.pet.cur_action.action_type not in (ActionType.MOVE,ActionType.FALL, ActionType.CLIMB, ActionType.CLIMB_TOP):
            self.pet.vx=0
            self.pet.vy=0
            self.pet.move_flag=False

    def notify(self, receiver, event):
        """异常处理函数"""
        try:
            return super().notify(receiver, event)
        except Exception as e:
            message = f"An exception of type {type(e).__name__} occurred.\n{e}"
            QMessageBox.critical(None, "Error", message)
            return False

        # QApplication.processEvents()


class MoveThread(QThread):
    signal = pyqtSignal(QPoint)

    def __init__(self, pet):
        super().__init__()
        self.pet = pet

        self.closed = True


    def run(self):
        self.closed = False
        while not self.closed:
            if self.pet.move_flag and self.pet.cur_action.action_type in (ActionType.MOVE, ActionType.CLIMB, ActionType.MOVE,
                                                   ActionType.CLIMB_TOP,ActionType.FALL) and self.pet.cur_action.animat_type == AnimatType.B_LOOP:

                # print(QPoint(abs(self.pet.vx) * self.pet.direction, self.pet.vy),'aaa')
                self.signal.emit(QPoint(abs(self.pet.vx) * self.pet.direction, self.pet.vy))
                # if self.pet.cur_action.animat_type==AnimatType.C_END:
                #     self.vx,self.vy=0,0
            QThread.msleep(50)

    def close(self):
        self.closed = True



class PetThread(QThread):
    signal = pyqtSignal(object)

    def __init__(self, pet):
        super().__init__()
        self.pet = pet
        self.closed = True
        self.e=None
        self.last_duration=0
        self.last_action_count=0

        # self.next_animat_type=None

    def run(self):
        self.closed = False
        while not self.closed:
            cur_action=self.pet.cur_action
            # print(cur_action.direction,cur_action.action_type,cur_action.graph_indexes)
            graph_lists=cur_action.graph_lists
            if self.pet.action_count != self.last_action_count:
                self.last_duration = 0
                self.last_action_count = self.pet.action_count



            if self.pet.action_count == 0 and self.pet.cur_action.graph_indexes[0] == 0:
                time.sleep(0.5)
                """
        感觉像是什么东西没有加载完全？总之添加这个可以一定程度解决部分情况下，图片有边缘覆盖不了的问题，应该只有垃圾mac会遇到这样的问题。
        应该是底层信号槽机制有点问题，见：
           https://stackoverflow.com/questions/62530793/pyqt-widget-refresh-behavior-different-when-clicking-button-with-mouse-or-keyboa
           https://bugreports.qt.io/browse/QTBUG-42827
           https://stackoverflow.com/questions/30728820/refreshing-a-qwidget
                """

            sum_durations = []
            for i, graph_list in enumerate(graph_lists):
                durations=[graph.duration for graph in graph_list]

                graph_index=cur_action.graph_indexes[i]
                if graph_index!=-1:
                    # print(durations[:graph_index+1])
                    sum_duration = sum(durations[:graph_index+1])
                else:
                    sum_duration=999999
                sum_durations.append(sum_duration)
            min_duration = min(sum_durations)
            min_indexes = [i for i, val in enumerate(sum_durations) if val == min_duration]
            graqhs=[]
            for min_index in min_indexes:
                graph=self.pet.next_gragh_list(min_index)
                if graph:
                    # print(graph.path,min_duration-self.last_duration,sum_durations,self.last_duration,)
                    graqhs.append(graph)
            if len(graqhs)<=0:
                self.last_duration=0
                action = self.pet.next_action()  # type: BaseAction
                self.pet.direction = action.direction
              # print(f"变方向：{self.pet.direction}")
                continue

            self.signal.emit(graqhs)
            self.e = threading.Event()

            self.e.wait(timeout=(min_duration-self.last_duration)/1000)

            self.last_duration=min_duration

    def close(self, force=False):
        if not force:
            self.pet.next_action(AnimatType.C_END)
        self.closed = True


    def wakeup(self):
        self.e.set()







