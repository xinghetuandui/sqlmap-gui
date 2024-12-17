from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                           QListWidget, QTextEdit, QMessageBox, QInputDialog,
                           QLabel, QSplitter, QWidget, QListWidgetItem)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from src.utils.tamper_manager import TamperManager

class TamperDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tamper脚本管理器")
        self.resize(1000, 600)
        
        self.tamper_manager = TamperManager()
        self.setup_ui()
        self.load_tampers()
        
    def setup_ui(self):
        layout = QHBoxLayout()
        
        # 左侧列表
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        
        list_label = QLabel("可用的Tamper脚本:")
        left_layout.addWidget(list_label)
        
        self.tamper_list = QListWidget()
        left_layout.addWidget(self.tamper_list)
        
        button_layout = QHBoxLayout()
        self.new_button = QPushButton("新建")
        self.delete_button = QPushButton("删除")
        self.delete_button.setEnabled(False)
        
        button_layout.addWidget(self.new_button)
        button_layout.addWidget(self.delete_button)
        left_layout.addLayout(button_layout)
        
        left_widget.setLayout(left_layout)
        
        # 右侧编辑器
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        
        self.info_label = QLabel("脚本信息:")
        right_layout.addWidget(self.info_label)
        
        self.editor = QTextEdit()
        self.editor.setFont(QFont("Courier New", 10))
        right_layout.addWidget(self.editor)
        
        editor_buttons = QHBoxLayout()
        self.save_button = QPushButton("保存")
        self.save_button.setEnabled(False)
        editor_buttons.addWidget(self.save_button)
        right_layout.addLayout(editor_buttons)
        
        right_widget.setLayout(right_layout)
        
        # 使用分割器
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([300, 700])
        
        layout.addWidget(splitter)
        self.setLayout(layout)
        
        # 连接信号
        self.connect_signals()
        
    def connect_signals(self):
        self.tamper_list.currentItemChanged.connect(self.on_tamper_selected)
        self.new_button.clicked.connect(self.create_new_tamper)
        self.delete_button.clicked.connect(self.delete_tamper)
        self.save_button.clicked.connect(self.save_tamper)
        
    def load_tampers(self):
        """加载所有tamper脚本"""
        self.tamper_list.clear()
        tampers = self.tamper_manager.get_available_tampers()
        
        for tamper in tampers:
            item = QListWidgetItem(tamper['name'])
            item.setData(Qt.UserRole, tamper)
            if tamper['is_system']:
                item.setForeground(Qt.gray)
            self.tamper_list.addItem(item)
            
    def on_tamper_selected(self, current, previous):
        """当选择tamper脚本时"""
        if not current:
            self.editor.clear()
            self.save_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            return
            
        tamper_info = current.data(Qt.UserRole)
        self.delete_button.setEnabled(not tamper_info['is_system'])
        self.save_button.setEnabled(not tamper_info['is_system'])
        
        # 显示脚本信息
        self.info_label.setText(
            f"脚本信息:\n"
            f"名称: {tamper_info['name']}\n"
            f"作者: {tamper_info['author']}\n"
            f"描述: {tamper_info['description']}"
        )
        
        # 加载脚本内容
        try:
            with open(tamper_info['path'], 'r', encoding='utf-8') as f:
                self.editor.setText(f.read())
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载脚本失败: {str(e)}")
            
    def create_new_tamper(self):
        """创建新的tamper脚本"""
        name, ok = QInputDialog.getText(self, "新建Tamper脚本", "请输入脚本名称:")
        
        if ok and name:
            try:
                content = self.tamper_manager.get_tamper_template()
                self.tamper_manager.create_tamper(name, content)
                self.load_tampers()
                
                # 选择新创建的脚本
                for i in range(self.tamper_list.count()):
                    item = self.tamper_list.item(i)
                    if item.data(Qt.UserRole)['name'] == name:
                        self.tamper_list.setCurrentItem(item)
                        break
                        
            except Exception as e:
                QMessageBox.warning(self, "错误", f"创建脚本失败: {str(e)}")
                
    def delete_tamper(self):
        """删除当前选中的tamper脚本"""
        current = self.tamper_list.currentItem()
        if not current:
            return
            
        tamper_info = current.data(Qt.UserRole)
        if tamper_info['is_system']:
            QMessageBox.warning(self, "错误", "系统脚本不能删除")
            return
            
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除脚本 {tamper_info['name']} 吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.tamper_manager.delete_tamper(tamper_info['name'])
                self.load_tampers()
            except Exception as e:
                QMessageBox.warning(self, "错误", f"删除脚本失败: {str(e)}")
                
    def save_tamper(self):
        """保存当前编辑的tamper脚本"""
        current = self.tamper_list.currentItem()
        if not current:
            return
            
        tamper_info = current.data(Qt.UserRole)
        if tamper_info['is_system']:
            QMessageBox.warning(self, "错误", "系统脚本不能修改")
            return
            
        try:
            content = self.editor.toPlainText()
            self.tamper_manager.edit_tamper(tamper_info['name'], content)
            QMessageBox.information(self, "成功", "保存成功")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"保存失败: {str(e)}") 