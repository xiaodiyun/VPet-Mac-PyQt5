
from enum import Enum
from . import settings
from .dict import Mood,ActionType,AnimatType
from PyQt5.QtGui import QPixmap
import os
from dataclasses import dataclass
from pprint import pprint
import random



@dataclass()
class Graph():
    """
    图片
    """
    path:str
    duration:int
    pixmap:QPixmap=None



# TODO 此处解析忽略了 drink,eat，因为是分体的逻辑，暂时不考虑
@dataclass(repr=True)
class BaseAction():
    action_name: str
    action_type: ActionType
    animat_type: AnimatType
    mood: Mood
    graph_list: [Graph]
    direction=0 #-1 左，1，右
    if_load=False
    # shift_x=0 #相对位移，如果为负数则反方向，或许不应该在这里设置，因为需要支持随机行走、跟随行走等
    # shift_y=0

#动画序列
@dataclass()
class SeqAction():
    start_action:BaseAction
    loop_action:BaseAction
    end_action:BaseAction
    loop_times=1
    cur_animat_type:AnimatType
    next_animat_type:AnimatType

    def __init__(self,start_action:BaseAction,loop_action:BaseAction,end_action:BaseAction):
        assert start_action or loop_action or end_action
        self.start_action=start_action
        self.loop_action=loop_action
        self.end_action=end_action

        first_action=start_action or loop_action or end_action
        if first_action.action_type not in settings.COMBO_ACTION_TIMES:
            self.loop_times=1
        else:
            self.loop_times=random.randint(*settings.COMBO_ACTION_TIMES[first_action.action_type])
        self.loop_count=1
        self.cur_animat_type = None
        self.next_animat_type = first_action.animat_type

    def _next_animat_type(self,animat_type:AnimatType,loop_count:int)->AnimatType:
        if animat_type==AnimatType.SINGLE:
            return None
        if animat_type==None or animat_type==AnimatType.C_END:
            return None


        if animat_type == AnimatType.A_START and self.loop_action:
            return AnimatType.B_LOOP
        else:
            animat_type=AnimatType.B_LOOP

        if animat_type == AnimatType.B_LOOP and self.loop_action:
            if loop_count < self.loop_times:
                return AnimatType.B_LOOP
        if animat_type == AnimatType.B_LOOP and self.end_action:
            return AnimatType.C_END
        return None



    def next_action(self)->BaseAction:
        action=self._get_action(self.next_animat_type)
        if action==None:
            self.cur_animat_type=None
            self.next_animat_type=None
            return None
        self.cur_animat_type=action.animat_type
        if self.cur_animat_type ==AnimatType.B_LOOP:
            self.loop_count=self.loop_count+1
        self.next_animat_type=self._next_animat_type(self.cur_animat_type,self.loop_count)
        return action

    def _get_action(self,animat_type:AnimatType)->BaseAction:
        if animat_type==None:
            return None
        return_action=None
        if animat_type==AnimatType.A_START:
            return_action=self.start_action

        elif animat_type in (AnimatType.B_LOOP,AnimatType.SINGLE):
            return_action=self.loop_action

        elif animat_type==AnimatType.C_END:
            return_action=self.end_action

        return return_action


