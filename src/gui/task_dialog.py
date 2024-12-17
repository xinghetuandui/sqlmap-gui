from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget,
                           QTableWidgetItem, QPushButton, QLabel, QMessageBox,
                           QMenu, QTabWidget, QWidget, QProgressBar)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor
from src.core.task_manager import TaskManager, TaskStatus
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from datetime import datetime

class TaskDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("任务管理")
        self.resize(1000, 600)
        self.task_manager = TaskManager()
        self.setup_ui()
        self.load_tasks()
        
        # 定时刷新
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_tasks)
        self.timer.start(5000)  # 每5秒刷新一次
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 创建选项卡
        tab_widget = QTabWidget()
        
        # 任务列表选项卡
        task_tab = QWidget()
        task_layout = QVBoxLayout(task_tab)
        
        # 任务表格
        self.task_table = QTableWidget()
        self.task_table.setColumnCount(7)
        self.task_table.setHorizontalHeaderLabels([
            "ID", "名称", "目标", "状态", "创建时间", "开始时间", "完成时间"
        ])
        self.task_table.setContextMenuPolicy(Qt.CustomContextMenu)
        task_layout.addWidget(self.task_table)
        
        # 按钮
        button_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("刷新")
        self.delete_btn = QPushButton("删除")
        self.export_btn = QPushButton("导出结果")
        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(self.export_btn)
        task_layout.addLayout(button_layout)
        
        tab_widget.addTab(task_tab, "任务列表")
        
        # 统计信息选项卡
        stats_tab = QWidget()
        stats_layout = QVBoxLayout(stats_tab)
        
        # 添加图表
        self.figure, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(10, 5))
        self.canvas = FigureCanvasQTAgg(self.figure)
        stats_layout.addWidget(self.canvas)
        
        # 添加统计信息标签
        self.stats_label = QLabel()
        stats_layout.addWidget(self.stats_label)
        
        tab_widget.addTab(stats_tab, "统计信息")
        
        layout.addWidget(tab_widget)
        self.setLayout(layout)
        
        # 连接信号
        self.task_table.customContextMenuRequested.connect(self.show_context_menu)
        self.refresh_btn.clicked.connect(self.refresh_tasks)
        self.delete_btn.clicked.connect(self.delete_selected_task)
        self.export_btn.clicked.connect(self.export_selected_result)
        
    def load_tasks(self):
        """加载所有任务"""
        tasks = self.task_manager.get_all_tasks()
        self.task_table.setRowCount(len(tasks))
        
        for i, task in enumerate(tasks):
            self.task_table.setItem(i, 0, QTableWidgetItem(str(task.id)))
            self.task_table.setItem(i, 1, QTableWidgetItem(task.name))
            self.task_table.setItem(i, 2, QTableWidgetItem(task.target_config.get('url', '')))
            self.task_table.setItem(i, 3, QTableWidgetItem(task.status.value))
            self.task_table.setItem(i, 4, QTableWidgetItem(task.create_time.strftime("%Y-%m-%d %H:%M:%S")))
            self.task_table.setItem(i, 5, QTableWidgetItem(
                task.start_time.strftime("%Y-%m-%d %H:%M:%S") if task.start_time else ""
            ))
            self.task_table.setItem(i, 6, QTableWidgetItem(
                task.end_time.strftime("%Y-%m-%d %H:%M:%S") if task.end_time else ""
            ))
            
            # 设置状态颜色
            status_item = self.task_table.item(i, 3)
            if task.status == TaskStatus.COMPLETED:
                status_item.setBackground(QColor(200, 255, 200))
            elif task.status == TaskStatus.FAILED:
                status_item.setBackground(QColor(255, 200, 200))
            elif task.status == TaskStatus.RUNNING:
                status_item.setBackground(QColor(200, 200, 255))
                
        self.task_table.resizeColumnsToContents()
        
        # 更新统计信息
        self.update_statistics()
        
    def update_statistics(self):
        """更新统计信息"""
        stats = self.task_manager.get_task_statistics()
        
        # 清除旧图表
        self.ax1.clear()
        self.ax2.clear()
        
        # 绘制状态统计饼图
        status_labels = []
        status_values = []
        for status in TaskStatus:
            count = stats['status_stats'].get(status.value, 0)
            if count > 0:
                status_labels.append(status.value)
                status_values.append(count)
                
        self.ax1.pie(status_values, labels=status_labels, autopct='%1.1f%%')
        self.ax1.set_title("任��状态分布")
        
        # 绘制漏洞统计柱状图
        vuln_data = [
            stats['vulnerable_targets'],
            stats['database_types']
        ]
        self.ax2.bar(['发现漏洞的目标', '数据库类型数'], vuln_data)
        self.ax2.set_title("漏洞统计")
        
        self.canvas.draw()
        
        # 更新统计信息标签
        self.stats_label.setText(f"""
            统计信息：
            - 总任务数：{sum(stats['status_stats'].values())}
            - 发现漏洞的目标：{stats['vulnerable_targets']}
            - 数据库类型数：{stats['database_types']}
        """)
        
    def show_context_menu(self, pos):
        """显示右键菜单"""
        menu = QMenu()
        view_action = menu.addAction("查看详情")
        stop_action = menu.addAction("停止")
        delete_action = menu.addAction("删除")
        
        action = menu.exec_(self.task_table.mapToGlobal(pos))
        if not action:
            return
            
        row = self.task_table.currentRow()
        task_id = int(self.task_table.item(row, 0).text())
        
        if action == view_action:
            self.view_task_details(task_id)
        elif action == stop_action:
            self.stop_task(task_id)
        elif action == delete_action:
            self.delete_task(task_id)
            
    def view_task_details(self, task_id):
        """查看任务详情"""
        task = self.task_manager.get_task(task_id)
        if not task:
            return
            
        from src.gui.result_dialog import ResultDialog
        dialog = ResultDialog(task.result, self)
        dialog.exec_()
        
    def stop_task(self, task_id):
        """停止任务"""
        task = self.task_manager.get_task(task_id)
        if task and task.status == TaskStatus.RUNNING:
            self.task_manager.update_task_status(task_id, TaskStatus.STOPPED)
            self.refresh_tasks()
            
    def delete_task(self, task_id):
        """删除任务"""
        reply = QMessageBox.question(
            self, "确认删除",
            "确定要删除该任务吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.task_manager.delete_task(task_id)
            self.refresh_tasks()
            
    def refresh_tasks(self):
        """刷新任务列表"""
        self.load_tasks()
        
    def delete_selected_task(self):
        """删除选中的任务"""
        rows = set(item.row() for item in self.task_table.selectedItems())
        if not rows:
            return
            
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除选中的 {len(rows)} 个任务吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            for row in rows:
                task_id = int(self.task_table.item(row, 0).text())
                self.task_manager.delete_task(task_id)
            self.refresh_tasks()
            
    def export_selected_result(self):
        """导出选中任务的结果"""
        rows = set(item.row() for item in self.task_table.selectedItems())
        if not rows:
            return
            
        for row in rows:
            task_id = int(self.task_table.item(row, 0).text())
            task = self.task_manager.get_task(task_id)
            if task and task.result:
                from src.gui.result_dialog import ResultDialog
                dialog = ResultDialog(task.result, self)
                dialog.export_json() 