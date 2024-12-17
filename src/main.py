from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QTextEdit, QTabWidget,
                           QStatusBar, QAction, QMenuBar, QLabel)
from PyQt5.QtCore import Qt
from src.gui.target_config import TargetConfigDialog
from src.core.sqlmap_wrapper import SQLMapWrapper
from src.gui.tamper_dialog import TamperDialog
from src.gui.decoder_dialog import DecoderDialog
from src.gui.advanced_dialog import AdvancedDialog
from src.gui.result_dialog import ResultDialog
from src.gui.task_dialog import TaskDialog
from src.core.task_manager import TaskManager, TaskStatus
from src.gui.advanced_options_dialog import AdvancedOptionsDialog
from src.gui.config_dialog import ConfigDialog
from src.gui.analysis_dialog import AnalysisDialog
from src.gui.proxy_dialog import ProxyDialog
from src.core.proxy_presets import PROXY_PRESETS
from src.utils.proxy_monitor import ProxyMonitor
from typing import Dict
from src.core.performance_manager import PerformanceManager, PerformanceMetrics
import os
import shutil

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SQLMap GUI - 零漏安全出品")
        self.resize(1200, 800)
        
        # 初始化组件
        self._init_components()
        
        # 初始化界面
        self.setup_ui()
        
        # 启动监控
        self._start_monitoring()
        
    def _init_components(self):
        """初始化组件"""
        try:
            # 初始化性能管理器
            self.performance_manager = PerformanceManager()
            
            # 初始化SQLMap包装器
            self.sqlmap = SQLMapWrapper()
            
            # 初始化任务管理器
            self.task_manager = TaskManager()
            
        except Exception as e:
            print(f"组件初始化失败: {str(e)}")
            raise
        
    def _start_monitoring(self):
        """启动监控"""
        try:
            # 启动性能监控
            if hasattr(self, 'performance_manager'):
                self.performance_manager.add_callback(self._update_performance_status)
                self.performance_manager.start_monitoring()
                
        except Exception as e:
            print(f"监控启动失败: {str(e)}")
        
    def setup_ui(self):
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建主���口件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 创建工具栏
        toolbar_layout = QHBoxLayout()
        self.target_button = QPushButton("配置目标")
        self.start_button = QPushButton("开始扫描")
        self.stop_button = QPushButton("停止扫描")
        self.stop_button.setEnabled(False)
        
        toolbar_layout.addWidget(self.target_button)
        toolbar_layout.addWidget(self.start_button)
        toolbar_layout.addWidget(self.stop_button)
        toolbar_layout.addStretch()
        
        main_layout.addLayout(toolbar_layout)
        
        # 创建选项卡
        self.tab_widget = QTabWidget()
        self.log_tab = QTextEdit()
        self.log_tab.setReadOnly(True)
        self.results_tab = QTextEdit()
        self.results_tab.setReadOnly(True)
        
        self.tab_widget.addTab(self.log_tab, "日志")
        self.tab_widget.addTab(self.results_tab, "结果")
        
        main_layout.addWidget(self.tab_widget)
        
        # 创建状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("就绪")
        
        # 添加代理状态显示
        self.proxy_status = QLabel()
        self.statusBar.addPermanentWidget(self.proxy_status)
        self.proxy_monitor = None
        
        # 添加性能状态标签
        self.performance_label = QLabel()
        self.statusBar.addPermanentWidget(self.performance_label)
        
        # 连接信号
        self.connect_signals()
        
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件")
        self.new_scan_action = QAction("新建扫描", self)
        self.save_results_action = QAction("保存结果", self)
        self.exit_action = QAction("退出", self)
        
        file_menu.addAction(self.new_scan_action)
        file_menu.addAction(self.save_results_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)
        
        # 工具菜单
        tools_menu = menubar.addMenu("工具")
        self.tamper_action = QAction("Tamper管理器", self)
        self.decoder_action = QAction("编码/解码工具", self)
        self.task_manager_action = QAction("任务管理", self)
        self.proxy_action = QAction("代理设置", self)
        self.performance_action = QAction("性能监控", self)
        tools_menu.addAction(self.tamper_action)
        tools_menu.addAction(self.decoder_action)
        tools_menu.addAction(self.task_manager_action)
        tools_menu.addAction(self.proxy_action)
        tools_menu.addAction(self.performance_action)
        
        # 扫描菜单
        scan_menu = menubar.addMenu("扫描")
        self.advanced_action = QAction("高级设置", self)
        self.results_action = QAction("查看结果", self)
        self.config_action = QAction("配置管理", self)
        self.analysis_action = QAction("结果分析", self)
        scan_menu.addAction(self.advanced_action)
        scan_menu.addAction(self.results_action)
        scan_menu.addAction(self.config_action)
        scan_menu.addAction(self.analysis_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        self.help_action = QAction("使用帮助", self)
        self.about_action = QAction("关于", self)
        help_menu.addAction(self.help_action)
        help_menu.addAction(self.about_action)
        
    def connect_signals(self):
        self.target_button.clicked.connect(self.show_target_config)
        self.start_button.clicked.connect(self.start_scan)
        self.stop_button.clicked.connect(self.stop_scan)
        self.exit_action.triggered.connect(self.close)
        self.tamper_action.triggered.connect(self.show_tamper_manager)
        self.decoder_action.triggered.connect(self.show_decoder)
        self.advanced_action.triggered.connect(self.show_advanced_settings)
        self.results_action.triggered.connect(self.show_results)
        self.task_manager_action.triggered.connect(self.show_task_manager)
        self.config_action.triggered.connect(self.show_config_manager)
        self.analysis_action.triggered.connect(self.show_analysis)
        self.help_action.triggered.connect(self.show_help)
        self.about_action.triggered.connect(self.show_about)
        self.proxy_action.triggered.connect(self.show_proxy_settings)
        self.performance_action.triggered.connect(self.show_performance_monitor)
        
    def show_target_config(self):
        dialog = TargetConfigDialog(self)
        if dialog.exec_():
            self.target_config = dialog.get_config()
            self.statusBar.showMessage(f"目标已配置: {self.target_config['url']}")
            
    def start_scan(self):
        if not hasattr(self, 'target_config'):
            self.statusBar.showMessage("请先配置目标")
            return
            
        # 合并所有选项
        options = {}
        if hasattr(self, 'scan_options'):
            options.update(self.scan_options)
        if hasattr(self, 'advanced_options'):
            options.update(self.advanced_options.to_sqlmap_args())
        
        # 创建新任务
        task = self.task_manager.create_task(
            name=f"扫描 {self.target_config['url']}",
            target_config=self.target_config,
            scan_options=options
        )
        
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.statusBar.showMessage("扫描中...")
        
        def log_callback(message):
            self.log_tab.append(message)
            
        def scan_completed(result):
            self.task_manager.update_task_status(
                task.id,
                TaskStatus.COMPLETED,
                result=result
            )
            self.scan_results = result
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.statusBar.showMessage("扫描完成")
            
        def scan_failed(error):
            self.task_manager.update_task_status(
                task.id,
                TaskStatus.FAILED,
                error=str(error)
            )
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.statusBar.showMessage(f"扫描失败: {error}")
            
        # 更新任务状态为运行中
        self.task_manager.update_task_status(task.id, TaskStatus.RUNNING)
        
        # 开始扫描
        self.sqlmap.start_scan(
            self.target_config,
            log_callback,
            scan_completed,
            scan_failed
        )
        
    def stop_scan(self):
        self.sqlmap.stop_scan()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.statusBar.showMessage("扫描已停止")
        
    def show_tamper_manager(self):
        dialog = TamperDialog(self)
        dialog.exec_()
        
    def show_decoder(self):
        dialog = DecoderDialog(self)
        dialog.exec_()
        
    def show_advanced_settings(self):
        dialog = AdvancedDialog(self)
        if dialog.exec_():
            self.scan_options = dialog.get_options()
            self.statusBar.showMessage("高级设置已更新")
        
    def show_results(self):
        if not hasattr(self, 'scan_results'):
            self.statusBar.showMessage("没有可用的扫描结果")
            return
        
        dialog = ResultDialog(self.scan_results, self)
        dialog.exec_()
        
    def show_task_manager(self):
        dialog = TaskDialog(self)
        dialog.exec_()
        
    def show_advanced_options(self):
        dialog = AdvancedOptionsDialog(self)
        if dialog.exec_():
            self.advanced_options = dialog.get_options()
            self.statusBar.showMessage("高级选项已更新")
        
    def show_config_manager(self):
        dialog = ConfigDialog(self)
        if dialog.exec_():
            config = dialog.selected_config
            # 更新目标配置
            self.target_config = config.target_config.copy()
            # 更新扫描选项
            self.scan_options = config.scan_options.copy()
            # 更新高级选项
            if config.advanced_options:
                self.advanced_options = config.advanced_options.copy()
            
            # 保存使用历史
            if hasattr(self, 'scan_results'):
                self.config_manager.add_template_history(
                    config.id,
                    self.scan_results
                )
            
            self.statusBar.showMessage(f"已加载配置: {config.name}")
        
    def show_analysis(self):
        if not hasattr(self, 'scan_results'):
            self.statusBar.showMessage("没有可用的扫描结果")
            return
        
        dialog = AnalysisDialog(self.scan_results, self)
        dialog.exec_()
        
    def show_help(self):
        """显示帮助对话框"""
        from src.gui.help_dialog import HelpDialog
        dialog = HelpDialog(self)
        dialog.exec_()
        
    def show_about(self):
        """显示关于对话框"""
        from src.gui.about_dialog import AboutDialog
        dialog = AboutDialog(self)
        dialog.exec_()
        
    def show_proxy_settings(self):
        """显示代理设置对话框"""
        dialog = ProxyDialog(self)
        if dialog.exec_():
            proxy_config = dialog.get_proxy_config()
            self.sqlmap.set_proxy(proxy_config)
            
            # 更新代理监控
            if self.proxy_monitor:
                self.proxy_monitor.stop()
            
            if proxy_config:
                self.proxy_monitor = ProxyMonitor(
                    proxy_config,
                    self._update_proxy_status
                )
                self.proxy_monitor.start()
                self.statusBar.showMessage("代理设置已更新")
            else:
                self.proxy_status.clear()
                self.statusBar.showMessage("代理已禁用")

    def _update_proxy_status(self, status: Dict):
        """更新代理状态显示"""
        if status['available']:
            self.proxy_status.setText(
                f"代理状态: 正常 (延迟: {status['latency']:.2f}秒)"
            )
            self.proxy_status.setStyleSheet("QLabel { color: rgb(0, 128, 0); }")  # 绿色
        else:
            self.proxy_status.setText(f"代理状态: 异常 ({status['error']})")
            self.proxy_status.setStyleSheet("QLabel { color: rgb(255, 0, 0); }")  # 红色

    def _update_performance_status(self, metrics: PerformanceMetrics):
        """更新性能状态显示"""
        try:
            if not metrics:
                return
            
            # 更新状态文本
            status_text = (f"CPU: {metrics.cpu_usage:.1f}% | "
                          f"内存: {metrics.memory_usage:.1f}MB | "
                          f"线程: {metrics.thread_count}")
            self.performance_label.setText(status_text)
            
            # 更新状态颜色
            self._update_status_color(metrics)
            
        except Exception as e:
            print(f"性能状态更新错误: {str(e)}")

    def _update_status_color(self, metrics: PerformanceMetrics):
        """更新状态颜色"""
        try:
            if (metrics.cpu_usage > 80 or 
                metrics.memory_usage > 1024 or 
                metrics.response_time > 5000):
                color = "rgb(255, 0, 0)"  # 红色
            elif (metrics.cpu_usage > 60 or 
                  metrics.memory_usage > 512 or 
                  metrics.response_time > 2000):
                color = "rgb(255, 165, 0)"  # 橙色
            else:
                color = "rgb(0, 128, 0)"  # 绿色
                
            self.performance_label.setStyleSheet(f"QLabel {{ color: {color}; }}")
            
        except Exception as e:
            print(f"状态颜色更新错误: {str(e)}")

    def closeEvent(self, event):
        """窗口关闭事件"""
        try:
            # 停止所有监控
            self._stop_monitoring()
            
            # 清理资源
            self._cleanup_resources()
            
            event.accept()
        except Exception as e:
            print(f"关闭窗口时发生错误: {str(e)}")
            event.accept()

    def _stop_monitoring(self):
        """停止所有监控"""
        # 停止性能监控
        if hasattr(self, 'performance_manager'):
            try:
                self.performance_manager.stop_monitoring()
            except Exception as e:
                print(f"停止性能监控失败: {str(e)}")
            
        # 停止代理监控
        if hasattr(self, 'proxy_monitor') and self.proxy_monitor:
            try:
                self.proxy_monitor.stop()
            except Exception as e:
                print(f"停止代理监控失败: {str(e)}")

    def _cleanup_resources(self):
        """清理资源"""
        try:
            # 清理临时文件
            if os.path.exists("sqlmap_results"):
                shutil.rmtree("sqlmap_results")
            
            # 清理缓存
            if os.path.exists("cache"):
                shutil.rmtree("cache")
            
        except Exception as e:
            print(f"清理资源失败: {str(e)}")

    def show_performance_monitor(self):
        """显示性能监控对话框"""
        from src.gui.performance_monitor_dialog import PerformanceMonitorDialog
        dialog = PerformanceMonitorDialog(self.performance_manager, self)
        dialog.exec_()

def main():
    """程序入口函数"""
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_()) 