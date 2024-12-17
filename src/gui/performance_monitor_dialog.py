from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                           QPushButton, QLabel, QTableWidget, QTableWidgetItem,
                           QHeaderView, QWidget, QGroupBox, QFileDialog, QMessageBox)
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis, QDateTimeAxis
from PyQt5.QtCore import Qt, QTimer, QPointF, QDateTime
from PyQt5.QtGui import QPainter
import time
import csv
import json

class PerformanceMonitorDialog(QDialog):
    def __init__(self, performance_manager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("性能监控")
        self.resize(1000, 600)
        self.performance_manager = performance_manager
        
        # 初始化数据点列表
        self.cpu_points = []
        self.memory_points = []
        self.start_time = QDateTime.currentDateTime()
        
        # 创建实时更新定时器
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(1000)  # 每秒更新一次
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 创建选项卡
        tab_widget = QTabWidget()
        
        # 实时监控选项卡
        realtime_tab = self._create_realtime_tab()
        tab_widget.addTab(realtime_tab, "实时监控")
        
        # 历史数据选项卡
        history_tab = self._create_history_tab()
        tab_widget.addTab(history_tab, "历史数据")
        
        # 性能分析选项卡
        analysis_tab = self._create_analysis_tab()
        tab_widget.addTab(analysis_tab, "性能分析")
        
        layout.addWidget(tab_widget)
        
        # 按钮
        button_layout = QHBoxLayout()
        self.optimize_btn = QPushButton("优化性能")
        self.export_btn = QPushButton("导出数据")
        self.close_btn = QPushButton("关闭")
        
        button_layout.addWidget(self.optimize_btn)
        button_layout.addWidget(self.export_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 连接信号
        self.optimize_btn.clicked.connect(self.optimize_performance)
        self.export_btn.clicked.connect(self.export_data)
        self.close_btn.clicked.connect(self.close)
        
    def _create_realtime_tab(self) -> QWidget:
        """创建实时监控选项卡"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # CPU使用率图表
        self.cpu_chart = self._create_chart("CPU使用率", "时间", "使用率(%)")
        cpu_view = QChartView(self.cpu_chart)
        cpu_view.setRenderHint(QPainter.Antialiasing)  # 抗锯齿
        layout.addWidget(cpu_view)
        
        # 内存使用图表
        self.memory_chart = self._create_chart("内存使用", "时间", "使用量(MB)")
        memory_view = QChartView(self.memory_chart)
        memory_view.setRenderHint(QPainter.Antialiasing)  # 抗锯齿
        layout.addWidget(memory_view)
        
        # 实时数据表格
        self.realtime_table = QTableWidget()
        self.realtime_table.setColumnCount(4)
        self.realtime_table.setHorizontalHeaderLabels([
            "指标", "当前值", "平均值", "最大值"
        ])
        header = self.realtime_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.realtime_table)
        
        widget.setLayout(layout)
        return widget
        
    def _create_history_tab(self) -> QWidget:
        """创建历史数据选项卡"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 历史数据表格
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels([
            "时间", "CPU使用率(%)", "内存使用(MB)", 
            "响应时间(ms)", "线程数", "队列大小"
        ])
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        
        # 添加导出按钮
        export_btn = QPushButton("导出历史数据")
        export_btn.clicked.connect(self._export_history)
        
        layout.addWidget(self.history_table)
        layout.addWidget(export_btn)
        
        widget.setLayout(layout)
        return widget
        
    def _create_analysis_tab(self) -> QWidget:
        """创建性能分析选项卡"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 性能分析文本
        analysis_group = QGroupBox("性能分析")
        analysis_layout = QVBoxLayout()
        self.analysis_text = QLabel()
        self.analysis_text.setWordWrap(True)
        self.analysis_text.setStyleSheet("QLabel { background-color: #f0f0f0; padding: 10px; }")
        analysis_layout.addWidget(self.analysis_text)
        analysis_group.setLayout(analysis_layout)
        
        # 性能建议
        suggestion_group = QGroupBox("优化建议")
        suggestion_layout = QVBoxLayout()
        self.suggestion_text = QLabel()
        self.suggestion_text.setWordWrap(True)
        self.suggestion_text.setStyleSheet("QLabel { background-color: #f0f0f0; padding: 10px; }")
        suggestion_layout.addWidget(self.suggestion_text)
        suggestion_group.setLayout(suggestion_layout)
        
        # 性能评分
        score_group = QGroupBox("性能评分")
        score_layout = QVBoxLayout()
        self.score_label = QLabel()
        self.score_label.setAlignment(Qt.AlignCenter)
        self.score_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
        """)
        score_layout.addWidget(self.score_label)
        score_group.setLayout(score_layout)
        
        layout.addWidget(analysis_group)
        layout.addWidget(suggestion_group)
        layout.addWidget(score_group)
        
        widget.setLayout(layout)
        return widget
        
    def _create_chart(self, title: str, x_label: str, y_label: str) -> QChart:
        """创建图表"""
        chart = QChart()
        chart.setTitle(title)
        chart.setAnimationOptions(QChart.NoAnimation)  # 禁用动画以提高性能
        
        # 创建数据系列
        series = QLineSeries()
        chart.addSeries(series)
        
        # 创建X轴（时间轴）
        axis_x = QDateTimeAxis()
        axis_x.setTitleText(x_label)
        axis_x.setFormat("mm:ss")
        axis_x.setTickCount(6)
        axis_x.setRange(self.start_time, self.start_time.addSecs(60))
        
        # 创建Y轴
        axis_y = QValueAxis()
        axis_y.setTitleText(y_label)
        axis_y.setRange(0, 100)
        
        chart.addAxis(axis_x, Qt.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignLeft)
        
        series.attachAxis(axis_x)
        series.attachAxis(axis_y)
        
        return chart
        
    def update_display(self):
        """更新显示"""
        # 获取最新性能数据
        metrics = self.performance_manager.get_metrics_summary()
        
        # 更新实时图表
        self._update_charts(metrics)
        
        # 更新实时数据表格
        self._update_realtime_table(metrics)
        
        # 更新历史数据表格
        self._update_history_table()
        
        # 更新性能分析
        self._update_analysis(metrics)
        
    def _update_charts(self, metrics: dict):
        """更新图表"""
        current_time = QDateTime.currentDateTime()
        
        # 更新CPU图表
        cpu_series = self.cpu_chart.series()[0]
        self.cpu_points.append(QPointF(current_time.toMSecsSinceEpoch(), 
                                     metrics['cpu']['current']))
        
        # 保持最近60秒的数据
        while len(self.cpu_points) > 60:
            self.cpu_points.pop(0)
            
        cpu_series.clear()
        cpu_series.append(self.cpu_points)
        
        # 更新时间轴范围
        axis_x = self.cpu_chart.axes(Qt.Horizontal)[0]
        axis_x.setRange(current_time.addSecs(-60), current_time)
        
        # 更新内存图表
        memory_series = self.memory_chart.series()[0]
        self.memory_points.append(QPointF(current_time.toMSecsSinceEpoch(), 
                                        metrics['memory']['current']))
        
        while len(self.memory_points) > 60:
            self.memory_points.pop(0)
            
        memory_series.clear()
        memory_series.append(self.memory_points)
        
        # 更新内存图表的时间轴范围
        axis_x = self.memory_chart.axes(Qt.Horizontal)[0]
        axis_x.setRange(current_time.addSecs(-60), current_time)
        
        # 更新内存图表的Y轴范围
        max_memory = max(point.y() for point in self.memory_points)
        axis_y = self.memory_chart.axes(Qt.Vertical)[0]
        axis_y.setRange(0, max(1024, max_memory * 1.2))  # 留出20%的余量
        
    def _update_realtime_table(self, metrics: dict):
        """更新实时数据表格"""
        self.realtime_table.setRowCount(5)
        
        # CPU
        self._set_table_row(0, "CPU使用率", 
                          metrics['cpu']['current'],
                          metrics['cpu']['avg'],
                          metrics['cpu']['max'])
                          
        # 内存
        self._set_table_row(1, "内存使用", 
                          metrics['memory']['current'],
                          metrics['memory']['avg'],
                          metrics['memory']['max'])
                          
        # 响应时间
        self._set_table_row(2, "响应时间", 
                          metrics['response_time']['current'],
                          metrics['response_time']['avg'],
                          metrics['response_time']['max'])
                          
        # 线程数
        self._set_table_row(3, "线程数", 
                          metrics['threads']['current'],
                          None,
                          metrics['threads']['max'])
                          
        # 队列大小
        self._set_table_row(4, "队列大小", 
                          metrics['queue']['current'],
                          None,
                          metrics['queue']['max'])
                          
    def _set_table_row(self, row: int, name: str, current: float, 
                      avg: float = None, max_val: float = None):
        """设置表格行数据"""
        self.realtime_table.setItem(row, 0, QTableWidgetItem(name))
        self.realtime_table.setItem(row, 1, 
                                  QTableWidgetItem(f"{current:.1f}"))
        if avg is not None:
            self.realtime_table.setItem(row, 2, 
                                      QTableWidgetItem(f"{avg:.1f}"))
        if max_val is not None:
            self.realtime_table.setItem(row, 3, 
                                      QTableWidgetItem(f"{max_val:.1f}"))
                                      
    def _update_history_table(self):
        """更新历史数据表格"""
        history = self.performance_manager.metrics_history
        self.history_table.setRowCount(len(history))
        
        for i, metrics in enumerate(history):
            self.history_table.setItem(i, 0, 
                QTableWidgetItem(time.strftime("%H:%M:%S", 
                    time.localtime(metrics.timestamp))))
            self.history_table.setItem(i, 1, 
                QTableWidgetItem(f"{metrics.cpu_usage:.1f}"))
            self.history_table.setItem(i, 2, 
                QTableWidgetItem(f"{metrics.memory_usage:.1f}"))
            self.history_table.setItem(i, 3, 
                QTableWidgetItem(f"{metrics.response_time:.1f}"))
            self.history_table.setItem(i, 4, 
                QTableWidgetItem(str(metrics.thread_count)))
            self.history_table.setItem(i, 5, 
                QTableWidgetItem(str(metrics.queue_size)))
                
    def _update_analysis(self, metrics: dict):
        """更新性能分析"""
        analysis = []
        suggestions = []
        
        # CPU分析
        if metrics['cpu']['current'] > 80:
            analysis.append("CPU使用率过高")
            suggestions.append("建议减少并发任务数")
        elif metrics['cpu']['current'] < 20:
            analysis.append("CPU使用率较低")
            suggestions.append("可��适当增加并发任务数")
            
        # 内存分析
        if metrics['memory']['current'] > 1024:
            analysis.append("内存使用量过大")
            suggestions.append("建议清理缓存或减少批处理大小")
            
        # 响应时间分析
        if metrics['response_time']['current'] > 5000:
            analysis.append("响应时间过长")
            suggestions.append("建议检查网络连接或减少请求频率")
            
        # 更新显示
        self.analysis_text.setText("性能分析:\n" + "\n".join(analysis))
        self.suggestion_text.setText("优化建议:\n" + "\n".join(suggestions))
        
    def optimize_performance(self):
        """优化性能"""
        self.performance_manager.optimize_performance()
        
    def export_data(self):
        """导出性能数据"""
        # TODO: 实现数据导出功能
        pass
        
    def closeEvent(self, event):
        """关闭事件"""
        self.update_timer.stop()
        event.accept() 
        
    def _export_history(self):
        """导出历史数据"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "导出历史数据", "", 
            "CSV文件 (*.csv);;JSON文件 (*.json)"
        )
        if not filename:
            return
        
        try:
            if filename.endswith('.csv'):
                self._export_to_csv(filename)
            elif filename.endswith('.json'):
                self._export_to_json(filename)
            
            QMessageBox.information(self, "成功", "数据导出成功")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"导出失败: {str(e)}")

    def _export_to_csv(self, filename: str):
        """导出为CSV文件"""
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # 写入表头
            writer.writerow([
                "时间", "CPU使用率(%)", "内存使用(MB)", 
                "响应时间(ms)", "线程数", "队列大小"
            ])
            # 写入数据
            for metrics in self.performance_manager.metrics_history:
                writer.writerow([
                    time.strftime("%Y-%m-%d %H:%M:%S", 
                                time.localtime(metrics.timestamp)),
                    f"{metrics.cpu_usage:.1f}",
                    f"{metrics.memory_usage:.1f}",
                    f"{metrics.response_time:.1f}",
                    metrics.thread_count,
                    metrics.queue_size
                ])

    def _export_to_json(self, filename: str):
        """导出为JSON文件"""
        data = []
        for metrics in self.performance_manager.metrics_history:
            data.append({
                'timestamp': metrics.timestamp,
                'cpu_usage': metrics.cpu_usage,
                'memory_usage': metrics.memory_usage,
                'response_time': metrics.response_time,
                'thread_count': metrics.thread_count,
                'queue_size': metrics.queue_size
            })
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def _update_score(self, metrics: dict):
        """更新性能评分"""
        # 计算性能评分 (0-100)
        cpu_score = max(0, 100 - metrics['cpu']['current'])
        memory_score = max(0, 100 - (metrics['memory']['current'] / 10.24))
        response_score = max(0, 100 - (metrics['response_time']['current'] / 50))
        
        total_score = (cpu_score * 0.4 + memory_score * 0.4 + response_score * 0.2)
        
        # 设置评分颜色
        if total_score >= 80:
            color = "rgb(0, 128, 0)"  # 绿色
        elif total_score >= 60:
            color = "rgb(255, 165, 0)"  # 橙色
        else:
            color = "rgb(255, 0, 0)"  # 红色
        
        self.score_label.setStyleSheet(f"""
            QLabel {{
                font-size: 24px;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
                background-color: {color};
                color: white;
            }}
        """)
        self.score_label.setText(f"性能评分: {total_score:.0f}") 