class ActionManager():
    """
    动作管理
    """
    def __init__(self):
        self._init_actions()
        self.search_cache={}


    def _init_actions(self):
        graph_list = []
        for root, dirs, files in os.walk(settings.ACTION_GRAPH_PATH):
            if len(dirs) <= 0 and len(files) > 0: #只看最后一层
                for file in files:
                    graph_list.append(os.path.join(root,file))

        last_dir=""
        self.action_list=[]
        cur_gragh_list=None
        for graph_path in sorted(graph_list):
            cur_dir=(os.sep).join(graph_path.split(os.sep)[0:-1])
            if cur_dir!=last_dir:
                path_pattern=graph_path.replace(os.sep,"_").upper()
                action_type=self._judge_enum(path_pattern,ActionType,ActionType.DEFAULT)
                mood = self._judge_enum(path_pattern, Mood, Mood.NOMAL)
                animat_type = self._judge_enum(path_pattern, AnimatType, AnimatType.SINGLE)
                graph_name=os.path.basename(graph_path)

                if animat_type==AnimatType.A_START:
                    action_name=path_pattern.split("_A_")[0]
                elif animat_type==AnimatType.B_LOOP:
                    action_name = path_pattern.split("_B_")[0]
                    if action_name==path_pattern:
                        action_name = path_pattern.split("循环")[0]
                elif animat_type==AnimatType.C_END:
                    action_name = path_pattern.split("_C_")[0]
                else:
                    action_name= path_pattern.split("_SINGLE_")[0]

                # action_name=os.path.dirname(graph_path).replace(os.sep,"_").upper()
                cur_gragh_list=[Graph(graph_path,int(graph_name.split("_")[-1].split(".")[0]))]
                action=BaseAction(action_name, action_type, animat_type, mood, cur_gragh_list)
                if ".LEFT" in path_pattern:
                    action.direction=-1
                if ".RIGHT" in path_pattern:
                    action.direction=1
                self.action_list.append(action)
                last_dir=cur_dir
            else:
                graph_name = os.path.basename(graph_path)
                cur_gragh_list.append(Graph(graph_path,int(graph_name.split("_")[-1].split(".")[0])))
        # pprint(self.action_list)



    def _judge_enum(self,path_pattern:str,enum:Enum,default:Enum):
        if enum.__name__=='AnimatType': #AnimatType比较特殊
            if "_A_" in path_pattern:
                return AnimatType.A_START
            elif "_B_" in path_pattern or "循环" in path_pattern:
                return AnimatType.B_LOOP
            elif "_C_" in path_pattern:
                return AnimatType.C_END
            else:
                return AnimatType.SINGLE
        else:
            for i in enum:
                if f"{i.name}_" in path_pattern or f"{i.name}." in path_pattern:
                    return i

            return default









    def load_actions(self):
        pass

    def load_one_action(self,action:BaseAction):
        """
        主要是懒加载
        """
        for graph in action.graph_list:
            graph.pixmap=QPixmap(graph.path)
        action.if_load=True
        return action

    def get_actions(self,action_type:ActionType,mood:Mood=None,animat_type:AnimatType=None,action_name:str=None):
        """
        根据心情和动画类型，获取动作
        """
        assert action_type!=None,"必须选定动画类型"
        k=(action_type,mood,animat_type,action_name)
        v=self.search_cache.get(k)
        if v==None:
            v=list(filter(lambda action: action_type in (action.action_type,None) and mood in(action.mood,None)
                        and  animat_type in (action.animat_type,None)  and action_name in (action.action_name,None),
                        self.action_list))
            self.search_cache[k]=v
            return v
        else:
            return v

    def get_one_action(self,action_type:ActionType,mood:Mood=None,animat_type:AnimatType=None,action_name:str=None):
        actions = self.get_actions(action_type, mood,animat_type,action_name)
        if actions == None or actions == []:
            return None
        action = random.choice(actions)
        if not action.if_load:

            action = action_manager.load_one_action(action)

        return action

    def get_seq_actions(self,action_type:ActionType,mood:Mood=None)->SeqAction:
        animat_type=random.choice([AnimatType.SINGLE,AnimatType.A_START])
        if animat_type==AnimatType.SINGLE:
            action=self.get_one_action(action_type,mood,AnimatType.SINGLE)

            if action!=None:
                return SeqAction(None,action,None)

        start_action=self.get_one_action(action_type, mood, AnimatType.A_START)
        action_name=None
        if start_action:
            action_name=start_action.action_name

        loop_action=self.get_one_action(action_type, mood, AnimatType.B_LOOP,action_name)
        if loop_action: #修改逻辑，具体循环次数由宠物类决定
            action_name = loop_action.action_name

        end_action = self.get_one_action(action_type, mood, AnimatType.C_END,action_name)

        if not (start_action or loop_action or end_action):
            single_action=self.get_one_action(action_type, mood, AnimatType.SINGLE)
            if single_action:
                return SeqAction(None,single_action,None)
            else:
                return None
        else:
            seq_action=SeqAction(start_action, loop_action, end_action)

            return seq_action




action_manager=ActionManager()



class Pet():


    def __init__(self):
        self.change_mood()
        self.cur_seq_action:SeqAction=self.get_seq_action(ActionType.STARTUP)

        # self.seq_actions_list=[] #需要这个吗？

        self.action_count=0 #动作总量计数器



    def change_mood(self):
        """
        为什么要不开心的呢？
        :return: 开心or开心的不明显
        """
        mood=random.choice([Mood.HAPPY, Mood.NOMAL])
        self.mood=mood
        return mood




    def next_action(self,action_type:ActionType=None,animat_type:AnimatType=None): #做事涉及到是否能被其他动作打断，暂时不考虑

        if action_type!=None:
            self.cur_seq_action=self.get_seq_action(action_type=action_type)

        if self.cur_seq_action.next_animat_type==None:
            self.cur_seq_action=self.get_seq_action(self._what_to_do())

        self.cur_action=self.cur_seq_action.next_action()

        self.action_count=self.action_count+1
        if self.action_count%20==0:
            self.change_mood()
        return self.cur_action



    def get_seq_action(self,action_type:ActionType)->SeqAction:
        assert action_type!=None
        seq_action=action_manager.get_seq_actions(action_type=action_type, mood=self.mood)
        if seq_action==None:
            seq_action=action_manager.get_seq_actions(action_type=action_type, mood=Mood.NOMAL) or []
        return seq_action





    def _what_to_do(self)->ActionType: #有趣的课题，加权随机
        total = sum(settings.COMMON_ACTION_WEIGHT.values())
        r = random.uniform(0, total)
        upto = 0
        for action_type, weight in settings.COMMON_ACTION_WEIGHT.items():
            if upto + weight >= r:
                return action_type
            upto += weight













