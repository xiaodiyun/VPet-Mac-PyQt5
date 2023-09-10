from .dict import ActionType
WINDOW_HEIGHT=150 #窗口高度
WINDOW_WIDTH=150 #窗口宽度


INIT_POS_X=1250 #初始出现在哪，或者随机？
INIT_POS_Y=650


ACTION_GRAPH_PATH="mod/0000_core/pet/vup" #图在哪

CLIMB_V=[2,3] #每帧移动距离，不支持多向移动

MOVE_VX=[2,3] #
MOVE_VY=[0,0]

FALL_VX=[3,3]
FALL_VY=[4,4]

# WALK_VX=[4,4]
# WALK_VY=[0,1]

#普通无交互情况下，做事权重
#TODO 考虑key改成元祖形式，这样可以更精细控制某些动作频率，以及屏蔽某些动作（设为0）
COMMON_ACTION_WEIGHT={
    ActionType.DEFAULT:1,
    ActionType.MOVE:1,
    ActionType.STATEONE:5,
    ActionType.STATETWO:5,
    ActionType.SAY:4,
    ActionType.IDEL:10
}
#动作循环时，循环次数倾向
# COMBO_ACTION_TIMES={
#     ActionType.DEFAULT:[10,20],
#     ActionType.MOVE:[10,50], #一直爬！爬到边缘被打断并进入climb
#     ActionType.CLIMB:[30,30], #一直爬！爬到边缘被打断并进入climb
#     ActionType.FALL:[30,30], #一般来说是落地之后自动打断，不存在循环次数
#     ActionType.STATEONE:[30,60],
#     ActionType.STATETWO:[30,60],
#     ActionType.SAY:[2,4],
#     ActionType.IDEL:[10,20], #很可爱！
# }

COMBO_ACTION_TIMES={
    ActionType.DEFAULT:[2,2],
    ActionType.MOVE:[2,2], #一直爬！爬到边缘被打断并进入climb
    ActionType.CLIMB:[2,2], #一直爬！爬到边缘被打断并进入climb
    ActionType.FALL:[2,2], #一般来说是落地之后自动打断，不存在循环次数
    ActionType.STATEONE:[2,2],
    ActionType.STATETWO:[2,2],
    ActionType.SAY:[2,2],
    ActionType.IDEL:[2,2], #很可爱！
}


