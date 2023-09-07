
from enum import Enum
from . import settings
from .dict import Mood,ActionType,AnimatType
from PyQt5.QtGui import QPixmap
import os
from dataclasses import dataclass
import pprint
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
    if_load=False

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
                action_type=self._judge_enum(path_pattern,ActionType,ActionType.COMMON)
                mood = self._judge_enum(path_pattern, Mood, Mood.NORMAL)
                animat_type = self._judge_enum(path_pattern, AnimatType, AnimatType.SINGLE)
                graph_name=os.path.basename(graph_path)
                action_name=graph_name.split("_")[0]
                cur_gragh_list=[Graph(graph_path,int(graph_name.split("_")[-1].split(".")[0]))]
                self.action_list.append(BaseAction(action_name,action_type,animat_type,mood,cur_gragh_list))
                last_dir=cur_dir
            else:
                graph_name = os.path.basename(graph_path)
                cur_gragh_list.append(Graph(graph_path,int(graph_name.split("_")[-1].split(".")[0])))
        # pprint.pp(action_list)



    def _judge_enum(self,path_pattern:str,enum:Enum,default:Enum):
        if enum.__name__=='AnimatType': #AnimatType比较特殊
            if "_A_" in path_pattern:
                return AnimatType.A_START
            elif "_B_" in path_pattern:
                return AnimatType.B_LOOP
            elif "_C_" in path_pattern:
                return AnimatType.C_END
            else:
                return AnimatType.SINGLE
        else:
            for i in enum:
                if f"{i.name}_" in path_pattern:
                    return i

            return default




    def _init_actions_bak(self):
        self.action_map={}
        action_types=os.listdir(settings.ACTION_GRAPH_PATH)


    #     for action_type in action_types:
    #         path=os.path.join(settings.ACTION_GRAPH_PATH,action_type)
    #         action_type=action_type.upper()
    #         if os.path.isdir(path):
    #
    #             self.action_map.setdefault(ActionType[action_type],[])
    #             action_list=self.action_map[ActionType[action_type]]
    #             #
    #
    #
    #             """
    #             解析逻辑总结：
    #             1.倒数第一层文件里面是同一个动画序列
    #             2.路径包含 Happy,Normal等，就是触发心情
    #             3.路径包含 A、B、C单独文件夹，或者A_、B_、C_就是动画类型，字典见AnimatType
    #             4.部分需要特殊处理以区分动作名字
    #             """
    #             for root, dirs, files in os.walk(path):
    #                 if len(dirs)<=0 and len(files)>0: #只看最后一层
    #                     files.sort()
    #                     graph_list=[]
    #                     for file in files:
    #                         graph_list.append(Graph(os.path.join(root,file),int(file.split("_")[-1].split(".")[0])))
    #                     rootupper=root.upper()
    #                     rootsplit = rootupper.split(os.sep)
    #                     action_name = rootsplit[rootsplit.index(action_type) + 1]
    #                     relative_path=rootupper.replace(settings.ACTION_GRAPH_PATH,"")
    #                     animat_type=self._judge_animat_type(relative_path)
    #                     mood=self._judge_mood(relative_path)
    #
    #                     #这个action_name暂时没用到
    #                     if action_type  in ('RAISE','STATE'):
    #                         action_type_name=action_name
    #                     elif action_type=='SWITCH':
    #                         action_type_name=action_type+"_"+action_name
    #                     else:
    #                         action_type_name=action_type
    #                     action_list.append(BaseAction(action_name,ActionType[action_type_name],animat_type,mood,graph_list))
    #
    #     pprint.pprint(self.action_map)
    #
    #
    #
    # def _judge_if_path_contains(self,path_split,pattern)->bool:
    #     return len([i for i in path_split if i.startswith(pattern+"_") or i.endswith("_"+pattern) or i==pattern]) > 0
    #
    # def _judge_animat_type(self,path)->AnimatType:
    #     # path=path.upper()
    #     path_split = path.split(os.sep)
    #     if  self._judge_if_path_contains(path_split,'A'):
    #         return AnimatType.A_START
    #     elif self._judge_if_path_contains(path_split,'B'):
    #         return AnimatType.B_LOOP
    #     elif self._judge_if_path_contains(path_split,'C'):
    #         return AnimatType.C_END
    #     elif self._judge_if_path_contains(path_split,'SINGLE'):
    #         return AnimatType.SINGLE
    #     else:
    #         return AnimatType.SINGLE
    # def _judge_mood(self,path)->Mood:
    #     # path = path.upper()
    #     path_split = path.split(os.sep)
    #     if self._judge_if_path_contains(path_split, 'NORMAL'):
    #         return Mood.NORMAL
    #     elif self._judge_if_path_contains(path_split, 'HAPPY'):
    #         return Mood.HAPPY
    #     elif self._judge_if_path_contains(path_split, 'POORCONDITION'):
    #         return Mood.POORCONDITION
    #     elif self._judge_if_path_contains(path_split, 'ILL'):
    #         return Mood.ILL
    #     else:
    #         return Mood.NORMAL




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

    def get_actions(self,action_type:ActionType,mood:Mood=None,animat_type:AnimatType=None):
        """
        根据心情和动画类型，获取动作
        """
        assert action_type!=None,"必须选定动画类型"
        k=(action_type,mood,animat_type)
        v=self.search_cache.get(k)
        if v==None:
            v=list(filter(lambda action: (action.action_type == action_type or action_type == None) and (
                        action.mood == mood or mood == None) and (action.animat_type == animat_type or animat_type == None),
                        self.action_list))
            self.search_cache[k]=v
            return v
        else:
            return v

    def get_one_action(self,**param):
        action_list=self.get_actions(**param)
        action=random.choice(action_list)
        if not action.if_load:
            action=action_manager.load_one_action(action)
        return action



action_manager=ActionManager()



class Pet():


    def __init__(self):
        self.change_mood()
        self.cur_action=None
        self.x=settings.INIT_POS_X
        self.y=settings.INIT_POS_Y
        self.action_list=[]
        self.add_action(self.choose_action(ActionType.STARTUP))
        self.action_count=0

    def move(self,x,y):
        self.x=x
        self.y=y

    def change_mood(self):
        """
        为什么要不开心的呢？
        :return: 开心or开心的不明显
        """
        mood=random.choice([Mood.HAPPY, Mood.NORMAL])
        self.mood=mood
        return mood

    def next_action(self): #做事涉及到是否能被其他动作打断，暂时不考虑
        self.cur_action=self.action_list.pop()
        self.action_count=self.action_count+1
        if self.action_count%10==0:
            self.change_mood()
        return self.cur_action

    def add_action(self,action:BaseAction=None):
        if  action==None:
            self.action_list.append(self.choose_action(ActionType.DEFAULT))
        else:
            self.action_list.append(action)

    def choose_action(self,action_type:ActionType):
        self.cur_action=action_manager.get_one_action(action_type=action_type,mood=self.mood)
        return self.cur_action











