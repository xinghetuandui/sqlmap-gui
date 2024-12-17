from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                           QWidget, QLabel, QLineEdit, QTextEdit, QPushButton,
                           QListWidget, QListWidgetItem, QMessageBox, QFileDialog,
                           QGroupBox, QFormLayout, QMenu)
from PyQt5.QtCore import Qt
from src.core.config_manager import ConfigManager, ScanConfig
from datetime import datetime
import json

class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("扫描配置管理")
        self.resize(800, 600)
        self.config_manager = ConfigManager()
        self.setup_ui()
        self.load_templates()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 创建选项卡
        tab_widget = QTabWidget()
        
        # 模板选项卡
        templates_tab = self._create_templates_tab()
        tab_widget.addTab(templates_tab, "配置模板")
        
        # 自定义配置选项卡
        custom_tab = self._create_custom_tab()
        tab_widget.addTab(custom_tab, "自定义配置")
        
        layout.addWidget(tab_widget)
        self.setLayout(layout)
        
    def _create_templates_tab(self) -> QWidget:
        """创建模板选项卡"""
        widget = QWidget()
        layout = QHBoxLayout()
        
        # 左侧模板列表
        left_layout = QVBoxLayout()
        self.template_list = QListWidget()
        left_layout.addWidget(self.template_list)
        
        # 按钮
        button_layout = QHBoxLayout()
        self.load_btn = QPushButton("加载")
        self.export_btn = QPushButton("导出")
        self.import_btn = QPushButton("导入")
        button_layout.addWidget(self.load_btn)
        button_layout.addWidget(self.export_btn)
        button_layout.addWidget(self.import_btn)
        left_layout.addLayout(button_layout)
        
        # 右侧详情
        right_layout = QVBoxLayout()
        
        # 模板信息
        info_group = QGroupBox("模板信息")
        info_layout = QFormLayout()
        
        self.template_name = QLineEdit()
        self.template_name.setReadOnly(True)
        info_layout.addRow("名称:", self.template_name)
        
        self.template_desc = QTextEdit()
        self.template_desc.setReadOnly(True)
        info_layout.addRow("描述:", self.template_desc)
        
        self.create_time = QLineEdit()
        self.create_time.setReadOnly(True)
        info_layout.addRow("创建时间:", self.create_time)
        
        self.last_used = QLineEdit()
        self.last_used.setReadOnly(True)
        info_layout.addRow("最后使用:", self.last_used)
        
        info_group.setLayout(info_layout)
        right_layout.addWidget(info_group)
        
        # 配置预览
        preview_group = QGroupBox("配置预览")
        preview_layout = QVBoxLayout()
        self.config_preview = QTextEdit()
        self.config_preview.setReadOnly(True)
        preview_layout.addWidget(self.config_preview)
        preview_group.setLayout(preview_layout)
        right_layout.addWidget(preview_group)
        
        layout.addLayout(left_layout, 1)
        layout.addLayout(right_layout, 2)
        
        widget.setLayout(layout)
        
        # 连接信号
        self.template_list.currentItemChanged.connect(self.on_template_selected)
        self.load_btn.clicked.connect(self.load_template)
        self.export_btn.clicked.connect(self.export_template)
        self.import_btn.clicked.connect(self.import_template)
        
        return widget
        
    def _create_custom_tab(self) -> QWidget:
        """创建自定义配置选项卡"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 配置名
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("配置名称:"))
        self.config_name = QLineEdit()
        name_layout.addWidget(self.config_name)
        layout.addLayout(name_layout)
        
        # 配置编辑器
        self.config_editor = QTextEdit()
        self.config_editor.setPlaceholderText("在此输入JSON格式的配置")
        layout.addWidget(self.config_editor)
        
        # 按钮
        button_layout = QHBoxLayout()
        self.save_custom_btn = QPushButton("保存")
        self.load_custom_btn = QPushButton("加载")
        button_layout.addWidget(self.save_custom_btn)
        button_layout.addWidget(self.load_custom_btn)
        layout.addLayout(button_layout)
        
        widget.setLayout(layout)
        
        # 连接信号
        self.save_custom_btn.clicked.connect(self.save_custom_config)
        self.load_custom_btn.clicked.connect(self.load_custom_config)
        
        return widget
        
    def load_templates(self):
        """加载所有模板"""
        self.template_list.clear()
        templates = self.config_manager.get_all_templates()
        
        for template in templates:
            item = QListWidgetItem(template.name)
            item.setData(Qt.UserRole, template)
            self.template_list.addItem(item)
            
    def on_template_selected(self, current, previous):
        """当选择模板时"""
        if not current:
            return
            
        template = current.data(Qt.UserRole)
        
        # 更新模板信息
        self.template_name.setText(template.name)
        self.template_desc.setText(template.description)
        self.create_time.setText(template.create_time.strftime("%Y-%m-%d %H:%M:%S"))
        self.last_used.setText(
            template.last_used.strftime("%Y-%m-%d %H:%M:%S") if template.last_used else "从未使用"
        )
        
        # 更新配置预览
        preview = {
            'target_config': template.target_config,
            'scan_options': template.scan_options
        }
        if template.advanced_options:
            preview['advanced_options'] = template.advanced_options
            
        self.config_preview.setText(
            json.dumps(preview, indent=2, ensure_ascii=False)
        )
        
    def load_template(self):
        """加载选中的模板"""
        current = self.template_list.currentItem()
        if not current:
            return
            
        template = current.data(Qt.UserRole)
        template.last_used = datetime.now()
        self.config_manager.save_template(template)
        
        # 返回配置给主窗口
        self.selected_config = template
        self.accept()
        
    def export_template(self):
        """导出模板"""
        current = self.template_list.currentItem()
        if not current:
            return
            
        template = current.data(Qt.UserRole)
        filename, _ = QFileDialog.getSaveFileName(
            self, "导出配置", "", "JSON文件 (*.json)"
        )
        
        if filename:
            try:
                self.config_manager.export_config(template, filename)
                QMessageBox.information(self, "成功", "配置已导出")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"导出失败: {str(e)}")
                
    def import_template(self):
        """导入模板"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "导入配置", "", "JSON文件 (*.json)"
        )
        
        if filename:
            try:
                template = self.config_manager.import_config(filename)
                self.config_manager.save_template(template)
                self.load_templates()
                QMessageBox.information(self, "成功", "配置已导入")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"导入失败: {str(e)}")
                
    def save_custom_config(self):
        """保存自定义配置"""
        name = self.config_name.text().strip()
        if not name:
            QMessageBox.warning(self, "错误", "请输入配置名称")
            return
            
        try:
            config = json.loads(self.config_editor.toPlainText())
            self.config_manager.save_custom_config(config, name)
            QMessageBox.information(self, "成功", "配置已保存")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"保存失败: {str(e)}")
            
    def load_custom_config(self):
        """加载自定义配置"""
        name = self.config_name.text().strip()
        if not name:
            QMessageBox.warning(self, "错误", "请输入配置名称")
            return
            
        config = self.config_manager.load_custom_config(name)
        if config:
            self.config_editor.setText(
                json.dumps(config, indent=2, ensure_ascii=False)
            )
        else:
            QMessageBox.warning(self, "错误", "配置不存在")

    def show_template_menu(self, position):
        """显示模板右键菜单"""
        menu = QMenu()
        current = self.template_list.currentItem()
        
        load_action = menu.addAction("加载")
        duplicate_action = menu.addAction("复制")
        export_action = menu.addAction("导出")
        delete_action = menu.addAction("删除")
        
        # 如果没有选中项，禁用相关操作
        if not current:
            load_action.setEnabled(False)
            duplicate_action.setEnabled(False)
            export_action.setEnabled(False)
            delete_action.setEnabled(False)
        
        action = menu.exec_(self.template_list.mapToGlobal(position))
        if not action:
            return
        
        template = current.data(Qt.UserRole)
        
        if action == load_action:
            self.load_template()
        elif action == duplicate_action:
            self.duplicate_template(template)
        elif action == export_action:
            self.export_template()
        elif action == delete_action:
            self.delete_template(template)

    def duplicate_template(self, template: ScanConfig):
        """复制模板"""
        new_name = f"{template.name}_复制"
        new_template = ScanConfig(
            id=len(self.config_manager.get_all_templates()) + 1,
            name=new_name,
            description=template.description,
            target_config=template.target_config.copy(),
            scan_options=template.scan_options.copy(),
            advanced_options=template.advanced_options.copy() if template.advanced_options else None
        )
        
        try:
            self.config_manager.save_template(new_template)
            self.load_templates()
            QMessageBox.information(self, "成功", "模板已复制")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"复制失败: {str(e)}")

    def delete_template(self, template: ScanConfig):
        """删除模板"""
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除模板 {template.name} 吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.config_manager.delete_template(template.id)
                self.load_templates()
                QMessageBox.information(self, "成功", "模板已删除")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"删除失败: {str(e)}")

    def show_template_details(self, template: ScanConfig):
        """显示模板详细信息"""
        details = f"""
        模板名称: {template.name}
        描述: {template.description}
        创建时间: {template.create_time.strftime("%Y-%m-%d %H:%M:%S")}
        最后使用: {template.last_used.strftime("%Y-%m-%d %H:%M:%S") if template.last_used else "从未使用"}
        
        目标配置:
        {json.dumps(template.target_config, indent=2, ensure_ascii=False)}
        
        扫描选项:
        {json.dumps(template.scan_options, indent=2, ensure_ascii=False)}
        """
        
        if template.advanced_options:
            details += f"""
        高级选项:
        {json.dumps(template.advanced_options, indent=2, ensure_ascii=False)}
        """
        
        QMessageBox.information(self, "模板详情", details) 