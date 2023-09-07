import time

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QApplication, QMainWindow

from . import settings
from .model import Pet


class DesktopPet(QMainWindow):
    """桌宠核心类"""

    def __init__(self):
        super(DesktopPet, self).__init__(None)
        self.pet = Pet()  # 初始化宠物对象
        self.initUI()  # 初始化界面
        self.play()  # 开始播放动画
        self.is_pressed = False  # 鼠标是否按下

    def initUI(self):
        self.desktop = QApplication.desktop()  # 获取桌面对象
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint  # 设置窗口属性为无边框且置顶
        )
        self.move(settings.INIT_POS_X, settings.INIT_POS_Y)  # 设置窗口位置
        self.setAttribute(Qt.WA_TranslucentBackground)  # 设置窗口背景透明
        self.resize(settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)  # 设置窗口大小

    def move(self, ax: int, ay: int) -> None:  # 移动窗口和宠物对象到指定位置
        super().move(ax, ay)
        self.pet.move(ax, ay)

    def mousePressEvent(self, event):
        """鼠标按下事件"""
        # 判断是否点击了宠物
        if self.pet.x <= event.globalX() <= self.pet.x + settings.WINDOW_WIDTH and self.pet.y <= event.globalY() <= self.pet.y + settings.WINDOW_HEIGHT:
            self.is_pressed = True  # 设置鼠标按下标志

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        self.is_pressed = False  # 设置鼠标按下标志

    def mouseMoveEvent(self, event):
        if self.is_pressed:  # 如果鼠标按下
            self.move(event.globalX() - settings.WINDOW_WIDTH / 2,
                      event.globalY() - settings.WINDOW_HEIGHT / 2)  # 移动窗口和宠物对象到指定位置

    def mouseDoubleClickEvent(self, QMouseEvent): pass  # 鼠标双击事件不做处理
    def closeEvent(self, QCloseEvent): pass  # 关闭窗口事件不做处理
    def contextMenuEvent(self, e): pass  # 右键菜单事件不做处理

    def paintEvent(self, QPaintEvent):  # 绘制窗口内容
        """绘图"""
        painter = QPainter(self)  # 创建画笔对象
        if hasattr(self, "pixmap"):  # 如果存在图片对象
            painter.drawPixmap(self.rect(), self.pixmap)  # 在窗口上绘制图片

    def play(self):  # 开始播放动画
        self.timer = QTimer(self)  # 创建定时器对象
        self.timer.timeout.connect(self.one_action)  # 当定时器超时时执行one_action方法
        self.timer.start(0)  # 启动定时器，不设置时间间隔

    def one_action(self):  # 每次动画帧的处理方法
        self.timer.stop()  # 停止定时器
        action = self.pet.next_action()  # 获取下一个动作对象
        for graph in action.graph_list:  # 遍历动作中的图形列表
            self.pixmap = graph.pixmap  # 将图形的图片对象赋值给窗口的图片对象属性
            QApplication.processEvents()  # 让当前线程处理其他事件，如界面刷新等操作
            self.update()  # 更新窗口显示内容
            QApplication.processEvents()  # 让当前线程处理其他事件，如界面刷新等操作
            time.sleep(graph.duration/1000)  # 根据图形的持续时间暂停一段时间后继续下一帧的绘制操作
        self.pet.add_action()  # 将当前动作添加到宠物的动作列表中
        self.timer.start()  # 继续播放动画
