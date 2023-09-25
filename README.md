# VPet-Mac

文档传送门：[中文](https://github.com/xiaodiyun/VPet-Mac-PyQt5) |
[English](https://translate.google.com.hk/?sl=zh-CN&tl=en)

虚拟桌宠模拟器mac版，用pyqt5实现。 <br/>

源项目传送门：[VPet](https://github.com/LorisYounger/VPet)

本质上是偷了图包之后重写的逻辑，所以和原版可能有较大差别。是的，我没用过这款软件（甚至进不了群，因为我不会用 c# 做 mod！！😭），这也是这个项目诞生的主要目的，mac也要养宠物！


### 版权声明
动画文件版权归 [源项目](https://github.com/LorisYounger/VPet) 所有

### 兼容性
仅兼容我自己的电脑，~~麻烦跑不通的参照我的配置买电脑~~
- mac m1，系统版本 13.3.1 (22E261)
- qt 版本 5.15.7
- python 版本 3.8

盲猜windows跑不通，因为弱智 mac m1 需要添加一些额外代码来驾驶pyqt5，尤其是透明背景。提 pr 我也没办法验证，除非v我一台 windows 电脑



### 开发计划
- 原地动作播放 ✅
- 加入提起动作 ✅ <br><br>
![提起](tutorial/raise.gif)
  <br><br>
- 加入攀爬等移动动作 ✅<br><br>
![攀爬](tutorial/climb.gif)
   <br><br>
- 加入下落动作 ✅<br><br>
![下落](tutorial/fall.gif)
   <br><br>
- 上下触摸交互 ✅<br><br>
![触摸](tutorial/touch.gif)
<br><br>
- 加入工作交互
- 加入睡觉交互
- 加入短时间多次点击后进入生气状态的交互
- 加入音乐交互
- 加入吃文件交互 ✅ (附带了复制文件路径和文件归档功能)
  <br><br>
![吃吃吃](tutorial/eat.gif)
<br><br>
- 加入鼠标跟随交互
- 再后续看心情。

### 一些问题
python似乎无法越过mac的权限，实现在全部窗口置顶的效果（不过好像可以通过第三方软件进行置顶），所以只能在桌面置顶。如果有方法的话请告诉我

