import sqlite3
from datetime import datetime
from typing import List, Optional, Tuple

class DatabaseManager:
    def __init__(self, db_name: str = "pomodoro.db"):
        self.db_name = db_name
        self.init_database()

    def init_database(self) -> None:
        """初始化数据库表"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            # 创建项目表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
            """)
            
            # 创建任务记录表，添加 duration_minutes 字段
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER,
                    description TEXT NOT NULL,
                    duration_minutes INTEGER NOT NULL,  -- 任务时长（分钟）
                    completed_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (project_id) REFERENCES projects (id)
                )
            """)
            conn.commit()

    def add_project(self, name: str) -> bool:
        """添加新项目"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO projects (name) VALUES (?)", (name,))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False

    def get_projects(self) -> List[Tuple[int, str]]:
        """获取所有项目"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM projects")
            return cursor.fetchall()

    def add_task(self, project_id: int, description: str, duration_minutes: int) -> bool:
        """
        添加任务记录
        
        Args:
            project_id: 项目ID
            description: 任务描述
            duration_minutes: 任务时长（分钟）
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO tasks (project_id, description, duration_minutes, completed_at) 
                    VALUES (?, ?, ?, ?)
                    """,
                    (project_id, description, duration_minutes, datetime.now())
                )
                conn.commit()
                return True
        except sqlite3.Error:
            return False

    def get_task_statistics(self, project_id: Optional[int] = None) -> List[Tuple]:
        """
        获取任务统计信息
        
        Args:
            project_id: 可选的项目ID过滤
            
        Returns:
            List of (project_name, total_tasks, total_duration_minutes)
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            query = """
                SELECT 
                    p.name,
                    COUNT(t.id) as total_tasks,
                    SUM(t.duration_minutes) as total_duration
                FROM projects p
                LEFT JOIN tasks t ON p.id = t.project_id
            """
            
            if project_id is not None:
                query += " WHERE p.id = ?"
                cursor.execute(query + " GROUP BY p.id", (project_id,))
            else:
                cursor.execute(query + " GROUP BY p.id")
                
            return cursor.fetchall() 

    def get_project_statistics(self) -> List[Tuple[str, int, int]]:
        """
        获取所有项目的统计信息
        
        Returns:
            List of (project_name, total_tasks, total_minutes)
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    p.name,
                    COUNT(t.id) as task_count,
                    COALESCE(SUM(t.duration_minutes), 0) as total_minutes
                FROM projects p
                LEFT JOIN tasks t ON p.id = t.project_id
                GROUP BY p.id, p.name
                ORDER BY total_minutes DESC
            """)
            return cursor.fetchall() 