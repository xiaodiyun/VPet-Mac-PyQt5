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
    """
    动作类型，key为不同动作类型，value为在路径中搜索动作的关键字（上覆盖下）
    """
    RAISED='RAISED'
    """提起"""
<<<<<<< HEAD

    CLIMB=3
    """攀爬"""
    """在顶上爬"""
    FALL=4
=======
    CLIMB_TOP = 'CLIMB.TOP'
    CLIMB='CLIMB'
    """攀爬"""
    FALL='FALL'
>>>>>>> climb
    """下落"""
    MOVE='MOVE'
    """移动"""
    DEFAULT='DEFAULT'
    """默认"""
    TOUCH_HEAD='TOUCH_HEAD'
    """摸头"""
    TOUCH_BODY='TOUCH_BODY'
    """摸身子"""
    IDEL='IDEL'
    """待机（打瞌睡）"""
    SLEEP='SLEEP'
    """睡觉"""
    SAY='SAY'
    """说话"""
    STATE='STATE'
    """坐下躺下"""
    STARTUP='STARTUP'
    """启动动作"""
    SHUTDOWN='SHUTDOWN'
    """关闭动作"""
    WORK_CLEAN = "WORKCLEAN"
    """一个很可爱的舔屏动作，重点提及"""
    WORK='WORK'
    """打工"""
    # SWITCH_UP=17
    # """状态切换"""
    # SWITCH_DOWN=18
    # SWITCH_THIRSTY=19
    # SWITCH_HUNGER=20
    MUSIC='MUSIC'
    """音乐"""
    EAT='EAT'
    DRINK='DRINK'

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
    """
    宠物状态，好像没用到？
    """
    DEFAULT=1
    MOVE=2
    WORK=4
    MUSIC=5
    RAISE=6

