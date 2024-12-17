from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                           QWidget, QLabel, QLineEdit, QCheckBox, QSpinBox,
                           QPushButton, QComboBox, QGroupBox, QFormLayout)
from PyQt5.QtCore import Qt

class AdvancedDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("高级设置")
        self.resize(800, 600)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 创建选项卡
        tab_widget = QTabWidget()
        
        # 注入选项
        injection_tab = QWidget()
        injection_layout = QVBoxLayout(injection_tab)
        
        # 注入技术
        tech_group = QGroupBox("注入技术")
        tech_layout = QVBoxLayout()
        self.bool_check = QCheckBox("布尔盲注 (B)")
        self.error_check = QCheckBox("报错注入 (E)")
        self.union_check = QCheckBox("联合查询注入 (U)")
        self.stacked_check = QCheckBox("堆叠注入 (S)")
        self.time_check = QCheckBox("时间盲注 (T)")
        
        tech_layout.addWidget(self.bool_check)
        tech_layout.addWidget(self.error_check)
        tech_layout.addWidget(self.union_check)
        tech_layout.addWidget(self.stacked_check)
        tech_layout.addWidget(self.time_check)
        tech_group.setLayout(tech_layout)
        injection_layout.addWidget(tech_group)
        
        # 注入参数
        param_group = QGroupBox("注入参数")
        param_layout = QFormLayout()
        
        self.level_spin = QSpinBox()
        self.level_spin.setRange(1, 5)
        self.level_spin.setValue(1)
        param_layout.addRow("测试级别(1-5):", self.level_spin)
        
        self.risk_spin = QSpinBox()
        self.risk_spin.setRange(1, 3)
        self.risk_spin.setValue(1)
        param_layout.addRow("风险等级(1-3):", self.risk_spin)
        
        self.threads_spin = QSpinBox()
        self.threads_spin.setRange(1, 10)
        self.threads_spin.setValue(1)
        param_layout.addRow("线程数:", self.threads_spin)
        
        param_group.setLayout(param_layout)
        injection_layout.addWidget(param_group)
        
        tab_widget.addTab(injection_tab, "注入选项")
        
        # 枚举选项
        enum_tab = QWidget()
        enum_layout = QVBoxLayout(enum_tab)
        
        enum_group = QGroupBox("枚举选项")
        enum_layout_inner = QVBoxLayout()
        self.dbs_check = QCheckBox("枚举数据库")
        self.tables_check = QCheckBox("枚举表")
        self.columns_check = QCheckBox("枚举列")
        self.dump_check = QCheckBox("导出数据")
        
        enum_layout_inner.addWidget(self.dbs_check)
        enum_layout_inner.addWidget(self.tables_check)
        enum_layout_inner.addWidget(self.columns_check)
        enum_layout_inner.addWidget(self.dump_check)
        enum_group.setLayout(enum_layout_inner)
        enum_layout.addWidget(enum_group)
        
        tab_widget.addTab(enum_tab, "枚举选项")
        
        # 其他选项
        misc_tab = QWidget()
        misc_layout = QVBoxLayout(misc_tab)
        
        # 输出选项
        output_group = QGroupBox("输出选项")
        output_layout = QVBoxLayout()
        self.verbose_check = QCheckBox("详细输出")
        self.batch_check = QCheckBox("批量模式")
        
        output_layout.addWidget(self.verbose_check)
        output_layout.addWidget(self.batch_check)
        output_group.setLayout(output_layout)
        misc_layout.addWidget(output_group)
        
        tab_widget.addTab(misc_tab, "其他选项")
        
        layout.addWidget(tab_widget)
        
        # 按钮
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("保存")
        self.cancel_button = QPushButton("取消")
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 连接信号
        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
    def get_options(self) -> dict:
        """获取设置的选项"""
        # 构建注入技术字符串
        tech = ""
        if self.bool_check.isChecked(): tech += "B"
        if self.error_check.isChecked(): tech += "E"
        if self.union_check.isChecked(): tech += "U"
        if self.stacked_check.isChecked(): tech += "S"
        if self.time_check.isChecked(): tech += "T"
        
        return {
            'technique': tech,
            'level': self.level_spin.value(),
            'risk': self.risk_spin.value(),
            'threads': self.threads_spin.value(),
            'getDbs': self.dbs_check.isChecked(),
            'getTables': self.tables_check.isChecked(),
            'getColumns': self.columns_check.isChecked(),
            'dumpData': self.dump_check.isChecked(),
            'verbose': self.verbose_check.isChecked(),
            'batch': self.batch_check.isChecked()
        } 