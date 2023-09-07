from enum import Enum



Mood=Enum("Mood",("HAPPY","NORMAL","POORCONDITION","ILL"))
"""
心情
"""


ActionType=Enum("ActionType",(
    'COMMON',
    'RAISED_DYNAMIC',
    'RAISED_STATIC',
    'MOVE',
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

