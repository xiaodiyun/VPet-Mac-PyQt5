from .dict import ActionType
from PyQt5.QtWidgets import QApplication




screen=QApplication.desktop().screenGeometry()


SCREEN_HEIGHT=screen.height()
"""
屏幕高度（因为有些mac会开底部菜单，所以需要手动设置偏移）
"""
SCREEN_WIDTH=screen.width()
"""
屏幕宽度
"""


WINDOW_HEIGHT=150
"""
宠物窗口高度
"""
WINDOW_WIDTH=150
"""
宠物窗口宽度
"""


INIT_POS_X=1250
"""
宠物初始出现x轴坐标，也可以设置为随机： `random.randint(0,SCREEN_WIDTH)`
"""
INIT_POS_Y=650
"""
宠物初始出现x轴坐标，也可以设置为随机： `random.randint(0,SCREEN_HEIGHT)`
"""

ACTION_GRAPH_PATH="mod/0000_core/pet/vup"
"""
宠物动作序列图片位置
"""

CLIMB_V=[2,3] #每帧移动距离，不支持多向移动

MOVE_VX=[2,3]
"""移动动作下，每50毫秒移动x轴距离"""

MOVE_VY=[-1,1]
"""移动动作下，每50毫秒移动y轴距离"""

FALL_VX=[3,3]
FALL_VY=[4,4]




COMMON_ACTION_WEIGHT={
    ActionType.DEFAULT:8,
    ActionType.MOVE:50,
    ActionType.STATEONE:5,
    ActionType.STATETWO:5,
    ActionType.SAY:1,
    ActionType.IDEL:8
}
"""
在空闲状态下，宠物随机做事的权重，可以自己更改权重，也可以删减动作
"""


COMBO_ACTION_TIMES={
    ActionType.DEFAULT:[6,10],
    ActionType.MOVE:[5,8], #一直爬！爬到边缘被打断并进入climb
    ActionType.CLIMB:[6,10], #一直爬！爬到边缘被打断并进入climb
    ActionType.FALL:[6,10],
    ActionType.STATEONE:[6,10],
    ActionType.STATETWO:[6,10],
    ActionType.SAY:[2,4],
    ActionType.IDEL:[4,6], #很可爱！
}
"""
宠物在循环做事时，循环的次数
"""

# COMBO_ACTION_TIMES={
#     ActionType.DEFAULT:[2,2],
#     ActionType.MOVE:[2,2], #一直爬！爬到边缘被打断并进入climb
#     ActionType.CLIMB:[2,2], #一直爬！爬到边缘被打断并进入climb
#     ActionType.FALL:[2,2], #一般来说是落地之后自动打断，不存在循环次数
#     ActionType.STATEONE:[2,2],
#     ActionType.STATETWO:[2,2],
#     ActionType.SAY:[2,2],
#     ActionType.IDEL:[2,2], #很可爱！
# }


