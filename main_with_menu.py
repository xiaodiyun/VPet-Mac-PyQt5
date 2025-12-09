
import os
import sys
from Foundation import NSBundle, NSLog, NSTimer
from Cocoa import (
    NSStatusBar,
    NSMenu,
    NSMenuItem,
    NSObject,
    NSApplication,
    NSImage,
    NSVariableStatusItemLength,
    NSOffState,
    NSOnState
)
from PyObjCTools import AppHelper
from modules.share import get_application
from  modules.ui import DesktopPet
from PyQt5.QtWidgets import QApplication
from modules import settings
# --- 全局变量 ---
_qt_app = None
_qt_window = None
_menu_item = None
move_item = True







# --- 关键：延迟初始化 PyQt 相关菜单项 ---
def lazy_init_pyqt_menu():
    """在应用启动后异步初始化 PyQt 和菜单"""
    global _menu_item,move_item


    # 创建菜单项（现在才创建，避免阻塞启动）
    _menu_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
        "显示宠物", "toggleWindow:", ""
    )
    _menu_item.setState_(NSOffState)

    move_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
        "允许乱跑", "toggleMove:", ""
    )
    move_item.setState_(NSOnState)  # 初始关闭

    actions_menu = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
        "动作", None, ""
    )


    submenu = NSMenu.alloc().init()
    actions_menu.setSubmenu_(submenu)


    for action in settings.MENU_MAP.keys():
        item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            action, "changeAction:", ""
        )
        submenu.addItem_(item)


    # 获取 AppDelegate 实例（通过 NSApp）
    delegate = NSApplication.sharedApplication().delegate()
    menu = delegate.status_item.menu()
    if menu is None:
        menu = NSMenu.alloc().init()
        # 插入到第一个位置
        menu.addItem_(_menu_item)
        menu.addItem_(move_item)
        menu.addItem_(actions_menu)
        menu.addItem_(NSMenuItem.separatorItem())

        quit_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "拜拜~", "terminate:", ""
        )
        menu.addItem_(quit_item)
        delegate.status_item.setMenu_(menu)
    else:
        # 如果已有菜单，替换或插入
        menu.insertItem_atIndex_(_menu_item, 0)




def show_or_toggle_window():
    global _qt_app, _qt_window
    if _qt_app is None:
        _qt_app = QApplication.instance() or QApplication([])
    if _qt_window is None:
        _qt_window = DesktopPet()
    _qt_window.show()
    _qt_window.raise_()
    _qt_window.activateWindow()
    if _menu_item:

        _menu_item.setState_(NSOnState)


# --- AppDelegate ---
class AppDelegate(NSObject):
    def applicationDidFinishLaunching_(self, notification):

        self.status_item = NSStatusBar.systemStatusBar().statusItemWithLength_(NSVariableStatusItemLength)



        self.performSelector_withObject_afterDelay_(
            "initFullMenu:", None, 0.1
        )
        self.performSelector_withObject_afterDelay_("showDefaultWindow:", None, 0.3)

    def initFullMenu_(self, sender):
        """异步初始化完整菜单"""
        # 换成正式图标（可选）
        # self.status_item.setTitle_("🔧")
        image = NSImage.alloc().initWithContentsOfFile_('icon.png')
        if image:
            image.setSize_((36, 26))
            self.status_item.setImage_(image)


        lazy_init_pyqt_menu()

    def toggleWindow_(self, sender):
        global _qt_window, _menu_item
        if _qt_window is not None and _qt_window.isVisible():
            _qt_window.close()
            if _menu_item:
                _menu_item.setState_(NSOffState)
        else:
            show_or_toggle_window()

    def showDefaultWindow_(self, sender):
        show_or_toggle_window()  # 你已有的函数

    def toggleMove_(self, sender):
        global move_item
        if sender.state()==NSOnState:
            settings.MOVE_VX_BAK=settings.MOVE_VX
            settings.MOVE_VX=[0,0]
            settings.MOVE_VY_BAK = settings.MOVE_VY
            settings.MOVE_VY = [0, 0]
            move_item.setState_(NSOffState)
        else:
            settings.MOVE_VX=settings.MOVE_VX_BAK
            settings.MOVE_VY = settings.MOVE_VY_BAK
            move_item.setState_(NSOnState)

    def changeAction_(self, sender):
        title = sender.title()
        action=settings.MENU_MAP[title]
        global _qt_window
        _qt_window.pet.change_action(action)



def main():
    app = NSApplication.sharedApplication()
    delegate = AppDelegate.alloc().init()
    app.setDelegate_(delegate)
    AppHelper.runEventLoop()


if __name__ == "__main__":
    main()