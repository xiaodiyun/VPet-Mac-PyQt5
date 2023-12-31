
from enum import Enum
from . import settings
from .dict import Mood,ActionType,AnimatType,ActionStatus
from PyQt5.QtGui import QImage
import os
from pprint import pprint
from dataclasses import dataclass,field

import random



@dataclass()
class Graph():
    """
    图片（动作帧）
    """
    path:str
    """图片位置"""
    duration:int
    """图片持续时间"""
    qimage:QImage=None
    """图片qt实体类"""

    x: int=None
    y: int=None
    width: int = None
    height: int = None

    #图片裁剪区域
    cut_area=[]






class BaseAction():
    # """动作基础类"""
    # action_name: str
    # """动作名称（同名动作在一个动作循环里面）"""
    # action_type: ActionType
    # """动作类型"""
    # animat_type: AnimatType
    # """动画类型"""
    # mood: Mood
    # """心情"""
    # graph_lists:
    # """动作对应的图片序列，一个动作可能同时播放多个图片序列，后面的图片覆盖前面的图片"""
    # graph_indexes:list
    # """动作播放到哪个序列了"""


    """动作是否已初始化"""

    def __init__(self,action_name,action_type,animat_type,mood,graph_lists):
        self.action_name=action_name
        self.action_type = action_type
        self.animat_type = animat_type
        self.mood = mood
        self.graph_lists = graph_lists
        self.graph_indexes=[]
        for i in range(len(self.graph_lists)):
            self.graph_indexes.append(0)
        self.direction = 0
        self.if_load = False

    def replace_graph_list(self,i=None):
        del self.graph_indexes[i]
        del self.graph_lists[i]
    def append_graph_list(self,graph_list,i=None):
        self.graph_indexes.append(0)
        if not i:
            i=len(self.graph_lists)
        self.graph_lists.insert(i,graph_list)

    def is_finished(self):
        for graph_index in self.graph_indexes:
            if graph_index!=-1:
                return False
        return True


    def next_graqh_list(self,i)->Graph:
        """
        获取下一个动作帧图片，如果为None，说明这个动作播放完了
        :return: Graph
        """

        if self.graph_indexes[i]<len(self.graph_lists[i]):
            graph_list=self.graph_lists[i][self.graph_indexes[i]]
            self.graph_indexes[i]=self.graph_indexes[i]+1
            return graph_list
        else:
            self.graph_indexes[i]=-1
            if all(val == -1 for val in self.graph_indexes):
                pass
                # self.reset()
            return None
    def reset(self):
        self.graph_indexes = []
        for i in range(len(self.graph_lists)):
            self.graph_indexes.append(0)






