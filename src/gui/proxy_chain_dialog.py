from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget,
                           QPushButton, QMessageBox, QInputDialog)
from typing import List

class ProxyChainDialog(QDialog):
    def __init__(self, proxies: List[dict] = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("代理链配置")
        self.resize(400, 300)
        self.proxies = proxies or []
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 代理列表
        self.proxy_list = QListWidget()
        self.update_proxy_list()
        layout.addWidget(self.proxy_list)
        
        # 按钮
        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("添加")
        self.remove_btn = QPushButton("删除")
        self.up_btn = QPushButton("上移")
        self.down_btn = QPushButton("下移")
        
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.remove_btn)
        button_layout.addWidget(self.up_btn)
        button_layout.addWidget(self.down_btn)
        
        layout.addLayout(button_layout)
        
        # 确定取消按钮
        dialog_buttons = QHBoxLayout()
        self.ok_btn = QPushButton("确定")
        self.cancel_btn = QPushButton("取消")
        dialog_buttons.addWidget(self.ok_btn)
        dialog_buttons.addWidget(self.cancel_btn)
        
        layout.addLayout(dialog_buttons)
        
        self.setLayout(layout)
        
        # 连接信号
        self.add_btn.clicked.connect(self.add_proxy)
        self.remove_btn.clicked.connect(self.remove_proxy)
        self.up_btn.clicked.connect(self.move_up)
        self.down_btn.clicked.connect(self.move_down)
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        
    def update_proxy_list(self):
        """更新代理列表"""
        self.proxy_list.clear()
        for proxy in self.proxies:
            text = f"{proxy['type']}://{proxy['host']}:{proxy['port']}"
            if proxy.get('auth', {}).get('enabled'):
                text = f"{proxy['auth']['username']}@{text}"
            self.proxy_list.addItem(text)
            
    def add_proxy(self):
        """添加代理"""
        dialog = ProxyDialog(self)
        if dialog.exec_():
            proxy_config = dialog.get_config()
            self.proxies.append(proxy_config)
            self.update_proxy_list()
            
    def remove_proxy(self):
        """删除代理"""
        current = self.proxy_list.currentRow()
        if current >= 0:
            self.proxies.pop(current)
            self.update_proxy_list()
            
    def move_up(self):
        """上移代理"""
        current = self.proxy_list.currentRow()
        if current > 0:
            self.proxies[current], self.proxies[current-1] = \
                self.proxies[current-1], self.proxies[current]
            self.update_proxy_list()
            self.proxy_list.setCurrentRow(current-1)
            
    def move_down(self):
        """下移代理"""
        current = self.proxy_list.currentRow()
        if current < len(self.proxies) - 1:
            self.proxies[current], self.proxies[current+1] = \
                self.proxies[current+1], self.proxies[current]
            self.update_proxy_list()
            self.proxy_list.setCurrentRow(current+1)
            
    def get_proxies(self) -> List[dict]:
        """获取代理链配置"""
        return self.proxies 