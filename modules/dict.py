from enum import Enum

#枚举构造方法没有代码提示
class Mood(Enum):
    """
    心情
    """
    HAPPY=1
    """开心"""
    NOMAL=2
    """开心的不明显"""
    POORCONDITION=3
    """生气"""
    ILL=4
    """生病（没打算进这个状态，感觉有点可怜）"""





class ActionType(Enum):
    """动作类型"""
    RAISED=1
    """提起"""

    CLIMB=3  # climb单独分类
    """攀爬"""
    FALL=4
    """下落"""
    MOVE=5
    """移动"""
    DEFAULT=6
    """默认"""
    TOUCH_HEAD=7
    """摸头"""
    TOUCH_BODY=8
    """摸身子"""
    IDEL=9
    """待机（打瞌睡）"""
    SLEEP=10
    """睡觉"""
    SAY=11
    """说话"""
    STATEONE=12
    """坐下"""
    STATETWO=13
    """躺下"""
    STARTUP=14
    """启动动作"""
    SHUTDOWN=15
    """关闭动作"""
    WORK=16
    """打工"""
    SWITCH_UP=17
    """状态切换"""
    SWITCH_DOWN=18
    SWITCH_THIRSTY=19
    SWITCH_HUNGER=20
    MUSIC=21
    """音乐"""
    EAT=22
    DRINK=23

"""
动作类型
"""

class AnimatType(Enum):
    """
    动画类型
    """
    SINGLE=1
    """单一动作不循环"""
    A_START=2
    """循环开始（只执行一次）"""
    B_LOOP=3
    """循环中"""
    C_END=4
    """循环结束（只执行一次）"""


class ActionStatus:
    DEFAULT=1
    MOVE=2
    WORK=4
    MUSIC=5
    RAISE=6

