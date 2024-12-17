import sqlite3
import json
import time
from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

class TaskStatus(Enum):
    PENDING = "等待中"
    RUNNING = "运行中"
    COMPLETED = "已完成"
    FAILED = "失败"
    STOPPED = "已停止"

@dataclass
class ScanTask:
    id: int
    name: str
    target_config: Dict
    scan_options: Dict
    status: TaskStatus
    create_time: datetime
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    result: Optional[Dict] = None
    error: Optional[str] = None

class TaskManager:
    def __init__(self, db_path: str = "sqlmap_gui.db"):
        self.db_path = db_path
        self.init_db()
        
    def init_db(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS scan_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    target_config TEXT NOT NULL,
                    scan_options TEXT,
                    status TEXT NOT NULL,
                    create_time TIMESTAMP NOT NULL,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    result TEXT,
                    error TEXT
                )
            """)
            
    def create_task(self, name: str, target_config: Dict, scan_options: Dict = None) -> ScanTask:
        """创建新的扫描任务"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            now = datetime.now()
            cursor.execute("""
                INSERT INTO scan_tasks (name, target_config, scan_options, status, create_time)
                VALUES (?, ?, ?, ?, ?)
            """, (
                name,
                json.dumps(target_config),
                json.dumps(scan_options) if scan_options else None,
                TaskStatus.PENDING.value,
                now
            ))
            task_id = cursor.lastrowid
            
        return ScanTask(
            id=task_id,
            name=name,
            target_config=target_config,
            scan_options=scan_options or {},
            status=TaskStatus.PENDING,
            create_time=now
        )
        
    def get_task(self, task_id: int) -> Optional[ScanTask]:
        """获取任务信息"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scan_tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            
        if not row:
            return None
            
        return ScanTask(
            id=row[0],
            name=row[1],
            target_config=json.loads(row[2]),
            scan_options=json.loads(row[3]) if row[3] else {},
            status=TaskStatus(row[4]),
            create_time=datetime.fromisoformat(row[5]),
            start_time=datetime.fromisoformat(row[6]) if row[6] else None,
            end_time=datetime.fromisoformat(row[7]) if row[7] else None,
            result=json.loads(row[8]) if row[8] else None,
            error=row[9]
        )
        
    def get_all_tasks(self) -> List[ScanTask]:
        """获取所有任务"""
        tasks = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scan_tasks ORDER BY create_time DESC")
            for row in cursor.fetchall():
                tasks.append(ScanTask(
                    id=row[0],
                    name=row[1],
                    target_config=json.loads(row[2]),
                    scan_options=json.loads(row[3]) if row[3] else {},
                    status=TaskStatus(row[4]),
                    create_time=datetime.fromisoformat(row[5]),
                    start_time=datetime.fromisoformat(row[6]) if row[6] else None,
                    end_time=datetime.fromisoformat(row[7]) if row[7] else None,
                    result=json.loads(row[8]) if row[8] else None,
                    error=row[9]
                ))
        return tasks
        
    def update_task_status(self, task_id: int, status: TaskStatus,
                          result: Dict = None, error: str = None):
        """更新任务状态"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            updates = ["status = ?"]
            params = [status.value]
            
            if status == TaskStatus.RUNNING:
                updates.append("start_time = ?")
                params.append(datetime.now().isoformat())
            elif status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.STOPPED):
                updates.append("end_time = ?")
                params.append(datetime.now().isoformat())
                
            if result is not None:
                updates.append("result = ?")
                params.append(json.dumps(result))
                
            if error is not None:
                updates.append("error = ?")
                params.append(error)
                
            params.append(task_id)
            
            cursor.execute(f"""
                UPDATE scan_tasks
                SET {', '.join(updates)}
                WHERE id = ?
            """, params)
            
    def delete_task(self, task_id: int):
        """删除任务"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM scan_tasks WHERE id = ?", (task_id,))
            
    def get_task_statistics(self) -> Dict:
        """获取任务统计信息"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT status, COUNT(*) 
                FROM scan_tasks 
                GROUP BY status
            """)
            status_stats = dict(cursor.fetchall())
            
            cursor.execute("""
                SELECT COUNT(DISTINCT json_extract(result, '$.database.type'))
                FROM scan_tasks 
                WHERE result IS NOT NULL
            """)
            db_types = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) 
                FROM scan_tasks 
                WHERE json_extract(result, '$.injection_points') IS NOT NULL
            """)
            vuln_count = cursor.fetchone()[0]
            
        return {
            'status_stats': status_stats,
            'database_types': db_types,
            'vulnerable_targets': vuln_count
        } 