@dataclass()
class SeqAction():
    """
    循环动画序列，比如行走循环分为转身（开始动画）-走路（循环）-走路*n-转回去（结束动画）
    """
    start_action:BaseAction
    """开始动作"""
    loop_action:BaseAction
    """循环动作（如果是single类型也会存在这里）"""
    end_action:BaseAction
    """结束动作"""
    loop_times=10000
    """动作循环次数，受settings.COMBO_ACTION_TIMES控制，默认无限循环直到某个事件打断动作"""
    cur_animat_type:AnimatType
    """当前动画类型"""
    next_animat_type:AnimatType
    """下一个动画类型"""



    def __init__(self,start_action:BaseAction,loop_action:BaseAction,end_action:BaseAction):
        assert start_action or loop_action or end_action
        self.start_action=start_action
        self.loop_action=loop_action
        self.end_action=end_action

        first_action=start_action or loop_action or end_action
        if first_action.action_type not in settings.COMBO_ACTION_TIMES:
            self.loop_times=10000
        else:
            self.loop_times=random.randint(*settings.COMBO_ACTION_TIMES[first_action.action_type])
        self.loop_count=1
        self.cur_animat_type = None
        self.next_animat_type = first_action.animat_type

    def _next_animat_type(self,animat_type:AnimatType,loop_count:int)->AnimatType:
        """
        根据输入的动画类型，判断对应的下一个动画类型是什么

        - 开始动画 -> 结束动画
        - 循环动画 -> 循环动画/结束动画（根据循环次数是否达到上限决定）
        - 循环动画 -> 结束动画
        - 结束动画 -> None

        :param animat_type: 动画类型
        :param loop_count: 当前循环次数
        :return: 下一个动画类型
        """
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



    def next_action(self,animat_type:AnimatType=None)->BaseAction:
        """
        获取下一个动作是什么

        - 开始动作 -> 结束动作
        - 循环动作 -> 循环动作/结束动作（根据循环次数是否达到上限决定）
        - 循环动作 -> 结束动作
        - 结束动作 -> None

        :param animat_type: 如果为None，则由SeqAction自己维护的顺序来依次返回动作；如果不为空，则根据输入的动画类型指定该类型的动作（这个指定也会实际更改顺序）
        :return: 下一个动作；None-当前动作序列全部播放完了
        """
        if animat_type:
            self.next_animat_type=animat_type
        action=self.get_action(self.next_animat_type)
        if action==None:
            self.cur_animat_type=None
            self.next_animat_type=None
            return None
        self.cur_animat_type=action.animat_type
        if self.cur_animat_type ==AnimatType.B_LOOP:
            self.loop_count=self.loop_count+1
            if self.loop_count%3==0 and self.loop_action.action_type==ActionType.RAISED:#部分动作支持循环之间相互替换
                self.loop_action=action_manager.get_one_action(ActionType.RAISED,self.loop_action.mood,AnimatType.B_LOOP)
            if self.loop_count%8==0 and self.loop_action.action_type==ActionType.MOVE:#部分动作支持循环之间相互替换
                self.loop_action=action_manager.get_one_action(ActionType.MOVE,self.loop_action.mood,AnimatType.B_LOOP,self.loop_action.direction)
        self.next_animat_type=self._next_animat_type(self.cur_animat_type,self.loop_count)

            # action.graph_lists=[eat_graqh_list]
        return action

    def get_action(self,animat_type:AnimatType)->BaseAction:
        """
        根据动画类型获取动作
        :param animat_type: 动画类型
        :return: 动作
        """
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
    动作管理类
    """
    def __init__(self):
        self._init_actions()
        self.search_cache={}


    def _init_actions(self):
        """
        装载所有动作
        :return:
        """
        graph_list = []
        for root, dirs, files in os.walk(settings.ACTION_GRAPH_PATH):
            if len(dirs) <= 0 and len(files) > 0: #只看最后一层
                for file in files:
                    graph_list.append(os.path.join(root,file))

        last_dir=""
        action_list=[]
        eat_front_list=[]
        cur_gragh_list=None
        for graph_path in sorted(graph_list):
            cur_dir=(os.sep).join(graph_path.split(os.sep)[0:-1])
            if cur_dir!=last_dir:
                path_pattern=graph_path.replace(os.sep,"_").upper()
                action_type=self._judge_enum(path_pattern,ActionType,ActionType.DEFAULT)
                mood = self._judge_enum(path_pattern, Mood, Mood.NOMAL)
                animat_type = self._judge_enum(path_pattern, AnimatType, AnimatType.SINGLE)
                graph_name=os.path.basename(graph_path)
                if action_type==ActionType.TOUCH_BODY: #这文件结构到底啥情况。。。
                    action_name=graph_path.split("/")[-2]
                elif action_type==ActionType.EAT:
                    action_name =graph_path.split("/")[-3]+'_'+ graph_path.split("/")[-2]
                else:
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

                action = BaseAction(action_name, action_type, animat_type, mood, graph_lists=[cur_gragh_list])  # TODO 此处考虑吃动作
                if action_type==ActionType.EAT and 'front_lay' in action_name:
                    eat_front_list.append(action)
                if ".LEFT" in path_pattern:
                    action.direction=-1
                if ".RIGHT" in path_pattern:
                    action.direction=1
                action_list.append(action)
                last_dir=cur_dir
            else:
                graph_name = os.path.basename(graph_path)
                cur_gragh_list.append(Graph(graph_path,int(graph_name.split("_")[-1].split(".")[0])))
        self.action_list=[]
        for action in action_list:
            if action.action_type==ActionType.EAT:
                if 'back_lay' in action.action_name:
                    self.action_list.append(action)
                    for eat_action in eat_front_list:
                        if eat_action.action_name.replace('front_lay','').replace('back_lay','')==action.action_name.replace('front_lay','').replace('back_lay','') and eat_action.mood==action.mood:

                            action.append_graph_list(eat_action.graph_lists[0])
                            break
            else:
                self.action_list.append(action)
        pass



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
        elif enum.__name__=='ActionType':
            for i in enum:
                if f"{i.value}_" in path_pattern or f"{i.value}." in path_pattern:
                    return i
        else:
            for i in enum:
                if f"{i.name}_" in path_pattern or f"{i.name}." in path_pattern:
                    return i

            return default









    def load_actions(self):
        pass

    def load_one_action(self,action:BaseAction):
        """
        加载一个动作下所有图片的QImage类。主要是为了懒加载
        :param action:动作类
        :return:返回该动作
        """
        for graph_list in action.graph_lists:
            for graph in graph_list:

                graph.qimage=QImage(graph.path)

        action.if_load=True
        return action

    def get_actions(self,action_type:ActionType,mood:Mood=None,animat_type:AnimatType=None,direction:int=None,action_name:str=None):
        """
        根据指定条件，查找所有符合条件的动作
        :param action_type: 动作类型
        :param mood: 心情
        :param animat_type: 动画类型
        :param action_name: 动作名称
        :return: 动作列表
        """
        assert action_type!=None,"必须选定动画类型"
        k=(action_type,mood,animat_type,action_name,direction)
        v=self.search_cache.get(k)
        if v==None:

            v=list(filter(lambda action: action_type==action.action_type and mood in(action.mood,None)
                                         and animat_type in (action.animat_type,None)
                                         and direction in (action.direction,None)
                                         and action_name in (action.action_name,None),
                        self.action_list))
            self.search_cache[k]=v
            return v
        else:
            return v

    def get_one_action(self,action_type:ActionType,mood:Mood=None,animat_type:AnimatType=None,direction:int=None,action_name:str=None):
        """
        根据指定条件，从所有符合条件的动作中随机抽一个动作，如果这个动作没加载的话会帮忙加载
         :param action_type: 动作类型
        :param mood: 心情
        :param animat_type: 动画类型
        :param direction: 动作方向
        :param action_name: 动作名称
        :return: 动作
        """
        actions = self.get_actions(action_type, mood,animat_type,direction,action_name)
        if actions == None or actions == []:
            return None
        action = random.choice(actions)
        if not action.if_load:
            action = action_manager.load_one_action(action)
        return action

    def get_seq_actions(self,action_type:ActionType,mood:Mood=None,direction:int=None,params=[])->SeqAction:
        """
        根据指定条件，查找对应的动作序列
        :param action_type: 动作类型
        :param mood: 心情
        :return: 动作序列类
        """


        animat_type=random.choice([AnimatType.SINGLE,AnimatType.A_START]) #查不到没有start，上来就loop的
        if animat_type==AnimatType.SINGLE:

            action=self.get_one_action(action_type,mood,AnimatType.SINGLE,direction)

            if action!=None:
                if action.action_type == ActionType.EAT:
                    if len(action.graph_lists)>2:
                        action.replace_graph_list(1)
                    action.append_graph_list(self.gen_eat_graqh_list(params[0]),1)
                return SeqAction(None,action,None)

        start_action=self.get_one_action(action_type, mood, AnimatType.A_START,direction)
        action_name=None
        if start_action:
            action_name=start_action.action_name

        loop_action=self.get_one_action(action_type, mood, AnimatType.B_LOOP,direction,action_name)
        if loop_action: #修改逻辑，具体循环次数由宠物类决定
            action_name = loop_action.action_name

        end_action = self.get_one_action(action_type, mood, AnimatType.C_END,direction,action_name)

        if not (start_action or loop_action or end_action):
            single_action=self.get_one_action(action_type, mood, AnimatType.SINGLE,direction)
            if single_action:
                if single_action.action_type == ActionType.EAT:
                    if len(single_action.graph_lists)>2:
                        single_action.replace_graph_list(1)
                    single_action.append_graph_list(self.gen_eat_graqh_list(params[0]),1)
                return SeqAction(None,single_action,None)
            else:
                return None
        else:
            seq_action=SeqAction(start_action, loop_action, end_action)

            return seq_action

    def gen_eat_graqh_list(self,filepath:str):
        if os.path.isdir(filepath):
            filepath="sth.folder"

        filename=os.path.basename(filepath)
        if "." in filename:
            file_extension=filename.split(".")[-1].lower()
        else:
            file_extension="default"
        if file_extension in ('bmp','jpg','jpeg','png','gif','ico','icns'):
            iconpath=filepath
        else:
            iconpath=settings.FILE_ICON_DEFAULT
            for key in settings.FILE_ICON_MAP:
                value=settings.FILE_ICON_MAP[key]
                if file_extension in value:
                    iconpath=key
                    break

        qimage=QImage(iconpath)
        qimage=qimage.scaled(30,30)
        if qimage.isNull():
            qimage=QImage(settings.FILE_ICON_DEFAULT)
        #
        food_animats=[ #此处动画实在兼容不动了，在调整宠物大小之后，一定会不兼容
            # 动画时长,x,y,w,h,截取区域(吃文件=文件图片高度截取)
            [550,60.25, 50, 0, 0,[]],
            [125,60.25, 50, 30, 30,[]],
            [125,60.25, 50, 30, 30,[]],
            [125,60.25, 50, 30, 30,[]],
            [375,60.25, 50, 30, 30,[]],
            [125,60.25, 48, 30, 30,[]],
            [125,60.6, 56, 30, 30,[0,qimage.width()/3,qimage.height(),qimage.width()]],
            [125,60.5, 56, 30, 30,[0,qimage.width()/3,qimage.height(),qimage.width()]],
            [125,60.5, 56, 30, 30,[0,qimage.width()/3,qimage.height(),qimage.width()]],
            [125,60.6, 60, 30, 30,[0,qimage.width()/4,qimage.height(),qimage.width()]],
            [125,60.5, 60, 30, 30,[0,qimage.width()/4,qimage.height(),qimage.width()]],
            [125,60.5, 60, 30, 30,[0,qimage.width()/4,qimage.height(),qimage.width()]],
            [125,60.5, 60, 30, 30,[0,qimage.width()/4,qimage.height(),qimage.width()]],
            [375,60.5, 48, 0, 0,[]],
        ]
        graqh_list=[]
        for food_animat in food_animats:
            graqh=Graph(iconpath,food_animat[0],qimage)
            graqh.x=food_animat[1]
            graqh.y = food_animat[2]
            graqh.width = food_animat[3]
            graqh.height = food_animat[4]
            graqh.cut_area=food_animat[5]
            graqh_list.append(graqh)
            # print(graqh)

        return graqh_list



action_manager=ActionManager()



class Pet():


    def __init__(self):
        self.cur_action:BaseAction = None
        self.change_mood()
        self.direction=0  #这个direction仅受ui类的动作线程实际控制，以避免动作和方向不一致的情况。因为调用change_action后不一定立刻播放动作
        self.action_count = 0  # 动作总量计数器
        # self.vx=0 #速度应当绑定动作，这样上一个动作结束时，速度不会被自动带入到下一个动作
        # self.vy=0

        self.x=0
        self.y=0
        self.move_flag=False

        self.change_action(ActionType.STARTUP)





        # if settings.LAZY_LOAD:
        #     #只加载提起的动作，因为这个动作加载容易影响交互
        #     for action in action_manager.get_actions(ActionType.STARTUP):
        #         action_manager.load_one_action(action)
        #     for action in action_manager.get_actions(ActionType.DEFAULT):
        #         action_manager.load_one_action(action)
        #     for action in action_manager.get_actions(ActionType.RAISED):
        #         action_manager.load_one_action(action)
        # else:
        # for action in action_manager.action_list:
        #     action_manager.load_one_action(action)
        # pprint(action_manager.action_list)



    #
    #
    # def change_action_status(self,action_status:ActionStatus=ActionStatus.DEFAULT):
    #     self.action_status=action_status


    def change_mood(self):
        """
        宠物换心情
        :return: 为什么要不开心的呢？开心or开心的不明显
        """
        mood=random.choice([Mood.HAPPY, Mood.NOMAL])
        # mood = random.choice([Mood.HAPPY, Mood.HAPPY])
        self.mood=mood
        return mood



    def change_action(self,action_type:ActionType=None,direction:int=None,interrupt=4,params=[]):
        """
        宠物更改当前动作
        :param action_type: 动作类型
        :param direction: 动作方向
        :param interrupt: 打断等级。1-等当前动作做完，再进行新动作；2-强制当前动作进入end阶段，然后进入新动作；3-强制打断当前动作，进入新动作，如果当前正在做这个动作的话，则不处理 4-强制打断当前动作，进入新动作；
        :return:None
        """
        if self.cur_action and not(interrupt==3 and  self.cur_action.action_type==action_type and self.cur_action.direction==direction):
            self.cur_action.reset()
        if interrupt==4 or (interrupt==3 and not( self.cur_action.action_type==action_type and self.cur_action.direction==direction)):


            self.cur_seq_action=self.get_seq_action(action_type=action_type,direction=direction,params=params)
            self.cur_action=self.cur_seq_action.next_action()



        elif interrupt==2:

            self.cur_action=self.next_action(AnimatType.C_END)
            self.cur_seq_action = self.get_seq_action(action_type=action_type, direction=direction,params=params)
        self.direction = self.cur_action.direction








    def next_action(self,animat_type:AnimatType=None)->BaseAction:
        """
        宠物开始进行下一个动作
        :param animat_type: 动画类型，直接指定宠物当前动作的阶段（比如指定播放宠物爬行动作的循环部分）
        :return: 动作
        """
        # if action_type!=None:
        #     self.cur_seq_action=self.get_seq_action(action_type=action_type)
        self.action_count = self.action_count + 1
        if self.action_count%20==0:
            self.change_mood()

        if animat_type!=None:
            self.cur_action = self.cur_seq_action.next_action(animat_type)

            return self.cur_action

        if self.cur_seq_action.next_animat_type==None:
            self.cur_seq_action=self.get_seq_action(self._what_to_do())

            self.move_flag=False
        self.cur_action=self.cur_seq_action.next_action()

        if self.action_count%20==0:
            self.change_mood()

        return self.cur_action



    def get_seq_action(self,action_type:ActionType,direction:int=None,params=[])->SeqAction:
        """
        根据条件查找动作序列
        :param action_type: 动作类型
        :return: 动作序列
        """

        assert action_type!=None
        seq_action=action_manager.get_seq_actions(action_type=action_type, mood=self.mood,direction=direction,params=params)

        if seq_action==None:
            seq_action=action_manager.get_seq_actions(action_type=action_type, mood=Mood.NOMAL,params=params)
            if seq_action == None:
                seq_action = action_manager.get_seq_actions(action_type=action_type, mood=Mood.HAPPY,params=params) or []
        return seq_action





    def _what_to_do(self)->ActionType:
        """
        默认情况下，宠物的动作选择，根据`settings.COMMON_ACTION_WEIGHT`配置来进行加权随机
        :return:
        """
        total = sum(settings.COMMON_ACTION_WEIGHT.values())
        r = random.uniform(0, total)
        upto = 0
        for action_type, weight in settings.COMMON_ACTION_WEIGHT.items():
            if upto + weight >= r:
                return action_type
            upto += weight



    def next_gragh_list(self,i):
        """
        获取宠物下一个动作帧
        :return: 动作帧
        """
        if  self.cur_action:
            graqh=self.cur_action.next_graqh_list(i)
            return graqh
            # if not graqh:
            #     self.next_action()
            #     # print("aaa")
            #     return self.next_gragh()
            # return graqh
        else:
            # self.next_action()
            return None










