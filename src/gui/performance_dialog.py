from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QTabWidget, QWidget,
                           QPushButton, QLabel)
from PyQt5.QtChart import QChart, QChartView, QLineSeries
from PyQt5.QtCore import Qt

class PerformanceDialog(QDialog):
    def __init__(self, performance_stats: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("性能监控")
        self.resize(800, 600)
        self.stats = performance_stats
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 创建选项卡
        tab_widget = QTabWidget()
        
        # CPU使用率图表
        cpu_tab = self._create_chart_tab(
            self.stats['cpu_usage'],
            "CPU使用率",
            "时间",
            "使用率(%)"
        )
        tab_widget.addTab(cpu_tab, "CPU使用率")
        
        # 内存使用图表
        memory_tab = self._create_chart_tab(
            self.stats['memory_usage'],
            "内存使用",
            "时间",
            "使用量(MB)"
        )
        tab_widget.addTab(memory_tab, "内存使用")
        
        # 扫描时间图表
        duration_tab = self._create_chart_tab(
            self.stats['scan_duration'],
            "扫描时间",
            "任务",
            "时间(秒)"
        )
        tab_widget.addTab(duration_tab, "扫描时间")
        
        layout.addWidget(tab_widget)
        
        # 统计信息
        stats_label = QLabel()
        stats_text = f"""
        平均扫描时间: {self.stats.get('avg_duration', 0):.2f}秒
        最长扫描时间: {self.stats.get('max_duration', 0):.2f}秒
        最短扫描时间: {self.stats.get('min_duration', 0):.2f}秒
        平均CPU使用率: {self.stats.get('avg_cpu', 0):.2f}%
        最高CPU使用率: {self.stats.get('max_cpu', 0):.2f}%
        平均内存使用: {self.stats.get('avg_memory', 0):.2f}MB
        最高内存使用: {self.stats.get('max_memory', 0):.2f}MB
        """
        stats_label.setText(stats_text)
        layout.addWidget(stats_label)
        
        self.setLayout(layout)
        
    def _create_chart_tab(self, data: list, title: str, 
                         x_label: str, y_label: str) -> QWidget:
        """创建图表选项卡"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 创建图表
        series = QLineSeries()
        for i, value in enumerate(data):
            series.append(i, value)
            
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(title)
        chart.createDefaultAxes()
        chart.axisX().setTitleText(x_label)
        chart.axisY().setTitleText(y_label)
        
        chart_view = QChartView(chart)
        layout.addWidget(chart_view)
        
        widget.setLayout(layout)
        return widget 