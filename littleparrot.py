import sys
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon
from PyQt5.QtGui import QIcon
from ui.main_window import MainWindow

def main():
    # 防止程序退出后图标残留
    try:
        import ctypes
        myappid = 'fengzili.littleparrot.pomodoro.v1'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except:
        pass

    app = QApplication(sys.argv)
    
    # 检查系统是否支持系统托盘
    if not QSystemTrayIcon.isSystemTrayAvailable():
        raise SystemExit("System tray is not available on this system")

    # 设置应用程序不会在最后一个窗口关闭时退出
    app.setQuitOnLastWindowClosed(False)
    
    window = MainWindow()
    window.show()
    
    # 确保程序不会过早退出
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main()) 