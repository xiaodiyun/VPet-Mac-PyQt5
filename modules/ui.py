import random,sys
import time

from PyQt5 import QtCore,QtWidgets
from PyQt5.QtCore import QTimer, QPoint,QThread,pyqtSignal,Qt
from PyQt5.QtGui import QPainter,QCursor,QBrush
from PyQt5.QtWidgets import QApplication, QMainWindow,QMessageBox

from . import settings
from .model import Pet,BaseAction
from .dict import ActionType,ActionStatus,AnimatType
import math




class DesktopPet(QMainWindow):
    """桌宠核心类"""

    def __init__(self):
        super(DesktopPet, self).__init__(None)
        self.pet = Pet()





        # 长按定时器，长按或短按+移动会触发宠物提起动作
        self.long_press_timer = QTimer()
        self.long_press_timer.setSingleShot(True)
        self.long_press_timer.setInterval(300) #长按判断时间
        self.long_press_timer.timeout.connect(self.raise_pet)

        self.raise_thread=None  #独立的提起动作信号线程
        self.move_thread=None #独立的移动动作信号线程
        self.action_thread=None
        self.drag_flag=False  #用于判断是否是点击后移动

        self.painter_offset_y=0 #绘图的y轴偏移量
        self.painter_scale_y = 1  # 绘图的高度放大倍数
        self.play()
        self.initUI()

    def initUI(self):
        # self.desktop = QApplication.instance().screens()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        self.move(QPoint(settings.INIT_POS_X, settings.INIT_POS_Y))
        # self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.resize(settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)





    def move(self, a0: QtCore.QPoint) -> None:
        current_pos = self.pos()

        new_pos = current_pos+a0
        self.move_to(new_pos)

    def move_to(self, a0: QtCore.QPoint) -> None:
        if not self.start_climb(a0):
            # if a0.y()-settings.WINDOW_HEIGHT>=settings.SCREEN_HEIGHT:
            #     a0.setY(settings.SCREEN_HEIGHT)
            # elif a0.y()<=0:
            #     a0.setY(0)

            super().move(a0)

    def start_climb(self,a0:QPoint):
        """
        如果移到边缘，且状态为move，则吸到边缘
        如果移到边缘，状态不为move，则在边缘挡住
        """
        vx=0
        vy=0
        if a0.y()<=settings.SCREEN_Y_START:
            # 如果爬行爬到最上面，切换climb_top模式，并且调整速度方向
            a0.setY(settings.SCREEN_Y_START)
            if self.pet.cur_action.action_type != ActionType.CLIMB_TOP: #不是climb_top的话，切climb_top，被raise提上来的也会走这个逻辑
                self.pet.change_action(ActionType.CLIMB_TOP,-1 if self.pet.cur_action.direction==0 else -self.pet.cur_action.direction)
            elif a0.x()<=-100/510*settings.WINDOW_WIDTH: #说明爬到边缘了，转个方向
                self.pet.change_action(ActionType.CLIMB_TOP,1)
                self.pet.next_action(AnimatType.B_LOOP)
                a0.setX(-100/510*settings.WINDOW_WIDTH)
            elif a0.x()>=settings.SCREEN_WIDTH-settings.WINDOW_WIDTH+100/510*settings.WINDOW_WIDTH: #说明爬到边缘了，转个方向
                self.pet.change_action(ActionType.CLIMB_TOP, -1)
                self.pet.next_action(AnimatType.B_LOOP)
                a0.setX(settings.SCREEN_WIDTH-settings.WINDOW_WIDTH+100/510*settings.WINDOW_WIDTH)
            vx = random.uniform(*settings.CLIMB_V)*self.pet.cur_action.direction

            vy = 0
        elif self.drag_flag:
            self.pet.change_action(ActionType.RAISED)
        if self.pet.cur_action.action_type==ActionType.CLIMB_TOP:
            # if self.drag_flag:
            #     self.pet.change_action(ActionType.RAISED)
            pass
        elif a0.x()<=0: #如果撞到左墙
            cur_action = self.pet.cur_action
            # vx=0
            # vy=-random.uniform(*settings.CLIMB_V)
            if cur_action.action_type == ActionType.MOVE and cur_action.direction==-1:
                vx = 0
                vy = -random.uniform(*settings.CLIMB_V)
                self.pet.change_action(ActionType.CLIMB, direction=-1)
                a0.setX(0)
            elif self.drag_flag:
                self.pet.change_action(ActionType.CLIMB,direction=-1)
                self.pet.next_action(AnimatType.B_LOOP)
                a0.setX(-140 / 480 * settings.WINDOW_WIDTH)
            elif cur_action.action_type not in (ActionType.CLIMB,ActionType.MOVE) or (cur_action.action_type==ActionType.CLIMB and cur_action.animat_type==AnimatType.A_START):
                vx = 0
                vy = -random.uniform(*settings.CLIMB_V)
                a0.setX(-100 / 480 * settings.WINDOW_WIDTH)
            elif cur_action.action_type == ActionType.MOVE and cur_action.direction==1:
                vx = random.uniform(*settings.MOVE_VX) * self.pet.cur_action.direction
                vy = random.uniform(*settings.MOVE_VY)
                # a0.setX(1)

            else:
                vx = 0
                vy = -random.uniform(*settings.CLIMB_V)
                a0.setX(-140 / 480 * settings.WINDOW_WIDTH)
        elif a0.x()+settings.WINDOW_WIDTH>=settings.SCREEN_WIDTH:#如果撞到右墙
            cur_action = self.pet.cur_action

            # print(vx,vy,a0,self.pet.cur_action.action_type)
            if cur_action.action_type == ActionType.MOVE and  cur_action.direction==1:
                vx = 0
                vy = -random.uniform(*settings.CLIMB_V)
                self.pet.change_action(ActionType.CLIMB, 1)
                a0.setX(settings.SCREEN_WIDTH-settings.WINDOW_WIDTH)
            elif self.drag_flag:
                self.pet.change_action(ActionType.CLIMB,direction=1)
                self.pet.next_action(AnimatType.B_LOOP)
                a0.setX(settings.SCREEN_WIDTH - 300 / 480 * settings.WINDOW_WIDTH)

            elif cur_action.action_type not in (ActionType.CLIMB,ActionType.MOVE) or (
                    cur_action.action_type == ActionType.CLIMB and cur_action.animat_type == AnimatType.A_START):
                vx = 0
                vy = -random.uniform(*settings.CLIMB_V) * cur_action.direction
                a0.setX(settings.SCREEN_WIDTH -350 / 480 * settings.WINDOW_WIDTH) #有个小过度
            elif cur_action.action_type == ActionType.MOVE and  cur_action.direction==-1:
                vx = random.uniform(*settings.MOVE_VX)*self.pet.cur_action.direction
                vy = random.uniform(*settings.MOVE_VY)
                # a0.setX(settings.SCREEN_WIDTH-settings.WINDOW_WIDTH-1)

            else:
                vx = 0
                vy = -random.uniform(*settings.CLIMB_V)
                a0.setX(settings.SCREEN_WIDTH -300 / 480 * settings.WINDOW_WIDTH)
        else:#说明没撞墙，退出去不走climb逻辑
            return False


        if not self.move_thread or self.move_thread.closed:
            self.move_thread = MoveThread(self.pet, vx, vy)
            self.move_thread.signal.connect(self.move)
            self.move_thread.start()
        else:
            # print(vx,vy,a0)
            self.move_thread.vx = vx
            self.move_thread.vy = vy

        super().move(a0) #这里需要等climb.start播完之后才能移位置，要不然看起来有点瞬移
        return True



    def raise_pet(self):
        rel_cursor_pos=self.mapFromGlobal(QCursor.pos())
        abs_window_pos=self.pos()
        #346*346 203*86
        x=int(-settings.WINDOW_WIDTH/346*203+rel_cursor_pos.x()+abs_window_pos.x())
        y=int(-settings.WINDOW_WIDTH/346*86+rel_cursor_pos.y()+abs_window_pos.y())
        self.move_to(QPoint(x,y))

        self.pet.change_action(ActionType.RAISED)

        self.action_thread.close(force=True)
        if not self.raise_thread or self.raise_thread.closed:
            self.raise_thread = PetThread(self.pet)

            self.raise_thread.signal.connect(self.one_action)
            self.raise_thread.start()


    def mousePressEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton:
            if not self.drag_flag:
                self.long_press_timer.start()

            self.drag_flag=True

            self.offset = event.pos()
            event.accept()

    def mouseReleaseEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton:
            if self.raise_thread and not self.raise_thread.closed and self.pet.cur_action.action_type==ActionType.RAISED:
                self.raise_thread.close()
                # self.pet.change_action_status()
                self.play()
            self.long_press_timer.stop()
            self.drag_flag=False



    def mouseMoveEvent(self, event):

        if self.drag_flag :
            rel_cursor_pos = self.mapFromGlobal(event.globalPos())
            abs_window_pos = self.pos()
            delta_x=int(-settings.WINDOW_WIDTH / 346 * 203 + rel_cursor_pos.x())
            delta_y=int(-settings.WINDOW_WIDTH / 346 * 88 + rel_cursor_pos.y())
            delta_point=QPoint(delta_x,delta_y)

            if (self.raise_thread and self.raise_thread.closed) or not self.raise_thread:
                self.long_press_timer.stop()
                self.raise_pet()
                self.move_to(delta_point + abs_window_pos)
            else:
                self.move_to( abs_window_pos+delta_point)
            event.accept()


    def mouseDoubleClickEvent(self, QMouseEvent):
        pass

    def closeEvent(self, QCloseEvent):
        pass

    def contextMenuEvent(self, e):
        pass

    def paintEvent(self, event):
        """绘图"""

        if hasattr(self, "qimage"):
            painter = QPainter(self)

            painter.translate(0,self.painter_offset_y)
            painter.scale(1, self.painter_scale_y)
            painter.drawImage(self.rect(), self.qimage)





    def play(self):
        if self.action_thread==None or self.action_thread.closed:
            self.action_thread = PetThread(self.pet)
            self.action_thread.signal.connect(self.one_action)
            self.action_thread.start()









    def one_action(self,qimage):
        self.qimage=qimage

        self.update()


        if self.pet.cur_action.action_type ==ActionType.MOVE:
            if not self.move_thread or self.move_thread.closed:
                self.move_thread=MoveThread(self.pet,random.uniform(*settings.MOVE_VX)*self.pet.cur_action.direction,random.uniform(*settings.MOVE_VY))
                self.move_thread.signal.connect(self.move)
                self.move_thread.start()
        elif self.pet.cur_action.action_type not in (ActionType.MOVE,ActionType.CLIMB,ActionType.CLIMB_TOP):
            if self.move_thread:
                self.move_thread.close()

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
    def __init__(self,pet,vx,vy):
        super().__init__()
        self.pet = pet
        self.vx=vx #vx的正负是不需要控制的，一切以pet类的direction为准
        self.vy=vy
        self.closed = False


    def run(self):
        while not self.closed:
            if self.pet.cur_action.action_type in (ActionType.MOVE,ActionType.CLIMB,ActionType.MOVE,ActionType.CLIMB_TOP) and self.pet.cur_action.animat_type==AnimatType.B_LOOP:
                self.signal.emit(QPoint(abs(self.vx)*self.pet.direction,self.vy))
            QThread.msleep(50)

    def close(self):
        self.closed=True



class PetThread(QThread):
    signal = pyqtSignal(object)
    def __init__(self,pet):
        super().__init__()
        self.pet=pet
        self.closed=False

        # self.next_animat_type=None

    def run(self):
        while not self.closed:
            graph=self.pet.next_gragh()

            if not graph:
                action=self.pet.next_action() #type: BaseAction
                self.pet.direction=action.direction

                continue
            if self.pet.action_count == 0 and self.pet.cur_action.graph_index==1:
                time.sleep(0.5)
                """
        感觉像是什么东西没有加载完全？总之添加这个可以一定程度解决部分情况下，图片有边缘覆盖不了的问题，应该只有垃圾mac会遇到这样的问题。
        应该是底层信号槽机制有点问题，见：
           https://stackoverflow.com/questions/62530793/pyqt-widget-refresh-behavior-different-when-clicking-button-with-mouse-or-keyboa
           https://bugreports.qt.io/browse/QTBUG-42827
           https://stackoverflow.com/questions/30728820/refreshing-a-qwidget
                """

            qimage = graph.qimage

            self.signal.emit(qimage)
            QThread.msleep(graph.duration)
    def close(self,force=False):
        if not force:
            self.pet.next_action(AnimatType.C_END)
        self.closed=True






