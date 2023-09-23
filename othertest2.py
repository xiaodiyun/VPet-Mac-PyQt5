from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QMimeDatabase

app = QApplication([])

# 创建QMimeDatabase实例
mime_db = QMimeDatabase()

# 根据文件路径获取MIME类型
mime_type = mime_db.mimeTypeForFile('/Users/diyun/Downloads/QQ20230922-201905.gif')

# 获取MIME类型对应的图标
icon = QIcon.fromTheme("application-x-archive")

# 将图标设置为窗口的图标
app.setWindowIcon(icon)

# 显示窗口
app.exec_()
