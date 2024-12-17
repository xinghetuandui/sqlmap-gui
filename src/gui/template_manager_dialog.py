from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                           QWidget, QLabel, QLineEdit, QTextEdit, QPushButton,
                           QListWidget, QListWidgetItem, QMessageBox, QFileDialog,
                           QGroupBox, QFormLayout, QComboBox, QCheckBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from src.core.config_template_manager import ConfigTemplateManager, ConfigTemplate
from datetime import datetime
import json

class TemplateManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("配置模板管理")
        self.resize(1000, 700)
        
        self.template_manager = ConfigTemplateManager()
        self.setup_ui()
        self.load_templates()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 创建选项卡
        tab_widget = QTabWidget()
        
        # 模板管理选项卡
        templates_tab = self._create_templates_tab()
        tab_widget.addTab(templates_tab, "配置模板")
        
        # 快捷配置选项卡
        quick_tab = self._create_quick_configs_tab()
        tab_widget.addTab(quick_tab, "快捷配置")
        
        # 导入/导出选项卡
        import_export_tab = self._create_import_export_tab()
        tab_widget.addTab(import_export_tab, "导入/导出")
        
        layout.addWidget(tab_widget)
        self.setLayout(layout)
        
    def _create_templates_tab(self) -> QWidget:
        """创建模板管理选项卡"""
        widget = QWidget()
        layout = QHBoxLayout()
        
        # 左侧模板列表
        left_layout = QVBoxLayout()
        
        # 搜索框
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("搜索:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入模板名称或标签")
        search_layout.addWidget(self.search_input)
        left_layout.addLayout(search_layout)
        
        # 模板列表
        self.template_list = QListWidget()
        left_layout.addWidget(self.template_list)
        
        # 按钮
        button_layout = QHBoxLayout()
        self.new_btn = QPushButton("新建")
        self.delete_btn = QPushButton("删除")
        self.copy_btn = QPushButton("复制")
        self.history_btn = QPushButton("版本历史")
        button_layout.addWidget(self.new_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(self.copy_btn)
        button_layout.addWidget(self.history_btn)
        left_layout.addLayout(button_layout)
        
        # 右侧详情
        right_layout = QVBoxLayout()
        
        # 基本信息
        info_group = QGroupBox("基本信息")
        info_layout = QFormLayout()
        
        self.template_name = QLineEdit()
        info_layout.addRow("名称:", self.template_name)
        
        self.template_desc = QTextEdit()
        self.template_desc.setMaximumHeight(100)
        info_layout.addRow("描述:", self.template_desc)
        
        self.template_category = QComboBox()
        self.template_category.addItems(["常用", "自定义", "团队共享"])
        info_layout.addRow("分类:", self.template_category)
        
        self.template_tags = QLineEdit()
        self.template_tags.setPlaceholderText("用逗号分隔多个标签")
        info_layout.addRow("标签:", self.template_tags)
        
        info_group.setLayout(info_layout)
        right_layout.addWidget(info_group)
        
        # 配置内容
        content_group = QGroupBox("配置内容")
        content_layout = QVBoxLayout()
        
        self.config_edit = QTextEdit()
        self.config_edit.setPlaceholderText("JSON格式的配置内容")
        content_layout.addWidget(self.config_edit)
        
        content_group.setLayout(content_layout)
        right_layout.addWidget(content_group)
        
        # 保存按钮
        self.save_btn = QPushButton("保存")
        right_layout.addWidget(self.save_btn)
        
        layout.addLayout(left_layout, 1)
        layout.addLayout(right_layout, 2)
        widget.setLayout(layout)
        
        # 连接信号
        self.search_input.textChanged.connect(self.filter_templates)
        self.template_list.currentItemChanged.connect(self.on_template_selected)
        self.new_btn.clicked.connect(self.create_template)
        self.delete_btn.clicked.connect(self.delete_template)
        self.copy_btn.clicked.connect(self.copy_template)
        self.save_btn.clicked.connect(self.save_template)
        self.history_btn.clicked.connect(self.show_version_history)
        
        return widget
        
    def _create_quick_configs_tab(self) -> QWidget:
        """创建快捷配置选项卡"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 快捷配置列表
        self.quick_list = QListWidget()
        layout.addWidget(self.quick_list)
        
        # 按钮
        button_layout = QHBoxLayout()
        self.add_quick_btn = QPushButton("添加到快捷配置")
        self.remove_quick_btn = QPushButton("移除")
        button_layout.addWidget(self.add_quick_btn)
        button_layout.addWidget(self.remove_quick_btn)
        layout.addLayout(button_layout)
        
        widget.setLayout(layout)
        
        # 连接信号
        self.add_quick_btn.clicked.connect(self.add_quick_config)
        self.remove_quick_btn.clicked.connect(self.remove_quick_config)
        
        return widget
        
    def _create_import_export_tab(self) -> QWidget:
        """创建导入/导出选项卡"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 导出选项
        export_group = QGroupBox("导出选项")
        export_layout = QVBoxLayout()
        
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("导出格���:"))
        self.export_format = QComboBox()
        self.export_format.addItems(["JSON", "XML"])
        format_layout.addWidget(self.export_format)
        export_layout.addLayout(format_layout)
        
        self.export_btn = QPushButton("导出选中的模板")
        export_layout.addWidget(self.export_btn)
        
        export_group.setLayout(export_layout)
        layout.addWidget(export_group)
        
        # 导入选项
        import_group = QGroupBox("导入选项")
        import_layout = QVBoxLayout()
        
        self.import_btn = QPushButton("导入模板")
        import_layout.addWidget(self.import_btn)
        
        import_group.setLayout(import_layout)
        layout.addWidget(import_group)
        
        widget.setLayout(layout)
        
        # 连接信号
        self.export_btn.clicked.connect(self.export_template)
        self.import_btn.clicked.connect(self.import_template)
        
        return widget
        
    def load_templates(self):
        """加载所有模板"""
        self.template_list.clear()
        templates = self.template_manager.get_all_templates()
        
        for template in templates:
            self._add_template_item(template)
            
        # 加载快捷配置
        self.quick_list.clear()
        quick_configs = self.template_manager.get_quick_configs()
        for config in quick_configs:
            self._add_quick_config_item(config)
            
    def _add_template_item(self, template: ConfigTemplate):
        """添加模板项到列表"""
        item = QListWidgetItem(template.name)
        item.setData(Qt.UserRole, template)
        if template.category == "常用":
            item.setBackground(QColor(200, 255, 200))
        elif template.category == "团队共享":
            item.setBackground(QColor(200, 200, 255))
        self.template_list.addItem(item)
        
    def _add_quick_config_item(self, config: ConfigTemplate):
        """添加快捷配置项到列表"""
        item = QListWidgetItem(config.name)
        item.setData(Qt.UserRole, config)
        self.quick_list.addItem(item)
        
    def filter_templates(self):
        """过滤模板列表"""
        search_text = self.search_input.text().lower()
        for i in range(self.template_list.count()):
            item = self.template_list.item(i)
            template = item.data(Qt.UserRole)
            
            # 检查名称和标签
            name_match = search_text in template.name.lower()
            tag_match = any(search_text in tag.lower() for tag in (template.tags or []))
            
            item.setHidden(not (name_match or tag_match))
            
    def on_template_selected(self, current, previous):
        """当选择模板时"""
        if not current:
            return
            
        template = current.data(Qt.UserRole)
        
        # 更新基本信息
        self.template_name.setText(template.name)
        self.template_desc.setText(template.description)
        self.template_category.setCurrentText(template.category)
        self.template_tags.setText(", ".join(template.tags or []))
        
        # 更新配置内容
        config_data = {
            'target_config': template.target_config,
            'scan_options': template.scan_options,
            'advanced_options': template.advanced_options
        }
        self.config_edit.setText(
            json.dumps(config_data, indent=2, ensure_ascii=False)
        )
        
    def create_template(self):
        """创建新模板"""
        template = ConfigTemplate(
            name="新模板",
            description="",
            category="自定义",
            target_config={},
            scan_options={},
            tags=[]
        )
        
        self._add_template_item(template)
        self.template_list.setCurrentRow(self.template_list.count() - 1)
        
    def delete_template(self):
        """删除模板"""
        current = self.template_list.currentItem()
        if not current:
            return
            
        template = current.data(Qt.UserRole)
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除模板 {template.name} 吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.template_list.takeItem(self.template_list.row(current))
            
    def copy_template(self):
        """复制模板"""
        current = self.template_list.currentItem()
        if not current:
            return
            
        template = current.data(Qt.UserRole)
        new_template = ConfigTemplate(
            name=f"{template.name}_复制",
            description=template.description,
            category=template.category,
            target_config=template.target_config.copy(),
            scan_options=template.scan_options.copy(),
            advanced_options=template.advanced_options.copy() if template.advanced_options else None,
            tags=template.tags.copy() if template.tags else None
        )
        
        self._add_template_item(new_template)
        self.template_list.setCurrentRow(self.template_list.count() - 1)
        
    def save_template(self):
        """保存模板"""
        current = self.template_list.currentItem()
        if not current:
            return
            
        template = current.data(Qt.UserRole)
        
        # 更新基本信息
        template.name = self.template_name.text()
        template.description = self.template_desc.toPlainText()
        template.category = self.template_category.currentText()
        template.tags = [tag.strip() for tag in self.template_tags.text().split(",") if tag.strip()]
        
        # 更新配置内容
        try:
            config_data = json.loads(self.config_edit.toPlainText())
            template.target_config = config_data['target_config']
            template.scan_options = config_data['scan_options']
            template.advanced_options = config_data.get('advanced_options')
        except Exception as e:
            QMessageBox.warning(self, "错误", f"配置格式错误: {str(e)}")
            return
            
        # 保存到文件
        try:
            self.template_manager.save_template(template)
            current.setText(template.name)
            QMessageBox.information(self, "成功", "模板已保存")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"保存失败: {str(e)}")
            
    def add_quick_config(self):
        """添加到快捷配置"""
        current = self.template_list.currentItem()
        if not current:
            return
            
        template = current.data(Qt.UserRole)
        try:
            self.template_manager.save_quick_config(template)
            self._add_quick_config_item(template)
            QMessageBox.information(self, "成功", "已添加到快捷配置")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"添加失败: {str(e)}")
            
    def remove_quick_config(self):
        """移除快捷配置"""
        current = self.quick_list.currentItem()
        if not current:
            return
            
        config = current.data(Qt.UserRole)
        reply = QMessageBox.question(
            self, "确认移除",
            f"确定要移除快捷配置 {config.name} 吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.quick_list.takeItem(self.quick_list.row(current))
            
    def export_template(self):
        """导出模板"""
        current = self.template_list.currentItem()
        if not current:
            return
            
        template = current.data(Qt.UserRole)
        format = self.export_format.currentText().lower()
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "导出模板",
            f"{template.name}.{format}",
            f"{format.upper()}文件 (*.{format})"
        )
        
        if filename:
            try:
                self.template_manager.export_template(template, filename, format)
                QMessageBox.information(self, "成功", "模板已导出")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"导出失败: {str(e)}")
                
    def import_template(self):
        """导入模板"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "导入模板", "",
            "模板文件 (*.json *.xml)"
        )
        
        if filename:
            try:
                template = self.template_manager.import_template(filename)
                self._add_template_item(template)
                QMessageBox.information(self, "成功", "模板已导入")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"导入失败: {str(e)}")
                
    def show_version_history(self):
        """显示版本历史"""
        current = self.template_list.currentItem()
        if not current:
            return
        
        template = current.data(Qt.UserRole)
        versions = self.template_manager.get_template_versions(template.name)
        
        dialog = QDialog(self)
        dialog.setWindowTitle("版本历史")
        dialog.resize(600, 400)
        
        layout = QVBoxLayout()
        
        # 版本列表
        version_list = QListWidget()
        for version in versions:
            item = QListWidgetItem(f"版本 {version.version_id}")
            item.setData(Qt.UserRole, version)
            version_list.addItem(item)
        
        layout.addWidget(version_list)
        
        # 版本详情
        detail_text = QTextEdit()
        detail_text.setReadOnly(True)
        layout.addWidget(detail_text)
        
        # 回滚按钮
        rollback_btn = QPushButton("回滚到此版本")
        layout.addWidget(rollback_btn)
        
        dialog.setLayout(layout)
        
        def show_version_detail(item):
            if not item:
                return
            version = item.data(Qt.UserRole)
            detail = f"""
            版本ID: {version.version_id}
            创建时间: {version.create_time.strftime('%Y-%m-%d %H:%M:%S')}
            作者: {version.author}
            备注: {version.comment}
            
            配置内容:
            {json.dumps(version.content, indent=2, ensure_ascii=False)}
            """
            detail_text.setText(detail)
        
        def rollback_version():
            item = version_list.currentItem()
            if not item:
                return
            
            version = item.data(Qt.UserRole)
            reply = QMessageBox.question(
                dialog,
                "确认回滚",
                f"确定要回滚到版本 {version.version_id} 吗？",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                try:
                    self.template_manager.rollback_template(
                        template.name,
                        version.version_id
                    )
                    QMessageBox.information(dialog, "成功", "已回滚到选中版本")
                    dialog.accept()
                    self.load_templates()
                except Exception as e:
                    QMessageBox.warning(dialog, "错误", f"回滚失败: {str(e)}")
                
        version_list.currentItemChanged.connect(show_version_detail)
        rollback_btn.clicked.connect(rollback_version)
        
        if versions:
            version_list.setCurrentRow(0)
        
        dialog.exec_() 