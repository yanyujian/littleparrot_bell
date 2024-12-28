from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QInputDialog,
                             QComboBox, QMessageBox, QSystemTrayIcon,
                             QMenu, QAction, QFrame, QApplication, QSlider,
                             QDialog, QLineEdit, QSpinBox, QTableWidget,
                             QTableWidgetItem, QHeaderView, QTextEdit, QActionGroup)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon, QPalette, QColor, QPixmap, QPainter, QBrush
from PyQt5.QtWidgets import QStyle
from database.db_manager import DatabaseManager
import os
from utils.config_manager import ConfigManager
from utils.language_manager import LanguageManager
import xlsxwriter
from datetime import datetime

from utils import sysHelper


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # 添加配置管理器
        self.config = ConfigManager()
        self.currentProjectIndex = self.config.get('current_project_index')
        self.db = DatabaseManager()
        self.timer = QTimer()

        # 添加预设时间选项（分钟）
        self.time_presets = [15, 20, 25, 30, 45, 60]
        self.default_time = self.config.get("duration") * 60
        self.remaining_time = self.default_time

        # 设置应用主题色
        self.primary_color = "#1E88E5"  # 主要蓝色
        self.secondary_color = "#212121"  # 深色背景
        self.accent_color = "#4CAF50"  # 绿色
        self.text_color = "#FFFFFF"  # 文本色

        # 初始化拖动位置
        self.drag_position = None

        # 定义菜单样式
        self.menu_style = """
            QMenu {
                background-color: rgba(33, 33, 33, 230);
                color: white;
                border: 1px solid #4CAF50;
            }
            QMenu::item:selected {
                background-color: rgba(30, 136, 229, 180);
            }
        """

        # 设置应用图标
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'icon.ico')
        if os.path.exists(icon_path):
            self.app_icon = QIcon(icon_path)
            self.setWindowIcon(self.app_icon)
        else:
            # 使用系统默认图标
            self.app_icon = self.style().standardIcon(QStyle.SP_ComputerIcon)  # 改用 SP_ComputerIcon

        # 加载背景图片
        bg_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images', 'littleparrot.png')
        self.background = QPixmap(bg_path)
        if self.background.isNull():
            print(f"Warning: Failed to load background image from {bg_path}")
            self.background = QPixmap(32, 32)  # 创建一个空背景

        # 设置窗口背景为半透明黑色
        self.overlay_color = QColor(0, 0, 0, 180)  # RGBA，最后一个值是透明度

        # 设置窗口位置
        pos = self.config.get("window_position")
        self.move(pos["x"], pos["y"])

        # 设置窗口透明度
        self.setWindowOpacity(self.config.get("opacity"))

        # 设置窗口标志
        flags = Qt.Tool | Qt.FramelessWindowHint
        if self.config.get("always_on_top"):
            flags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)

        # 添加语言管理器
        self.lang_manager = LanguageManager()
        self.current_lang = self.config.get("language")

        self.init_ui()
        self.init_timer()
        self.init_tray()

    def init_ui(self):
        self.setWindowTitle(self.tr("pomodoro_timer"))
        self.setFixedSize(320, 220)

        # 创建中央部件并设置透明背景
        central_widget = QWidget()
        central_widget.setAttribute(Qt.WA_TranslucentBackground)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        # 修改时间框架样式
        time_frame = QFrame()
        time_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        time_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #4CAF50;
                border-radius: 10px;
                background-color: rgba(33, 33, 33, 180);
                padding: 10px;
            }
        """)
        time_layout = QVBoxLayout(time_frame)

        # 时间显示标签
        self.time_label = QLabel(f"{self.config.get('duration'):02}:00")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet(f"""
            font-size: 48px;
            color: {self.accent_color};
            font-weight: bold;
            margin: 5px 0;
        """)
        time_layout.addWidget(self.time_label)
        layout.addWidget(time_frame)

        # 修改按钮样式
        button_style = """
            QPushButton {
                background-color: rgba(30, 136, 229, 200);
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(33, 150, 243, 220);
            }
            QPushButton:pressed {
                background-color: rgba(25, 118, 210, 220);
            }
        """

        # 创建水平布局来设置控制按钮
        control_layout = QHBoxLayout()
        control_layout.setSpacing(8)

        # 开始/停止按钮
        self.start_button = QPushButton(self.tr("start"))
        self.start_button.clicked.connect(self.toggle_timer)
        self.start_button.setStyleSheet(button_style)
        control_layout.addWidget(self.start_button)

        # 重置按钮
        self.reset_button = QPushButton(self.tr("reset"))
        self.reset_button.clicked.connect(self.reset_timer)
        self.reset_button.setStyleSheet(button_style)
        control_layout.addWidget(self.reset_button)

        layout.addLayout(control_layout)

    def init_timer(self):
        self.timer.timeout.connect(self.update_timer)
        self.timer.setInterval(1000)  # 1秒

    def init_tray(self):
        """初始化系统托盘图标"""
        # 确保在初始化之前没有存在的托盘图标
        if hasattr(self, 'tray_icon'):
            self.tray_icon.hide()
            del self.tray_icon

        self.tray_icon = QSystemTrayIcon(self)

        # 使用一个明显的系统图标
        icon = self.style().standardIcon(QStyle.SP_MediaPlay)
        self.tray_icon.setIcon(icon)

        # 创建托盘菜单
        tray_menu = QMenu()
        tray_menu.setStyleSheet(self.menu_style)  # 使用自定义菜单样式

        # 显示/隐藏主窗口
        toggle_window_action = QAction(self.tr("show_hide"), self)
        toggle_window_action.triggered.connect(self.toggle_window)
        tray_menu.addAction(toggle_window_action)

        # 开始/停止计时
        self.tray_timer_action = QAction(self.tr("start"), self)
        self.tray_timer_action.triggered.connect(self.toggle_timer)
        tray_menu.addAction(self.tray_timer_action)

        # 重置时间
        reset_action = QAction(self.tr("reset"), self)
        reset_action.triggered.connect(self.reset_timer)
        tray_menu.addAction(reset_action)

        # 添加时间设置菜单
        time_menu = QMenu(self.tr("set_timer"), self)
        time_menu.setObjectName("time_menu")
        time_menu.setStyleSheet(self.menu_style)

        # 添加预设时间选项
        for minutes in self.time_presets:
            action = QAction(f"{minutes} {self.tr('minutes')}", self)
            action.setObjectName(f"preset_{minutes}")
            action.triggered.connect(lambda checked, m=minutes: self.set_timer_duration(m))
            time_menu.addAction(action)

        # 添加自定义时间选项
        custom_time_action = QAction(self.tr("custom"), self)
        custom_time_action.setObjectName("custom_time")
        custom_time_action.triggered.connect(self.set_custom_timer_duration)
        time_menu.addAction(custom_time_action)

        # 将时设置菜单添加到菜单
        tray_menu.addMenu(time_menu)

        # 将添加项目移到设置菜单中
        settings_menu = QMenu(self.tr("settings"), self)
        settings_menu.setObjectName("settings_menu")  # 设置对象名称
        settings_menu.setStyleSheet(self.menu_style)

        # 添加项目选项
        add_project_action = QAction(self.tr("add_project"), self)
        add_project_action.setObjectName("add_project_action")
        add_project_action.triggered.connect(self.add_project)
        settings_menu.addAction(add_project_action)

        settings_menu.addSeparator()

        # 添加置顶选项
        always_on_top_action = QAction(self.tr("always_on_top"), self)
        always_on_top_action.setObjectName("always_on_top_action")
        always_on_top_action.setCheckable(True)
        always_on_top_action.setChecked(self.config.get("always_on_top"))
        always_on_top_action.triggered.connect(self.toggle_always_on_top)
        settings_menu.addAction(always_on_top_action)

        # 添加透明度设置子菜单
        opacity_menu = QMenu(self.tr("opacity"), self)
        opacity_menu.setObjectName("opacity_menu")  # 设置对象名称
        opacity_menu.setStyleSheet(self.menu_style)

        opacity_values = [0.15, 0.3, 0.5, 0.7, 0.8, 0.9, 1.0]
        current_opacity = self.config.get("opacity")

        def changeOpacity(newOpacity):
            self.set_opacity(newOpacity)
            # lambda checked, o=opacity: self.set_opacity(o)
            selectedIndex = opacity_values.index(newOpacity)
            # opacity_menu.actions()[selectedIndex].setChecked(True)
            for index, tempAction in enumerate(opacity_menu.actions()):
                tempAction.setChecked(selectedIndex == index)

        for opacity in opacity_values:
            action = QAction(f"{int(opacity * 100)}%", self)
            action.setCheckable(True)
            action.setChecked(abs(opacity - current_opacity) < 0.01)
            action.triggered.connect(lambda checked, o=opacity: changeOpacity(o))
            opacity_menu.addAction(action)

        settings_menu.addMenu(opacity_menu)

        # 在 Settings 菜单中添加查看项目统计的选项
        settings_menu.addSeparator()
        stats_action = QAction(self.tr("project_statistics"), self)
        stats_action.setObjectName("stats_action")
        stats_action.triggered.connect(self.show_project_statistics)
        settings_menu.addAction(stats_action)

        # 添加语言切换菜单
        lang_menu = QMenu(self.tr("language"), self)
        lang_menu.setObjectName("language_menu")
        lang_menu.setStyleSheet(self.menu_style)

        # 添加语言选项
        lang_group = QActionGroup(self)
        lang_group.setExclusive(True)

        for lang, name in [("en", "English"), ("zh", "中文")]:
            action = QAction(name, self)
            action.setObjectName(f"lang_{lang}")
            action.setCheckable(True)
            action.setChecked(self.current_lang == lang)
            action.setData(lang)
            action.triggered.connect(lambda checked, l=lang: self.change_language(l))
            lang_group.addAction(action)
            lang_menu.addAction(action)

        settings_menu.addMenu(lang_menu)

        # 将设置菜单添加到主菜单
        tray_menu.addMenu(settings_menu)

        # 添加分隔线
        tray_menu.addSeparator()

        # 添加项目统计选项（移到这里）
        stats_action = QAction(self.tr("project_statistics"), self)
        stats_action.setObjectName("stats_action")
        stats_action.triggered.connect(self.show_project_statistics)
        tray_menu.addAction(stats_action)

        # 添加分隔线
        tray_menu.addSeparator()
        export_action = QAction(self.tr("export"), self)
        export_action.triggered.connect(self.export_data)
        tray_menu.addAction(export_action)
        tray_menu.addSeparator()

        # 添加关于选项
        about_action = QAction(self.tr("about"), self)
        about_action.triggered.connect(self.show_about_dialog)
        tray_menu.addAction(about_action)

        # 添加分隔线
        tray_menu.addSeparator()

        # 退出程序
        quit_action = QAction(self.tr("quit"), self)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.setToolTip("Pomodoro Timer")

        # 确保图显示并处理激活事件
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.tray_icon_activated)

    def toggle_window(self):
        """切换窗口显示状态"""
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.activateWindow()

    def tray_icon_activated(self, reason):
        """处理托盘图标的激活事件"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.toggle_window()

    def quit_application(self):
        """退出应用程序"""
        self.tray_icon.hide()
        QApplication.quit()

    def reset_timer(self):
        """重置计时器"""
        self.timer.stop()
        self.remaining_time = self.default_time
        minutes = self.default_time // 60
        self.time_label.setText(f"{minutes:02d}:00")
        self.start_button.setText("Start")
        self.tray_timer_action.setText("Start")
        self.tray_icon.setToolTip(f"Pomodoro Timer - {minutes:02d}:00")

    def toggle_timer(self):
        if self.timer.isActive():
            self.timer.stop()
            self.start_button.setText("Start")
            self.tray_timer_action.setText("Start")
        else:
            self.timer.start()
            self.start_button.setText("Stop")
            self.tray_timer_action.setText("Stop")

    def update_timer(self):
        """更新的update_timer方法，同时更新托盘图标提示"""
        self.remaining_time -= 1
        minutes = self.remaining_time // 60
        seconds = self.remaining_time % 60
        time_text = f"{minutes:02d}:{seconds:02d}"

        if self.remaining_time <= 0:
            self.timer.stop()
            self.start_button.setText("Start")
            self.tray_timer_action.setText("Start")
            # 显示下一次的时间而不是 0:00
            next_minutes = self.default_time // 60
            self.time_label.setText(f"{next_minutes:02d}:00")
            self.tray_icon.setToolTip(f"Pomodoro Timer - {next_minutes:02d}:00")
            self.remaining_time = self.default_time  # 重置时间
            self.tray_icon.showMessage(
                "Pomodoro Timer",
                "Time's up! Please record your work.",
                QSystemTrayIcon.Information,
                2000  # 显示2秒
            )
            self.show_task_dialog()
        else:
            self.time_label.setText(time_text)
            self.tray_icon.setToolTip(f"Pomodoro Timer - {time_text}")

    def add_project(self):
        """添加新项目的对话"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Project")
        dialog.setFixedSize(300, 150)
        dialog.setStyleSheet(f"""
            QDialog {{
                background-color: {self.secondary_color};
                color: {self.text_color};
                border: 2px solid {self.accent_color};
                border-radius: 10px;
            }}
            QLabel {{
                color: {self.text_color};
                font-size: 12px;
            }}
            QLineEdit {{
                background-color: rgba(255, 255, 255, 0.1);
                color: {self.text_color};
                border: 1px solid {self.accent_color};
                border-radius: 4px;
                padding: 5px;
                font-size: 12px;
            }}
            QPushButton {{
                background-color: {self.primary_color};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #2196F3;
            }}
            QPushButton:pressed {{
                background-color: #1976D2;
            }}
        """)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # 项目名��输入
        name_label = QLabel("Project Name:")
        layout.addWidget(name_label)

        name_input = QLineEdit()
        name_input.setPlaceholderText("Enter project name...")
        layout.addWidget(name_input)

        # 按钮布局
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
            }
            QPushButton:hover {
                background-color: #E53935;
            }
            QPushButton:pressed {
                background-color: #D32F2F;
            }
        """)

        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        save_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)

        if dialog.exec() == QDialog.Accepted:
            name = name_input.text().strip()
            if name:
                if self.db.add_project(name):
                    self.show_message("Success", "Project added successfully!")
                else:
                    self.show_message("Error", "Failed to add project. It may already exist.", QMessageBox.Warning)

    def update_project_items(self, project_combo: QComboBox):
        # 获取项目列表
        while len(projects := self.db.get_projects()) == 0:
            self.show_message("Warning", "Please add a project first!", QMessageBox.Warning)
        for project_id, project_name in projects:
            if project_combo.findData(project_id) == -1:
                project_combo.addItem(project_name, project_id)

    def show_task_dialog(self):
        """显示任务完成对话框"""
        # 创建自定义对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("Complete Task")
        dialog.setFixedSize(400, 300)  # 增加高度
        dialog.setStyleSheet(f"""
            QDialog {{
                background-color: {self.secondary_color};
                color: {self.text_color};
                border: 2px solid {self.accent_color};
                border-radius: 10px;
            }}
            QLabel {{
                color: {self.text_color};
                font-size: 12px;
                margin-bottom: 5px;
            }}
            QTextEdit {{
                background-color: rgba(255, 255, 255, 0.1);
                color: {self.text_color};
                border: 1px solid {self.accent_color};
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }}
            QComboBox {{
                background-color: rgba(255, 255, 255, 0.1);
                color: {self.text_color};
                border: 1px solid {self.accent_color};
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
                min-height: 30px;
            }}
            QPushButton {{
                background-color: {self.primary_color};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: #2196F3;
            }}
            QPushButton:pressed {{
                background-color: #1976D2;
            }}
        """)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # 项目选择
        project_label = QLabel("Select Project:")
        layout.addWidget(project_label)

        project_combo = QComboBox()
        project_combo.setFixedHeight(35)  # 设置下拉框高度
        layout.addWidget(project_combo)

        # 任务描述
        desc_label = QLabel("Task Description:")
        layout.addWidget(desc_label)

        desc_input = QTextEdit()
        desc_input.setPlaceholderText("Enter your work description...")
        desc_input.setFixedHeight(100)  # 设置文本框高度
        desc_input.setStyleSheet(f"""
            QTextEdit {{
                background-color: rgba(255, 255, 255, 0.1);
                color: {self.text_color};
                border: 1px solid {self.accent_color};
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }}
        """)
        layout.addWidget(desc_input)

        # 显示实际用时
        actual_duration = (self.default_time - self.remaining_time) // 60
        if actual_duration == 0:
            actual_duration = self.default_time // 60

        duration_label = QLabel(f"Duration: {actual_duration} minutes")
        duration_label.setAlignment(Qt.AlignCenter)
        duration_label.setStyleSheet("""
            font-size: 14px;
            color: #4CAF50;
            margin: 10px 0;
        """)
        layout.addWidget(duration_label)

        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
            }
            QPushButton:hover {
                background-color: #E53935;
            }
            QPushButton:pressed {
                background-color: #D32F2F;
            }
        """)

        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        # 连接按钮信号
        save_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)
        alreadySetDefaultIndex = False
        # 显示对话框
        while True:
            self.update_project_items(project_combo)  # 在显示前再获取一下项目列表，确保项目被刷新进来了。
            if not alreadySetDefaultIndex and self.currentProjectIndex < project_combo.count():
                project_combo.setCurrentIndex(self.currentProjectIndex)
                alreadySetDefaultIndex = True
            if dialog.exec() == QDialog.Accepted:
                description = desc_input.toPlainText().strip()
                if not description:
                    self.show_message("Warning", "Please enter a task description!", QMessageBox.Warning)
                    continue
                else:
                    break
        project_id = project_combo.currentData()
        self.currentProjectIndex = project_combo.currentIndex()
        self.config.set("current_project_index", self.currentProjectIndex)

        if description and project_id is not None:
            if self.db.add_task(project_id, description, actual_duration):
                self.show_message(
                    "Success",
                    f"Task record saved!\nDuration: {actual_duration} minutes"
                )
            else:
                self.show_message(
                    "Error",
                    "Failed to save task record!",
                    QMessageBox.Warning
                )

    def closeEvent(self, event):
        """重写关闭事件"""
        event.ignore()
        self.hide()
        # 显示提示消息
        self.tray_icon.showMessage(
            "Pomodoro Timer",
            "Application minimized to system tray",
            QSystemTrayIcon.Information,
            2000
        )

    def set_timer_duration(self, minutes: int):
        """设置计时器时长"""
        if not self.timer.isActive():
            self.default_time = minutes * 60
            self.remaining_time = self.default_time
            self.time_label.setText(f"{minutes:02d}:00")
            self.tray_icon.setToolTip(f"Pomodoro Timer - {minutes:02d}:00")
            self.show_message("Timer Updated", f"Timer set to {minutes} minutes")

    def show_message(self, title: str, message: str, icon: QMessageBox.Icon = QMessageBox.Information):
        """显示统一风格的消息框"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(self.tr(title))
        msg_box.setText(self.tr(message))
        msg_box.setIcon(icon)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #212121;
                color: #FFFFFF;
                border: 2px solid #4CAF50;
                border-radius: 10px;
            }
            QLabel {
                color: #FFD700;
                font-size: 13px;
                font-weight: bold;
                min-width: 200px;
                max-width: 300px;
            }
            QPushButton {
                background-color: #1E88E5;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: bold;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: #2196F3;
            }
            QPushButton:pressed {
                background-color: #1976D2;
            }
        """)

        msg_box.setFixedSize(300, 150)
        return msg_box.exec_()

    def set_custom_timer_duration(self):
        """设置自定义计时器时长"""
        if self.timer.isActive():
            self.show_message("Warning", "Please stop the timer first!", QMessageBox.Warning)
            return

        # 创建自定义对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("Custom Timer")
        dialog.setFixedSize(300, 150)
        dialog.setStyleSheet(f"""
            QDialog {{
                background-color: {self.secondary_color};
                color: {self.text_color};
                border: 2px solid {self.accent_color};
                border-radius: 10px;
            }}
            QLabel {{
                color: {self.text_color};
                font-size: 12px;
            }}
            QSpinBox {{
                background-color: rgba(255, 255, 255, 0.1);
                color: {self.text_color};
                border: 1px solid {self.accent_color};
                border-radius: 4px;
                padding: 5px;
                font-size: 12px;
                min-width: 100px;
            }}
            QPushButton {{
                background-color: {self.primary_color};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #2196F3;
            }}
            QPushButton:pressed {{
                background-color: #1976D2;
            }}
        """)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # 时间输入
        time_label = QLabel("Enter time in minutes:")
        layout.addWidget(time_label)

        time_input = QSpinBox()
        time_input.setRange(1, 24 * 60 * 7)  # 最长一周
        time_input.setValue(25)
        time_input.setSingleStep(5)
        layout.addWidget(time_input)

        # 按钮布局
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
            }
            QPushButton:hover {
                background-color: #E53935;
            }
            QPushButton:pressed {
                background-color: #D32F2F;
            }
        """)

        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        save_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)

        if dialog.exec() == QDialog.Accepted:
            self.set_timer_duration(time_input.value())
            self.config.set("duration", time_input.value())

    def paintEvent(self, event):
        """重写绘制事件，绘制背景图"""
        painter = QPainter(self)

        # 绘制缩放后的背景图
        scaled_bg = self.background.scaled(self.size(), Qt.KeepAspectRatioByExpanding)

        # 计算居位置
        x = (self.width() - scaled_bg.width()) // 2
        y = (self.height() - scaled_bg.height()) // 2

        # 绘制背景图
        painter.drawPixmap(x, y, scaled_bg)

        # 绘制半透明遮罩
        painter.fillRect(self.rect(), self.overlay_color)

    def mousePressEvent(self, event):
        """记录鼠标按下时的位置"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """处理窗口拖动"""
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            self.move(event.globalPos() - self.drag_position)
            # 保存新窗口位置
            pos = self.pos()
            self.config.set("window_position", {"x": pos.x(), "y": pos.y()})
            event.accept()

    def mouseReleaseEvent(self, event):
        """处理鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            self.drag_position = None
            event.accept()

    def toggle_always_on_top(self, checked):
        """切换窗口置顶状态"""
        # 保持其他标志不变只修改置顶标志
        flags = self.windowFlags()
        if checked:
            flags |= Qt.WindowStaysOnTopHint
        else:
            flags &= ~Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.show()  # 需要重新显示窗口以应用更改
        self.config.set("always_on_top", checked)

    def set_opacity(self, opacity):
        """设置窗口透明度"""
        self.setWindowOpacity(opacity)
        self.config.set("opacity", opacity)

    def export_data(self):
        """将数据明细导出到Excel中"""
        # 创建一个Excel文件
        excelPath = f'data_export{datetime.now().strftime("%Y-%m-%d")}.xlsx'
        workbook = xlsxwriter.Workbook(excelPath)

        # 添加一个工作表
        worksheet = workbook.add_worksheet()
        bold = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'size': 16})
        # 设置列宽
        worksheet.set_column(0, 0, 10, bold)  # 任务id
        worksheet.set_column(1, 1, 30, bold)  # 项目名称
        worksheet.set_column(2, 2, 10, bold)  # 用时列
        worksheet.set_column(3, 3, 30, bold)  # 完成时间列
        worksheet.set_column(4, 4, 100, bold)  # 任务描述
        # 设置行高
        worksheet.set_row(0, 20)  # 标题行
        worksheet.set_row(1, 15)  # 数据行
        # 设置标题
        worksheet.write(0, 0, "任务ID")
        worksheet.write(0, 1, "项目名称")
        worksheet.write(0, 2, "用时")
        worksheet.write(0, 3, "完成时间")
        worksheet.write(0, 4, "任务描述")
        # 读取数据
        details = self.db.get_details()
        for rowIndex, row in enumerate(details):
            realRowIndex = rowIndex + 1
            for columnIndex in range(len(row)):
                worksheet.write(realRowIndex, columnIndex, row[columnIndex])
        workbook.close()
        sysHelper.openExcelFile(excelPath)

    def show_project_statistics(self):
        """显示项目统计信息"""
        stats = self.db.get_project_statistics()
        if not stats:
            self.show_message("Info", "No projects found.", QMessageBox.Information)
            return

        # 创建统计信息对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("Project Statistics")
        dialog.setMinimumSize(660, 300)
        dialog.setStyleSheet(f"""
            QDialog {{
                background-color: {self.secondary_color};
                color: {self.text_color};
                border: 2px solid {self.accent_color};
                border-radius: 10px;
            }}
            QLabel {{
                color: {self.text_color};
                font-size: 12px;
            }}
            QTableWidget {{
                background-color: rgba(255, 255, 255, 0.1);
                color: {self.text_color};
                border: 1px solid {self.accent_color};
                border-radius: 4px;
                gridline-color: {self.accent_color};
            }}
            QTableWidget::item {{
                padding: 5px;
            }}
            QHeaderView::section {{
                background-color: {self.primary_color};
                color: white;
                padding: 8px;
                border: none;
            }}
        """)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # 添加标题标签
        title_label = QLabel("Project Time Statistics")
        title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #4CAF50;
            margin-bottom: 10px;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # 创建表格
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels([
            "Project Name",
            "Total Tasks",
            "Total Time",
            "Average Time/Task"
        ])

        # 设置表格列宽
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # 项目名称列自适应
        header.setSectionResizeMode(1, QHeaderView.Fixed)  # 任务数固定宽度
        header.setSectionResizeMode(2, QHeaderView.Fixed)  # 总时间固定宽度
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # 平均时间固定宽度

        table.setColumnWidth(1, 100)  # 任务数列宽
        table.setColumnWidth(2, 120)  # 总时间列宽增加到 120
        table.setColumnWidth(3, 180)  # 平均时间列宽增加到 140

        # 填充数据
        table.setRowCount(len(stats))
        total_time = 0
        total_tasks = 0

        for row, (name, task_count, total_minutes) in enumerate(stats):
            total_time += total_minutes
            total_tasks += task_count

            # 项目名称
            table.setItem(row, 0, QTableWidgetItem(name))

            # 任务数量
            task_item = QTableWidgetItem(str(task_count))
            task_item.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 1, task_item)

            # 总时长
            hours = total_minutes // 60
            mins = total_minutes % 60
            if hours > 0:
                time_str = f"{hours}h {mins}m"
            else:
                time_str = f"{mins}m"
            time_item = QTableWidgetItem(time_str)
            time_item.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 2, time_item)

            # 平均时长
            if task_count > 0:
                avg_mins = total_minutes / task_count
                if avg_mins >= 60:
                    avg_str = f"{avg_mins / 60:.1f}h"
                else:
                    avg_str = f"{avg_mins:.1f}m"
            else:
                avg_str = "0m"
            avg_item = QTableWidgetItem(avg_str)
            avg_item.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 3, avg_item)

        layout.addWidget(table)

        # 添加总计信息
        total_hours = total_time // 60
        total_mins = total_time % 60
        total_info = (f"Total Statistics: {total_tasks} tasks, "
                      f"Total time: {total_hours}h {total_mins}m")
        if total_tasks > 0:
            avg_time = total_time / total_tasks
            if avg_time >= 60:
                avg_str = f"{avg_time / 60:.1f}h"
            else:
                avg_str = f"{avg_time:.1f}m"
            total_info += f", Average: {avg_str}/task"

        total_label = QLabel(total_info)
        total_label.setStyleSheet("""
            font-size: 12px;
            color: #4CAF50;
            margin-top: 10px;
        """)
        total_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(total_label)

        # 关闭按钮
        close_button = QPushButton("Close")
        close_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.primary_color};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: #2196F3;
            }}
            QPushButton:pressed {{
                background-color: #1976D2;
            }}
        """)
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button, alignment=Qt.AlignCenter)

        dialog.exec_()

    def show_about_dialog(self):
        """显示关于对话框"""
        dialog = QDialog(self)
        dialog.setWindowTitle("About Little Parrot Timer")
        dialog.setFixedSize(700, 668)  # 增加宽度从 600 到 700
        dialog.setStyleSheet(f"""
            QDialog {{
                background-color: {self.secondary_color};
                color: {self.text_color};
                border: 2px solid {self.accent_color};
                border-radius: 10px;
            }}
            QLabel {{
                color: {self.text_color};
                font-size: 13px;
                qproperty-alignment: AlignCenter;
            }}
        """)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(25)
        layout.setContentsMargins(30, 30, 30, 30)

        # 添加标题
        title_label = QLabel("Little Parrot Timer / 小虎皮鹦鹉计时器")
        title_label.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: #4CAF50;
            margin-bottom: 15px;
        """)
        layout.addWidget(title_label)

        # 添加纪念文字
        memorial_text = """
In Memory of Little budgerigar
纪念小虎皮鹦鹉

December 21, 2024
2024年12月21日

This timer application is dedicated to my beloved pet parrot,
who brought joy, companionship and countless happy moments to my life.
Though your time with us was brief, your impact was profound.

这个计时应用程序献给我挚爱的宠物鹦鹉，
是你为我的生活带来了欢乐、陪伴和无数美好时光。
虽然与你相处的时光短暂，但你留下的印记永远深刻。

May your spirit soar freely in the endless sky,
Your cheerful chirps will forever echo in my heart.
愿你的灵魂在无垠的天际自由翱翔，
你欢快的啁啾声将永远在我的心中回响。

Rest in Peace, Little Friend
安息吧，我的小伙伴
        """

        memorial_label = QLabel(memorial_text)
        memorial_label.setStyleSheet("""
            color: #FFD700;
            font-size: 15px;
            line-height: 160%;
        """)
        memorial_label.setWordWrap(True)
        layout.addWidget(memorial_label)

        # 添加版本信息
        version_text = """
Version 1.0.0 / 版本 1.0.0
Created with love and memory / 用爱与回忆创造
        """
        version_label = QLabel(version_text)
        version_label.setStyleSheet("""
            color: #90CAF9;
            font-size: 13px;
            margin-top: 15px;
        """)
        layout.addWidget(version_label)

        # 关闭按钮
        close_button = QPushButton("Close / 关闭")
        close_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.primary_color};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-size: 13px;
                font-weight: bold;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background-color: #2196F3;
            }}
            QPushButton:pressed {{
                background-color: #1976D2;
            }}
        """)
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button, alignment=Qt.AlignCenter)

        dialog.exec_()

    def change_language(self, lang: str):
        """切换语言"""
        self.current_lang = lang
        self.config.set("language", lang)

        # 更新语言选项的选中状态
        menu = self.tray_icon.contextMenu()
        settings_menu = menu.findChild(QMenu, "settings_menu")
        if settings_menu:
            lang_menu = settings_menu.findChild(QMenu, "language_menu")
            if lang_menu:
                for action in lang_menu.actions():
                    action.setChecked(action.data() == lang)

        # 更新所有UI文本
        self.update_ui_texts()

    def update_ui_texts(self):
        """更新所有UI文本"""
        # 更新窗口标题
        self.setWindowTitle(self.tr("pomodoro_timer"))

        # 更新按钮文本
        if self.timer.isActive():
            self.start_button.setText(self.tr("stop"))
        else:
            self.start_button.setText(self.tr("start"))
        self.reset_button.setText(self.tr("reset"))

        # 更新托盘菜单文本
        self.update_tray_menu_texts()

        # 更新托盘图标提示
        minutes = self.remaining_time // 60
        seconds = self.remaining_time % 60
        self.tray_icon.setToolTip(f"{self.tr('pomodoro_timer')} - {minutes:02d}:{seconds:02d}")

    def tr(self, key: str, *args) -> str:
        """翻译辅助方法"""
        return self.lang_manager.get(key, self.current_lang, *args)

    def update_tray_menu_texts(self):
        """更新托盘菜单的文本"""
        menu = self.tray_icon.contextMenu()

        # 更新主菜单项
        actions = menu.actions()
        actions[0].setText(self.tr("show_hide"))
        self.tray_timer_action.setText(self.tr("start") if not self.timer.isActive() else self.tr("stop"))
        actions[2].setText(self.tr("reset"))

        # 更新时间设置菜单
        for action in actions:
            if isinstance(action, QMenu) and action.objectName() == "time_menu":
                action.setTitle(self.tr("set_timer"))
                for sub_action in action.actions()[:-1]:  # 除了最后一个自定义选项
                    try:
                        minutes = int(''.join(filter(str.isdigit, sub_action.text())))
                        sub_action.setText(f"{minutes} {self.tr('minutes')}")
                    except ValueError:
                        continue
                action.actions()[-1].setText(self.tr("custom"))
            elif isinstance(action, QMenu) and action.objectName() == "settings_menu":
                action.setTitle(self.tr("settings"))
                # 更新设置菜单的子项
                for sub_item in action.actions():
                    if isinstance(sub_item, QAction):
                        if sub_item.objectName() == "add_project_action":
                            sub_item.setText(self.tr("add_project"))
                        elif sub_item.objectName() == "always_on_top_action":
                            sub_item.setText(self.tr("always_on_top"))
                        elif sub_item.objectName() == "stats_action":
                            sub_item.setText(self.tr("project_statistics"))
                    elif isinstance(sub_item, QMenu):
                        if sub_item.objectName() == "opacity_menu":
                            sub_item.setTitle(self.tr("opacity"))
                        elif sub_item.objectName() == "language_menu":
                            sub_item.setTitle(self.tr("language"))

        # 更新项目统计、关于和退出选项
        actions[-4].setText(self.tr("project_statistics"))  # 项目统计
        actions[-3].setText(self.tr("about"))  # 关于
        actions[-1].setText(self.tr("quit"))  # 退出
