from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextEdit,
                           QPushButton, QLabel, QComboBox, QSplitter)
from PyQt5.QtCore import Qt
import requests
import json

class ReplayDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("请求重放")
        self.resize(800, 600)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 请求方法选择
        method_layout = QHBoxLayout()
        method_layout.addWidget(QLabel("请求方法:"))
        self.method_combo = QComboBox()
        self.method_combo.addItems(["GET", "POST", "PUT", "DELETE"])
        method_layout.addWidget(self.method_combo)
        method_layout.addStretch()
        layout.addLayout(method_layout)
        
        # 创建分割器
        splitter = QSplitter(Qt.Vertical)
        
        # 请求编辑区
        request_widget = QWidget()
        request_layout = QVBoxLayout(request_widget)
        request_layout.addWidget(QLabel("请求内容:"))
        self.request_edit = QTextEdit()
        self.request_edit.setPlaceholderText("输入请求内容...")
        request_layout.addWidget(self.request_edit)
        splitter.addWidget(request_widget)
        
        # 响应显示区
        response_widget = QWidget()
        response_layout = QVBoxLayout(response_widget)
        response_layout.addWidget(QLabel("响应内容:"))
        self.response_edit = QTextEdit()
        self.response_edit.setReadOnly(True)
        response_layout.addWidget(self.response_edit)
        splitter.addWidget(response_widget)
        
        layout.addWidget(splitter)
        
        # 按钮
        button_layout = QHBoxLayout()
        self.send_btn = QPushButton("发送")
        self.clear_btn = QPushButton("清除")
        self.close_btn = QPushButton("关闭")
        
        button_layout.addWidget(self.send_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 连接信号
        self.send_btn.clicked.connect(self.send_request)
        self.clear_btn.clicked.connect(self.clear_content)
        self.close_btn.clicked.connect(self.close)
        
    def send_request(self):
        """发送请求"""
        try:
            # 获取请求内容
            request_data = self.request_edit.toPlainText().strip()
            if not request_data:
                self.response_edit.setText("错误: 请求内容不能为空")
                return
                
            # 解析请求数据
            try:
                data = json.loads(request_data)
            except json.JSONDecodeError:
                data = request_data
                
            # 发送请求
            method = self.method_combo.currentText()
            response = requests.request(
                method=method,
                url=data.get('url', ''),
                headers=data.get('headers', {}),
                data=data.get('data', {}),
                timeout=10
            )
            
            # 显示响应
            self.show_response(response)
            
        except Exception as e:
            self.response_edit.setText(f"错误: {str(e)}")
            
    def show_response(self, response):
        """显示响应内容"""
        # 状态行
        status_line = f"HTTP/1.1 {response.status_code} {response.reason}\n"
        
        # 响应头
        headers = '\n'.join(f"{k}: {v}" for k, v in response.headers.items())
        
        # 响应体
        try:
            body = json.dumps(response.json(), indent=2, ensure_ascii=False)
        except:
            body = response.text
            
        # 组合响应内容
        response_text = f"{status_line}\n{headers}\n\n{body}"
        self.response_edit.setText(response_text)
        
    def clear_content(self):
        """清除内容"""
        self.request_edit.clear()
        self.response_edit.clear() 