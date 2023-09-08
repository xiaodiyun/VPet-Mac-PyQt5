
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

    # def __init__(self, action_name:str,action_type: ActionType, animat_type: AnimatType,mood:Mood, png_list:[]):
    #     self.action_name = action_name
    #     self.action_type = action_type
    #     self.animat_type = animat_type
    #     self.mood=mood
    #     self.png_list = png_list



class ActionManager():
    """
    动作管理
    """
    def __init__(self):
        self._init_actions()
        self.search_cache={}


    """
    看上去，同情绪，同类型的动作，可以从start-loop-end顺着找
    不是，需要在同类型文件夹下面，暂且归纳为ABC的上一级目录中顺着找（上一级目录为名字，这样按名字区分）
    """
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
            v=list(filter(lambda action: (action.action_type == action_type or action_type == None) and (
                        action.mood == mood or mood == None) and (action.animat_type == animat_type or animat_type == None)  and (action.action_name==action_name or action_name==None),
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

    def get_seq_actions(self,action_type:ActionType,mood:Mood=None):
        animat_type=random.choice([AnimatType.SINGLE,AnimatType.A_START])
        if animat_type==AnimatType.SINGLE:
            action=self.get_one_action(action_type,mood,AnimatType.SINGLE)
            if action!=None:
                return [action]
        seq_actions=[]
        start_action=self.get_one_action(action_type, mood, AnimatType.A_START)
        action_name=None
        if start_action:
            action_name=start_action.action_name
            seq_actions.append(start_action)
        loop_action=self.get_one_action(action_type, mood, AnimatType.B_LOOP,action_name)
        if loop_action:
            action_name = loop_action.action_name
            for i in range(random.randint(*settings.COMBO_ACTION_TIMES[action_type])):
                seq_actions.append(loop_action)
        end_action = self.get_one_action(action_type, mood, AnimatType.C_END,action_name)
        if end_action:
            seq_actions.append(end_action)
        if len(seq_actions)==0:
            single_action=self.get_one_action(action_type, mood, AnimatType.SINGLE)
            if single_action:
                return [self.get_one_action(action_type,mood,AnimatType.SINGLE)]
            else:
                return []
        else:
            return seq_actions




action_manager=ActionManager()



class Pet():


    def __init__(self):
        self.change_mood()
        self.cur_action=None
        self.x=settings.INIT_POS_X
        self.y=settings.INIT_POS_Y
        self.action_list=[]
        self.add_seq_actions(self.choose_seq_actions(ActionType.STARTUP))
        self.action_count=0
        self.last_add_action=None

    def move(self,x,y):
        self.x=x
        self.y=y

    def change_mood(self):
        """
        为什么要不开心的呢？
        :return: 开心or开心的不明显
        """
        mood=random.choice([Mood.HAPPY, Mood.NOMAL])
        self.mood=mood
        return mood

    def next_action(self): #做事涉及到是否能被其他动作打断，暂时不考虑
        if len(self.action_list)==0:
            self.add_seq_actions()
        self.cur_action=self.action_list.pop(0)
        self.action_count=self.action_count+1
        if self.action_count%20==0:
            self.change_mood()
        return self.cur_action

    def add_seq_actions(self,actions:[BaseAction]=None):
        if  actions==None or actions==[]:
            actions=self.choose_seq_actions(self._what_to_do())
        #TODO 动作与动作之间可能需要default动作来过渡，不确定是不是所有动作都需要过渡
        # if self.last_add_action!=None and self.last_add_action.action_type!=ActionType.DEFAULT:
        #     self.action_list = self.action_list+self.choose_seq_actions(ActionType.DEFAULT)
        # self.last_add_action=actions[0]
        self.action_list=self.action_list+actions

    def choose_seq_actions(self,action_type:ActionType)->[BaseAction]:

        actions=action_manager.get_seq_actions(action_type=action_type, mood=self.mood)

        if actions==None or actions==[]:
            actions=action_manager.get_seq_actions(action_type=action_type, mood=Mood.NOMAL) or []
        return actions




    def _what_to_do(self)->ActionType: #有趣的课题，加权随机
        total = sum(settings.COMMON_ACTION_WEIGHT.values())
        r = random.uniform(0, total)
        upto = 0
        for action_type, weight in settings.COMMON_ACTION_WEIGHT.items():
            if upto + weight >= r:
                return action_type
            upto += weight












