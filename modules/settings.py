from .dict import ActionType
from modules.share import app

SCREEN_HEIGHT = app.desktop().screenGeometry().height()
"""
屏幕高度（因为有些mac会开底部程序坞，所以需要手动设置偏移）
"""
SCREEN_WIDTH = app.desktop().screenGeometry().width()
"""
屏幕宽度
"""

SCREEN_Y_START = 25
"""
- 经过反复测试，（在作者电脑上）如果mac电脑开启了"始终显示菜单栏"，则所有窗口的y轴坐标无法低于0，且低于25的会被重定向到25
- 如果mac电脑关闭了菜单栏，则y轴坐标可以低于0，且不会被重定向
- 此处做了兼容，宠物在顶上爬墙时，实际上是宠物图片偏移，而不是窗体移动到合适位置（跟左右爬墙逻辑不同）

"""

WINDOW_HEIGHT = 150
"""
宠物窗口高度
更改此项配置造成的各种交互偏移，并没有做测试（在作者电脑上跑的好就行）
"""
WINDOW_WIDTH = 150
"""
宠物窗口宽度
"""

INIT_POS_X = 1250
"""
宠物初始出现x轴坐标，也可以设置为随机： `random.randint(0,SCREEN_WIDTH)`
"""
INIT_POS_Y = 650
# INIT_POS_Y=-500
"""
宠物初始出现x轴坐标，也可以设置为随机： `random.randint(0,SCREEN_HEIGHT)`
"""

ACTION_GRAPH_PATH = "mod/0000_core/pet/vup"
"""
宠物动作序列图片位置
"""

CLIMB_V = [2, 3]  # 每帧移动距离

MOVE_VX = [2, 3]
"""移动动作下，每50毫秒移动x轴距离"""

MOVE_VY = [-1, 1]
"""移动动作下，每50毫秒移动y轴距离"""

FALL_VX = [2, 3]
"""
降落x轴速度，标量
"""
FALL_VY = [3, 6]
"""
降落y轴速度，标量。这个值与COMBO_ACTION_TIMES共同决定宠物掉落距离。宠物掉落仅设置左右限制，可以调到屏幕下方不可见位置
"""

FALL_GUESS=0.001
"""
宠物在顶部爬行时（climb_top）才会触发落下，此数值为每帧有多少概率掉下去
"""



# LAZY_LOAD=True
# """
# 是否懒加载图片
# """


COMMON_ACTION_WEIGHT = {
    ActionType.DEFAULT: 100,
    ActionType.MOVE: 1,
    ActionType.STATE: 5,
    ActionType.WORK_CLEAN: 3,
    ActionType.SAY: 1,
    ActionType.IDEL: 8
}
"""
在空闲状态下，宠物随机做事的权重，可以自己更改权重，也可以删减动作
"""

COMBO_ACTION_TIMES = {
    ActionType.DEFAULT: [6, 10],
    ActionType.MOVE: [5, 30],  # 一直爬！爬到边缘被打断并进入climb
    ActionType.FALL: [2, 8],
    ActionType.STATE: [6, 10],
    ActionType.WORK_CLEAN: [4, 8],
    ActionType.SAY: [2, 4],
    ActionType.IDEL: [4, 6],  # 很可爱！
    ActionType.TOUCH_HEAD:[2,3],
    ActionType.TOUCH_BODY:[1,2]
}
"""
宠物在循环做事时，循环的次数。不在里面的默认无限次
"""


FILE_ICON_MAP={
    "modules/icon/docx.icns":["doc","docx"],
    "modules/icon/folder.icns": ["folder"],
    "modules/icon/sql.icns": ["sql", "db"],
    "modules/icon/xlsx.icns": ["xls", "xlsx"],
    "modules/icon/pdf.icns": ["pdf"],
}
FILE_ICON_DEFAULT="modules/icon/default.icns"
"""
文件后缀跟图标映射，用于在宠物吃文件时展示
"""

