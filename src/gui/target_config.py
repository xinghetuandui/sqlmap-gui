from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                           QLineEdit, QTextEdit, QPushButton, QLabel, QComboBox,
                           QMessageBox, QFileDialog, QTabWidget, QWidget,
                           QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt
import json
import csv
import re
from urllib.parse import urlparse
from src.utils.cache_manager import CacheManager

class TargetConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("目标配置")
        self.resize(800, 600)
        
        # 初始化缓存管理器
        self.cache_manager = CacheManager()
        
        # 加载缓存的配置
        self.cached_config = self.cache_manager.load_cache('target_config')
        
        # 添加去重集合
        self.url_set = set()
        
        self.setup_ui()
        
        # 如果有缓存配置，恢复上次的设置
        if self.cached_config:
            self.restore_config(self.cached_config)
            
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 创建选项卡
        tab_widget = QTabWidget()
        
        # 单一目标选项卡
        single_tab = self._create_single_target_tab()
        tab_widget.addTab(single_tab, "单一目标")
        
        # 批量目标选项卡
        batch_tab = self._create_batch_target_tab()
        tab_widget.addTab(batch_tab, "批量目标")
        
        layout.addWidget(tab_widget)
        
        # 按钮
        button_layout = QHBoxLayout()
        self.ok_btn = QPushButton("确定")
        self.cancel_btn = QPushButton("取消")
        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 连接信号
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        
    def _create_single_target_tab(self) -> QWidget:
        """创建单一目标选项卡"""
        widget = QWidget()
        layout = QFormLayout()
        
        # URL输入
        self.url_edit = QLineEdit()
        layout.addRow("目标URL:", self.url_edit)
        
        # HTTP方法选择
        self.method_combo = QComboBox()
        self.method_combo.addItems(["GET", "POST"])
        layout.addRow("HTTP方法:", self.method_combo)
        
        # Headers输入
        self.headers_edit = QTextEdit()
        self.headers_edit.setPlaceholderText("每行一个header，格式：Key: Value")
        layout.addRow("Headers:", self.headers_edit)
        
        # Cookie输入
        self.cookie_edit = QLineEdit()
        layout.addRow("Cookie:", self.cookie_edit)
        
        widget.setLayout(layout)
        return widget
        
    def _create_batch_target_tab(self) -> QWidget:
        """创建批量目标选项卡"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 工具栏
        toolbar = QHBoxLayout()
        self.import_btn = QPushButton("导入")
        self.export_btn = QPushButton("导出")
        self.add_btn = QPushButton("添加")
        self.remove_btn = QPushButton("删除")
        self.clear_btn = QPushButton("清空")
        
        toolbar.addWidget(self.import_btn)
        toolbar.addWidget(self.export_btn)
        toolbar.addWidget(self.add_btn)
        toolbar.addWidget(self.remove_btn)
        toolbar.addWidget(self.clear_btn)
        toolbar.addStretch()
        
        layout.addLayout(toolbar)
        
        # 目标列表
        self.target_table = QTableWidget()
        self.target_table.setColumnCount(5)
        self.target_table.setHorizontalHeaderLabels([
            "URL", "方法", "Headers", "Cookie", "状态"
        ])
        header = self.target_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        
        layout.addWidget(self.target_table)
        
        widget.setLayout(layout)
        
        # 连接信号
        self.import_btn.clicked.connect(self.import_targets)
        self.export_btn.clicked.connect(self.export_targets)
        self.add_btn.clicked.connect(self.add_target)
        self.remove_btn.clicked.connect(self.remove_target)
        self.clear_btn.clicked.connect(self.clear_targets)
        
        return widget
        
    def import_targets(self):
        """导入目标"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "导入目标", "", 
            "文本文件 (*.txt);;CSV文件 (*.csv);;JSON文件 (*.json)"
        )
        if not filename:
            return
            
        try:
            if filename.endswith('.txt'):
                self._import_from_txt(filename)
            elif filename.endswith('.csv'):
                self._import_from_csv(filename)
            elif filename.endswith('.json'):
                self._import_from_json(filename)
                
            QMessageBox.information(self, "成功", "目标导入成功")
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"导入失败: {str(e)}")
            
    def _import_from_txt(self, filename: str):
        """从文本文件导入"""
        with open(filename, 'r', encoding='utf-8') as f:
            urls = f.readlines()
            
        for url in urls:
            url = url.strip()
            if url and self._is_valid_url(url):
                self._add_target_to_table({
                    'url': url,
                    'method': 'GET'
                })
                
    def _import_from_csv(self, filename: str):
        """从CSV文件导入"""
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'url' in row and self._is_valid_url(row['url']):
                    self._add_target_to_table(row)
                    
    def _import_from_json(self, filename: str):
        """从JSON文件导入"""
        with open(filename, 'r', encoding='utf-8') as f:
            targets = json.load(f)
            
        if isinstance(targets, list):
            for target in targets:
                if isinstance(target, dict) and 'url' in target:
                    if self._is_valid_url(target['url']):
                        self._add_target_to_table(target)
                        
    def export_targets(self):
        """导出目标"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "导出目标", "",
            "CSV文件 (*.csv);;JSON文件 (*.json)"
        )
        if not filename:
            return
            
        try:
            targets = self._get_targets_from_table()
            
            if filename.endswith('.csv'):
                self._export_to_csv(filename, targets)
            elif filename.endswith('.json'):
                self._export_to_json(filename, targets)
                
            QMessageBox.information(self, "成功", "目标导出成功")
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"导出失败: {str(e)}")
            
    def _export_to_csv(self, filename: str, targets: list):
        """导出为CSV文件"""
        if not targets:
            return
            
        fieldnames = ['url', 'method', 'headers', 'cookie']
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(targets)
            
    def _export_to_json(self, filename: str, targets: list):
        """导出为JSON文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(targets, f, indent=4, ensure_ascii=False)
            
    def add_target(self):
        """添加目标"""
        url = self.url_edit.text().strip()
        if not url:
            QMessageBox.warning(self, "错误", "请输入目标URL")
            return
            
        if not self._is_valid_url(url):
            QMessageBox.warning(self, "错误", "无效的URL格式")
            return
            
        target = {
            'url': url,
            'method': self.method_combo.currentText(),
            'headers': self.headers_edit.toPlainText(),
            'cookie': self.cookie_edit.text()
        }
        
        self._add_target_to_table(target)
        
    def remove_target(self):
        """删除目标"""
        current_row = self.target_table.currentRow()
        if current_row >= 0:
            self.target_table.removeRow(current_row)
            
    def clear_targets(self):
        """清空目标"""
        self.target_table.setRowCount(0)
        
    def _add_target_to_table(self, target: dict):
        """添加目标到表格"""
        url = target['url']
        
        # URL去重
        if url in self.url_set:
            return
        
        # 检查缓存
        cache_key = self.cache_manager._get_cache_key(target)
        cached_data = self.cache_manager.get(cache_key)
        if cached_data:
            target.update(cached_data)
        
        row = self.target_table.rowCount()
        self.target_table.insertRow(row)
        
        self.target_table.setItem(row, 0, QTableWidgetItem(url))
        self.target_table.setItem(row, 1, QTableWidgetItem(
            target.get('method', 'GET')))
        self.target_table.setItem(row, 2, QTableWidgetItem(
            target.get('headers', '')))
        self.target_table.setItem(row, 3, QTableWidgetItem(
            target.get('cookie', '')))
        self.target_table.setItem(row, 4, QTableWidgetItem("待扫描"))
        
        # 添加到去重集合
        self.url_set.add(url)
        
        # 缓存配置
        self.cache_manager.set(cache_key, target)
        
    def _get_targets_from_table(self) -> list:
        """从表格获取目标列表"""
        targets = []
        for row in range(self.target_table.rowCount()):
            target = {
                'url': self.target_table.item(row, 0).text(),
                'method': self.target_table.item(row, 1).text(),
                'headers': self.target_table.item(row, 2).text(),
                'cookie': self.target_table.item(row, 3).text()
            }
            targets.append(target)
        return targets
        
    def _is_valid_url(self, url: str) -> bool:
        """验证URL格式"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
            
    def get_config(self) -> dict:
        """获取配置"""
        # 如果在批量目标选项卡
        if self.target_table.rowCount() > 0:
            return {
                'targets': self._get_targets_from_table()
            }
            
        # 如果在单一目标选项卡
        return {
            'url': self.url_edit.text().strip(),
            'method': self.method_combo.currentText(),
            'headers': self.headers_edit.toPlainText(),
            'cookie': self.cookie_edit.text()
        } 