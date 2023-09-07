from enum import Enum



Mood=Enum("Mood",("HAPPY","NOMAL","POORCONDITION","ILL"))
"""
心情
"""


ActionType=Enum("ActionType",(
    'RAISED_DYNAMIC',  #提起
    'RAISED_STATIC',

    'CLIMB',  #climb单独分类
    "FALL",
    'MOVE',  # 走路、蠕动
    'DEFAULT',
    'TOUCH_HEAD',
    'TOUCH_BODY',
    'IDEL',
    'SLEEP',
    'SAY',
    'STATEONE',
    'STATETWO',
    'STARTUP',
    'SHUTDOWN',
    'WORK',
    'SWITCH_UP',
    'SWITCH_DOWN',
    'SWITCH_THIRSTY',
    'SWITCH_HUNGER',
    "MUSIC",
    "EAT",
    "DRINK"
))
"""
动作类型
"""



AnimatType=Enum("AnimatType",(
    "SINGLE",
    "A_START",
    "B_LOOP",
    "C_END",
))
"""
动画类型
"""

