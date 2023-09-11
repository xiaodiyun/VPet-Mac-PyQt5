from enum import Enum

#枚举构造方法没有代码提示
class Mood(Enum):
    """
    心情
    """
    HAPPY=1
    NOMAL=2
    POORCONDITION=3
    ILL=4





class ActionType(Enum):
    RAISED=1  # 提起


    CLIMB=3  # climb单独分类
    FALL=4
    MOVE=5  # 走路、蠕动
    DEFAULT=6
    TOUCH_HEAD=7
    TOUCH_BODY=8
    IDEL=9
    SLEEP=10
    SAY=11
    STATEONE=12
    STATETWO=13
    STARTUP=14
    SHUTDOWN=15
    WORK=16
    SWITCH_UP=17
    SWITCH_DOWN=18
    SWITCH_THIRSTY=19
    SWITCH_HUNGER=20
    MUSIC=21
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
    A_START=2
    B_LOOP=3
    C_END=4


class ActionStatus:
    DEFAULT=1
    MOVE=2
    WORK=4
    MUSIC=5
    RAISE=6

