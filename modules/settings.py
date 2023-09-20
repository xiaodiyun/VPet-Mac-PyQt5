from .dict import ActionType
from modules.share import app






SCREEN_HEIGHT=app.desktop().screenGeometry().height()
"""
屏幕高度（因为有些mac会开底部程序坞，所以需要手动设置偏移）
"""
SCREEN_WIDTH=app.desktop().screenGeometry().width()
"""
屏幕宽度
"""

SCREEN_Y_START=25
"""
预留字段
- 经过反复测试，（在作者电脑上）如果mac电脑开启了"始终显示菜单栏"，则所有窗口的y轴坐标无法低于0，且低于25的会被重定向到25
- 如果mac电脑关闭了菜单栏，则y轴坐标可以低于0，且不会被重定向
- 暂时只考虑关闭菜单栏情况。如果开启菜单栏，宠物在顶部的爬行应该会浮空。因为爬行时，宠物是在png图片中部，所以想要桌面上边缘贴着宠物的手，必须要把宠物窗体移到桌面边缘上方
（可以通过改变窗体大小+偏移图片位置的方式来做兼容，太麻烦了，请按作者推荐配置运行，作者和宠物有一个能跑就行）
  
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
# INIT_POS_Y=-500
"""
宠物初始出现x轴坐标，也可以设置为随机： `random.randint(0,SCREEN_HEIGHT)`
"""

ACTION_GRAPH_PATH="mod/0000_core/pet/vup"
"""
宠物动作序列图片位置
"""

CLIMB_V=[2,3] #每帧移动距离

MOVE_VX=[2,3]
"""移动动作下，每50毫秒移动x轴距离"""

MOVE_VY=[-1,1]
"""移动动作下，每50毫秒移动y轴距离"""

FALL_VX=[3,3]
FALL_VY=[4,4]


# LAZY_LOAD=True
# """
# 是否懒加载图片
# """


COMMON_ACTION_WEIGHT={
    ActionType.DEFAULT:8,
    ActionType.MOVE:1000,
    ActionType.STATE:5,
    ActionType.WORK_CLEAN:3,
    ActionType.SAY:1,
    ActionType.IDEL:8
}
"""
在空闲状态下，宠物随机做事的权重，可以自己更改权重，也可以删减动作
"""


COMBO_ACTION_TIMES={
    ActionType.DEFAULT:[6,10],
    ActionType.MOVE:[5,30], #一直爬！爬到边缘被打断并进入climb
    # ActionType.CLIMB:[6,10], #一直爬！爬到边缘被打断并进入climb
    ActionType.FALL:[6,10],
    ActionType.STATE:[6,10],
    ActionType.WORK_CLEAN:[4,8],
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


