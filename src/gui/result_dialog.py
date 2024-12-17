from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextEdit,
                           QPushButton, QLabel, QSplitter, QWidget, QTreeWidget,
                           QTreeWidgetItem)
from PyQt5.QtCore import Qt
import json

class ResultDialog(QDialog):
    def __init__(self, result_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("扫描结果")
        self.resize(1000, 700)
        self.result_data = result_data
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧树形结构
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("漏洞类型")
        self.tree.itemClicked.connect(self.show_details)
        left_layout.addWidget(self.tree)
        
        splitter.addWidget(left_widget)
        
        # 右侧详细信息
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        self.detail_edit = QTextEdit()
        self.detail_edit.setReadOnly(True)
        right_layout.addWidget(self.detail_edit)
        
        splitter.addWidget(right_widget)
        
        # 设置分割器比例
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        layout.addWidget(splitter)
        
        # 按钮
        button_layout = QHBoxLayout()
        self.export_btn = QPushButton("导出报告")
        self.close_btn = QPushButton("关闭")
        
        button_layout.addWidget(self.export_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 连接信号
        self.export_btn.clicked.connect(self.export_report)
        self.close_btn.clicked.connect(self.close)
        
        # 加载结果数据
        self.load_results()
        
    def load_results(self):
        """加载扫描结果"""
        if not self.result_data:
            self.tree.addTopLevelItem(QTreeWidgetItem(["无扫描结果"]))
            return
            
        try:
            # 解析结果数据
            if isinstance(self.result_data, str):
                data = json.loads(self.result_data)
            else:
                data = self.result_data
                
            # 添加漏洞类型
            for vuln_type, details in data.items():
                type_item = QTreeWidgetItem([vuln_type])
                self.tree.addTopLevelItem(type_item)
                
                # 添加具体漏洞
                for detail in details:
                    detail_item = QTreeWidgetItem([detail.get('title', '未知漏洞')])
                    detail_item.setData(0, Qt.UserRole, detail)
                    type_item.addChild(detail_item)
                    
            # 展开所有项
            self.tree.expandAll()
            
        except Exception as e:
            self.tree.addTopLevelItem(QTreeWidgetItem([f"加载结果失败: {str(e)}"]))
            
    def show_details(self, item):
        """显示漏洞详情"""
        detail_data = item.data(0, Qt.UserRole)
        if not detail_data:
            return
            
        # 格式化显示
        detail_text = f"""
漏洞标题: {detail_data.get('title', '未知')}

漏洞描述:
{detail_data.get('description', '无描述')}

影响范围:
{detail_data.get('affected', '未知')}

修复建议:
{detail_data.get('solution', '无建议')}

风险等级: {detail_data.get('risk_level', '未知')}
CVSS评分: {detail_data.get('cvss_score', '未知')}

发现时间: {detail_data.get('found_time', '未知')}
验证状态: {detail_data.get('verified', '未验证')}
        """
        
        self.detail_edit.setText(detail_text)
        
    def export_report(self):
        """导出报告"""
        # TODO: 实现报告导出功能
        pass