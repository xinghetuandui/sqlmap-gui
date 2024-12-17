from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                           QPushButton, QComboBox, QCheckBox, QGroupBox,
                           QTableWidget, QTableWidgetItem, QHeaderView,
                           QMessageBox, QFileDialog, QWidget, QTabWidget,
                           QGridLayout)
from PyQt5.QtCore import Qt
from typing import Dict, List
from PyQt5.QtGui import QColor
from src.utils.proxy_pool import ProxyPool

class ProxyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("代理设置")
        self.resize(600, 400)
        
        # 初始化代理配置
        self.proxy_type = "HTTP"
        self.proxy_host = ""
        self.proxy_port = ""
        self.auth_enabled = False
        self.auth_username = ""
        self.auth_password = ""
        self.proxy_chain = []  # 添加代理链列表
        self.proxy_pool = ProxyPool()  # 初始化代理池
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 创建选项卡
        self.tab_widget = QTabWidget()
        
        # 基本设置选项卡
        basic_tab = QWidget()
        basic_layout = QVBoxLayout()
        
        # 代理类型
        type_group = QGroupBox("代理类型")
        type_layout = QHBoxLayout()
        self.type_combo = QComboBox()
        self.type_combo.addItems(["HTTP", "SOCKS4", "SOCKS5"])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        type_layout.addWidget(self.type_combo)
        type_group.setLayout(type_layout)
        basic_layout.addWidget(type_group)
        
        # 代理服务器
        server_group = QGroupBox("代理服务器")
        server_layout = QVBoxLayout()
        
        host_layout = QHBoxLayout()
        host_layout.addWidget(QLabel("主机:"))
        self.host_edit = QLineEdit()
        host_layout.addWidget(self.host_edit)
        host_layout.addWidget(QLabel("端口:"))
        self.port_edit = QLineEdit()
        self.port_edit.setMaximumWidth(100)
        host_layout.addWidget(self.port_edit)
        server_layout.addLayout(host_layout)
        
        server_group.setLayout(server_layout)
        basic_layout.addWidget(server_group)
        
        # 代理认证
        auth_group = QGroupBox("代理认证")
        auth_layout = QVBoxLayout()
        
        self.auth_check = QCheckBox("启用认证")
        self.auth_check.stateChanged.connect(self.on_auth_changed)
        auth_layout.addWidget(self.auth_check)
        
        auth_form = QHBoxLayout()
        auth_form.addWidget(QLabel("用户名:"))
        self.username_edit = QLineEdit()
        self.username_edit.setEnabled(False)
        auth_form.addWidget(self.username_edit)
        auth_form.addWidget(QLabel("密码:"))
        self.password_edit = QLineEdit()
        self.password_edit.setEnabled(False)
        self.password_edit.setEchoMode(QLineEdit.Password)
        auth_form.addWidget(self.password_edit)
        auth_layout.addLayout(auth_form)
        
        auth_group.setLayout(auth_layout)
        basic_layout.addWidget(auth_group)
        
        # 代理链
        chain_group = QGroupBox("代理链")
        chain_layout = QVBoxLayout()
        
        chain_buttons = QHBoxLayout()
        self.add_chain_btn = QPushButton("添加代理")
        self.add_chain_btn.clicked.connect(self.show_proxy_chain)
        chain_buttons.addWidget(self.add_chain_btn)
        chain_buttons.addStretch()
        chain_layout.addLayout(chain_buttons)
        
        # 代理链表格
        self.chain_table = QTableWidget()
        self.chain_table.setColumnCount(4)
        self.chain_table.setHorizontalHeaderLabels(["类型", "主机", "端口", "认证"])
        header = self.chain_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        chain_layout.addWidget(self.chain_table)
        
        chain_group.setLayout(chain_layout)
        basic_layout.addWidget(chain_group)
        
        basic_tab.setLayout(basic_layout)
        self.tab_widget.addTab(basic_tab, "基本设置")
        
        # 代理池选项卡
        pool_tab = QWidget()
        pool_layout = QVBoxLayout()
        
        # 代理池工具栏
        pool_toolbar = QHBoxLayout()
        self.import_btn = QPushButton("导入代理")
        self.export_btn = QPushButton("导出代理")
        self.refresh_btn = QPushButton("刷新状态")
        pool_toolbar.addWidget(self.import_btn)
        pool_toolbar.addWidget(self.export_btn)
        pool_toolbar.addWidget(self.refresh_btn)
        pool_toolbar.addStretch()
        pool_layout.addLayout(pool_toolbar)
        
        # 代理池表格
        self.pool_table = QTableWidget()
        self.pool_table.setColumnCount(6)
        self.pool_table.setHorizontalHeaderLabels([
            "类型", "主机", "端口", "延迟", "状态", "失败次数"
        ])
        header = self.pool_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        pool_layout.addWidget(self.pool_table)
        
        # 代理池设置
        settings_group = QGroupBox("代理池设置")
        settings_layout = QVBoxLayout()
        
        self.auto_switch = QCheckBox("自动切换代理")
        self.auto_switch.setChecked(True)
        settings_layout.addWidget(self.auto_switch)
        
        switch_options = QHBoxLayout()
        switch_options.addWidget(QLabel("检查间隔:"))
        self.interval_edit = QLineEdit("30")
        self.interval_edit.setMaximumWidth(50)
        switch_options.addWidget(self.interval_edit)
        switch_options.addWidget(QLabel("秒"))
        switch_options.addStretch()
        settings_layout.addLayout(switch_options)
        
        settings_group.setLayout(settings_layout)
        pool_layout.addWidget(settings_group)
        
        # 代理池统计
        stats_group = QGroupBox("代理统计")
        stats_layout = QGridLayout()
        
        self.total_label = QLabel("总数: 0")
        self.working_label = QLabel("可用: 0")
        self.failed_label = QLabel("失败: 0")
        self.latency_label = QLabel("平均延迟: 0ms")
        
        stats_layout.addWidget(self.total_label, 0, 0)
        stats_layout.addWidget(self.working_label, 0, 1)
        stats_layout.addWidget(self.failed_label, 1, 0)
        stats_layout.addWidget(self.latency_label, 1, 1)
        
        stats_group.setLayout(stats_layout)
        pool_layout.addWidget(stats_group)
        
        pool_tab.setLayout(pool_layout)
        self.tab_widget.addTab(pool_tab, "代理池")
        
        layout.addWidget(self.tab_widget)
        
        # 按钮
        button_layout = QHBoxLayout()
        self.test_btn = QPushButton("测试代理")
        self.save_btn = QPushButton("保存")
        self.cancel_btn = QPushButton("取消")
        
        button_layout.addWidget(self.test_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 连接信号
        self.test_btn.clicked.connect(self.test_proxy)
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        self.import_btn.clicked.connect(self.import_proxies)
        self.export_btn.clicked.connect(self.export_proxies)
        self.refresh_btn.clicked.connect(self.refresh_proxies)
        
    def on_type_changed(self, proxy_type: str):
        """代理类型改变"""
        self.proxy_type = proxy_type
        
    def on_auth_changed(self, state: int):
        """认证状态改变"""
        enabled = state == Qt.Checked
        self.auth_enabled = enabled
        self.username_edit.setEnabled(enabled)
        self.password_edit.setEnabled(enabled)
        
    def show_proxy_chain(self):
        """显示代理链配置话框"""
        dialog = ProxyChainDialog(self)
        if dialog.exec_():
            proxy = dialog.get_proxy()
            self.proxy_chain.append(proxy)
            self.update_chain_table()
            
    def update_chain_table(self):
        """更新代理链表格"""
        self.chain_table.setRowCount(len(self.proxy_chain))
        for i, proxy in enumerate(self.proxy_chain):
            self.chain_table.setItem(i, 0, QTableWidgetItem(proxy['type']))
            self.chain_table.setItem(i, 1, QTableWidgetItem(proxy['host']))
            self.chain_table.setItem(i, 2, QTableWidgetItem(str(proxy['port'])))
            auth = "是" if proxy.get('auth', {}).get('enabled') else "否"
            self.chain_table.setItem(i, 3, QTableWidgetItem(auth))
            
    def test_proxy(self):
        """测试代理连接"""
        from src.utils.proxy_tester import ProxyTester
        
        config = self.get_proxy_config()
        success, message, latency = ProxyTester.test_proxy(config)
        
        if success:
            QMessageBox.information(self, "成功",
                                  f"代理连接成功\n延迟: {latency:.2f}秒")
        else:
            QMessageBox.warning(self, "失败", f"代理连接失败\n{message}")
            
    def get_proxy_config(self) -> Dict:
        """获取代理配置"""
        config = {
            'type': self.proxy_type,
            'host': self.host_edit.text(),
            'port': int(self.port_edit.text()) if self.port_edit.text() else 0,
            'auto_switch': {
                'enabled': self.auto_switch.isChecked(),
                'interval': int(self.interval_edit.text())
            }
        }
        
        if self.auth_enabled:
            config['auth'] = {
                'enabled': True,
                'username': self.username_edit.text(),
                'password': self.password_edit.text()
            }
            
        if self.proxy_chain:
            config['chain'] = self.proxy_chain
            
        return config
        
    def import_proxies(self):
        """导入代理"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "导入代理", "", "JSON文件 (*.json)"
        )
        if filename:
            self.proxy_pool.load_from_file(filename)
            self.update_pool_table()
            
    def export_proxies(self):
        """导出代理"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "导出代理", "", "JSON文件 (*.json)"
        )
        if filename:
            self.proxy_pool.save_to_file(filename)
            
    def refresh_proxies(self):
        """刷新代理状态"""
        self.proxy_pool.refresh_proxies()
        self.update_pool_table()
        
    def update_pool_table(self):
        """更新代理池表格"""
        self.pool_table.setRowCount(len(self.proxy_pool.proxies))
        
        for i, proxy in enumerate(self.proxy_pool.proxies):
            self.pool_table.setItem(i, 0, QTableWidgetItem(proxy['type']))
            self.pool_table.setItem(i, 1, QTableWidgetItem(proxy['host']))
            self.pool_table.setItem(i, 2, QTableWidgetItem(str(proxy['port'])))
            self.pool_table.setItem(i, 3, QTableWidgetItem(f"{proxy.get('latency', 0):.2f}"))
            
            status = "可用" if proxy in self.proxy_pool.working_proxies else "失败"
            status_item = QTableWidgetItem(status)
            status_item.setForeground(
                QColor("green") if status == "可用" else QColor("red")
            )
            self.pool_table.setItem(i, 4, status_item)
            
            self.pool_table.setItem(i, 5, 
                QTableWidgetItem(str(proxy.get('fail_count', 0))))
        
        self.update_stats()
        
    def update_stats(self):
        """更新统计信息"""
        stats = self.proxy_pool.get_stats()
        self.total_label.setText(f"总数: {stats['total']}")
        self.working_label.setText(f"可用: {stats['working']}")
        self.failed_label.setText(f"失败: {stats['failed']}")
        self.latency_label.setText(f"平均延迟: {stats['avg_latency']:.2f}ms")

class ProxyChainDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加代理")
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 代理类型
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("代理类型:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["HTTP", "SOCKS4", "SOCKS5"])
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)
        
        # 代理服务器
        server_layout = QHBoxLayout()
        server_layout.addWidget(QLabel("主机:"))
        self.host_edit = QLineEdit()
        server_layout.addWidget(self.host_edit)
        server_layout.addWidget(QLabel("端口:"))
        self.port_edit = QLineEdit()
        self.port_edit.setMaximumWidth(100)
        server_layout.addWidget(self.port_edit)
        layout.addLayout(server_layout)
        
        # 代理认证
        auth_layout = QVBoxLayout()
        self.auth_check = QCheckBox("启用认证")
        auth_layout.addWidget(self.auth_check)
        
        auth_form = QHBoxLayout()
        auth_form.addWidget(QLabel("用户名:"))
        self.username_edit = QLineEdit()
        auth_form.addWidget(self.username_edit)
        auth_form.addWidget(QLabel("密码:"))
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        auth_form.addWidget(self.password_edit)
        auth_layout.addLayout(auth_form)
        
        layout.addLayout(auth_layout)
        
        # 按钮
        button_layout = QHBoxLayout()
        self.ok_btn = QPushButton("确定")
        self.cancel_btn = QPushButton("取消")
        
        button_layout.addStretch()
        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 连接信号
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        
    def get_proxy(self) -> Dict:
        """获取代理配置"""
        config = {
            'type': self.type_combo.currentText(),
            'host': self.host_edit.text(),
            'port': int(self.port_edit.text()) if self.port_edit.text() else 0
        }
        
        if self.auth_check.isChecked():
            config['auth'] = {
                'enabled': True,
                'username': self.username_edit.text(),
                'password': self.password_edit.text()
            }
            
        return config 