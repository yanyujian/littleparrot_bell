from typing import Dict

class LanguageManager:
    def __init__(self):
        self.translations = {
            "en": {
                # 主窗口
                "start": "Start",
                "stop": "Stop",
                "reset": "Reset",
                
                # 系统托盘菜单
                "show_hide": "Show/Hide",
                "set_timer": "Set Timer",
                "custom": "Custom...",
                "minutes": "minutes",
                "settings": "Settings",
                "add_project": "Add Project",
                "always_on_top": "Always on Top",
                "opacity": "Opacity",
                "project_statistics": "Project Statistics",
                "about": "About",
                "quit": "Quit",
                
                # 项目相关
                "project_name": "Project Name:",
                "enter_project_name": "Enter project name...",
                "project_added": "Project added successfully!",
                "project_add_failed": "Failed to add project. It may already exist.",
                "no_projects": "Please add a project first!",
                
                # 任务相关
                "complete_task": "Complete Task",
                "select_project": "Select Project:",
                "task_description": "Task Description:",
                "enter_task_desc": "Enter your work description...",
                "duration": "Duration: {} minutes",
                "task_saved": "Task record saved!\nDuration: {} minutes",
                "task_save_failed": "Failed to save task record!",
                
                # 统计信息
                "project_time_stats": "Project Time Statistics",
                "project_name_col": "Project Name",
                "total_tasks_col": "Total Tasks",
                "total_time_col": "Total Time",
                "avg_time_col": "Average Time/Task",
                "total_stats": "Total Statistics: {} tasks, Total time: {}h {}m",
                "avg_per_task": "Average: {}/task",
                
                # 按钮
                "save": "Save",
                "cancel": "Cancel",
                "close": "Close",
                
                # 消息
                "timer_updated": "Timer Updated",
                "timer_set": "Timer set to {} minutes",
                "times_up": "Time's up! Please record your work.",
                "app_minimized": "Application minimized to system tray",
                
                # 自定义时间
                "custom_timer": "Custom Timer",
                "enter_minutes": "Enter time in minutes:",
                "stop_timer_first": "Please stop the timer first!",
                
                # 窗口标题
                "pomodoro_timer": "Pomodoro Timer",
                
                # 语言菜单
                "language": "Language",
                "language_name": "English",
            },
            "zh": {
                # 主窗口
                "start": "开始",
                "stop": "停止",
                "reset": "重置",
                
                # 系统托盘菜单
                "show_hide": "显示/隐藏",
                "set_timer": "设置时间",
                "custom": "自定义...",
                "minutes": "分钟",
                "settings": "设置",
                "add_project": "添加项目",
                "always_on_top": "窗口置顶",
                "opacity": "透明度",
                "project_statistics": "项目统计",
                "about": "关于",
                "quit": "退出",
                
                # 项目相关
                "project_name": "项目名称：",
                "enter_project_name": "请输入项目名称...",
                "project_added": "项目添加成功！",
                "project_add_failed": "项目添加失败，可能已存在。",
                "no_projects": "请先添加一个项目！",
                
                # 任务相关
                "complete_task": "完成任务",
                "select_project": "选择项目：",
                "task_description": "任务描述：",
                "enter_task_desc": "请输入工作描述...",
                "duration": "用时：{} 分钟",
                "task_saved": "任务记录已保存！\n用时：{} 分钟",
                "task_save_failed": "任务记录保存失败！",
                
                # 统计信息
                "project_time_stats": "项目时间统计",
                "project_name_col": "项目名称",
                "total_tasks_col": "总任务数",
                "total_time_col": "总时长",
                "avg_time_col": "平均时长",
                "total_stats": "总计：{}个任务，总时长：{}小时{}分钟",
                "avg_per_task": "平均每任务：{}",
                
                # 按钮
                "save": "保存",
                "cancel": "取消",
                "close": "关闭",
                
                # 消息
                "timer_updated": "计时器已更新",
                "timer_set": "计时器已设置为 {} 分钟",
                "times_up": "时间到！请记录您的工作。",
                "app_minimized": "应用程序已最小化到系统托盘",
                
                # 自定义时间
                "custom_timer": "自定义时间",
                "enter_minutes": "请输入时间（分钟）：",
                "stop_timer_first": "请先停止计时器！",
                
                # 窗口标题
                "pomodoro_timer": "番茄钟计时器",
                
                # 语言菜单
                "language": "语言",
                "language_name": "中文",
            }
        }
        
    def get(self, key: str, lang: str, *args) -> str:
        """获取翻译文本"""
        text = self.translations.get(lang, self.translations["en"]).get(key, key)
        if args:
            return text.format(*args)
        return text 