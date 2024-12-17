from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                           QWidget, QLabel, QLineEdit, QCheckBox, QSpinBox,
                           QPushButton, QComboBox, QGroupBox, QFormLayout,
                           QTextEdit, QFileDialog, QListWidget)
from PyQt5.QtCore import Qt
from src.core.advanced_options import (AdvancedOptions, AuthConfig, WafConfig,
                                 EncodingConfig)

class AdvancedOptionsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("高级选项配置")
        self.resize(800, 600)
        self.options = AdvancedOptions()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 创建选项卡
        tab_widget = QTabWidget()
        
        # 认证设置选项卡
        auth_tab = self._create_auth_tab()
        tab_widget.addTab(auth_tab, "认证设置")
        
        # WAF绕过选项卡
        waf_tab = self._create_waf_tab()
        tab_widget.addTab(waf_tab, "WAF绕过")
        
        # 编码设置选项卡
        encoding_tab = self._create_encoding_tab()
        tab_widget.addTab(encoding_tab, "编码设置")
        
        # 自定义Payload选项卡
        payload_tab = self._create_payload_tab()
        tab_widget.addTab(payload_tab, "自定义Payload")
        
        layout.addWidget(tab_widget)
        
        # 按钮
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("保存")
        self.cancel_btn = QPushButton("取消")
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 连接信号
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        
    def _create_auth_tab(self) -> QWidget:
        """创建认证设置选项卡"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 认证类型
        auth_group = QGroupBox("认证设置")
        auth_layout = QFormLayout()
        
        self.auth_type = QComboBox()
        self.auth_type.addItems(["无", "Basic认证", "Digest认证", "NTLM认证", "PKI认证"])
        auth_layout.addRow("认证类型:", self.auth_type)
        
        self.username = QLineEdit()
        auth_layout.addRow("用户名:", self.username)
        
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        auth_layout.addRow("密码:", self.password)
        
        self.domain = QLineEdit()
        auth_layout.addRow("域名:", self.domain)
        
        self.cert_file = QLineEdit()
        self.cert_browse = QPushButton("浏览")
        cert_layout = QHBoxLayout()
        cert_layout.addWidget(self.cert_file)
        cert_layout.addWidget(self.cert_browse)
        auth_layout.addRow("证书文件:", cert_layout)
        
        self.key_file = QLineEdit()
        self.key_browse = QPushButton("浏览")
        key_layout = QHBoxLayout()
        key_layout.addWidget(self.key_file)
        key_layout.addWidget(self.key_browse)
        auth_layout.addRow("密钥文件:", key_layout)
        
        auth_group.setLayout(auth_layout)
        layout.addWidget(auth_group)
        
        widget.setLayout(layout)
        return widget
        
    def _create_waf_tab(self) -> QWidget:
        """创建WAF绕过选项卡"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # WAF绕过选项
        waf_group = QGroupBox("WAF/IPS绕过设置")
        waf_layout = QFormLayout()
        
        self.waf_techniques = QListWidget()
        self.waf_techniques.addItems([
            "使用注释", "随机大小写", "URL编码", "双URL编码",
            "Unicode编码", "十六进制编码", "HTML实体编码"
        ])
        self.waf_techniques.setSelectionMode(QListWidget.MultiSelection)
        waf_layout.addRow("绕过技术:", self.waf_techniques)
        
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(0, 30)
        self.delay_spin.setValue(0)
        waf_layout.addRow("请求延迟(秒):", self.delay_spin)
        
        self.retries_spin = QSpinBox()
        self.retries_spin.setRange(1, 10)
        self.retries_spin.setValue(3)
        waf_layout.addRow("重试次数:", self.retries_spin)
        
        self.random_agent = QCheckBox("使用随机User-Agent")
        waf_layout.addRow(self.random_agent)
        
        self.tamper_list = QListWidget()
        # 从tamper目录加载可用脚本
        waf_layout.addRow("Tamper脚本:", self.tamper_list)
        
        waf_group.setLayout(waf_layout)
        layout.addWidget(waf_group)
        
        widget.setLayout(layout)
        return widget
        
    def _create_encoding_tab(self) -> QWidget:
        """创建编码设置选项卡"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 编码设置
        encoding_group = QGroupBox("编码设置")
        encoding_layout = QFormLayout()
        
        self.encoding = QComboBox()
        self.encoding.addItems(["UTF-8", "GBK", "GB2312", "ISO-8859-1"])
        encoding_layout.addRow("页面编码:", self.encoding)
        
        self.param_encoding = QComboBox()
        self.param_encoding.addItems(["UTF-8", "GBK", "GB2312", "ISO-8859-1"])
        encoding_layout.addRow("参数编码:", self.param_encoding)
        
        self.payload_encoding = QComboBox()
        self.payload_encoding.addItems(["UTF-8", "GBK", "GB2312", "ISO-8859-1"])
        encoding_layout.addRow("Payload编码:", self.payload_encoding)
        
        self.skip_urlencode = QCheckBox("跳过URL编码")
        encoding_layout.addRow(self.skip_urlencode)
        
        self.skip_escape = QCheckBox("跳过特殊字符转义")
        encoding_layout.addRow(self.skip_escape)
        
        encoding_group.setLayout(encoding_layout)
        layout.addWidget(encoding_group)
        
        widget.setLayout(layout)
        return widget
        
    def _create_payload_tab(self) -> QWidget:
        """创建自定义Payload选项卡"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Payload编辑器
        payload_group = QGroupBox("自定义Payload")
        payload_layout = QVBoxLayout()
        
        self.payload_edit = QTextEdit()
        self.payload_edit.setPlaceholderText("每行一个payload")
        payload_layout.addWidget(self.payload_edit)
        
        payload_group.setLayout(payload_layout)
        layout.addWidget(payload_group)
        
        # 示例和说明
        help_text = """
        Payload示例:
        ' OR '1'='1
        ' UNION SELECT NULL--
        ' AND SLEEP(5)--
        
        支持的特殊标记:
        [RANDNUM] - 随机数
        [RANDSTR] - 随机字符串
        [ORIGINAL] - 原始值
        """
        help_label = QLabel(help_text)
        layout.addWidget(help_label)
        
        widget.setLayout(layout)
        return widget
        
    def get_options(self) -> AdvancedOptions:
        """获取配置的选项"""
        options = AdvancedOptions()
        
        # 获取认证设置
        auth_type = self.auth_type.currentText()
        if auth_type != "无":
            options.auth_config = AuthConfig(
                type=auth_type.replace("认证", "").upper(),
                username=self.username.text(),
                password=self.password.text(),
                domain=self.domain.text() if auth_type == "NTLM认证" else None,
                cert_file=self.cert_file.text() if auth_type == "PKI认证" else None,
                key_file=self.key_file.text() if auth_type == "PKI认证" else None
            )
            
        # 获取WAF绕过设置
        selected_techniques = [item.text() for item in self.waf_techniques.selectedItems()]
        selected_tampers = [item.text() for item in self.tamper_list.selectedItems()]
        if selected_techniques or selected_tampers or self.random_agent.isChecked():
            options.waf_config = WafConfig(
                techniques=selected_techniques,
                delay=self.delay_spin.value(),
                retries=self.retries_spin.value(),
                random_agent=self.random_agent.isChecked(),
                tamper_scripts=selected_tampers
            )
            
        # 获取编码设置
        if (self.encoding.currentText() != "UTF-8" or
            self.skip_urlencode.isChecked() or
            self.skip_escape.isChecked()):
            options.encoding_config = EncodingConfig(
                encoding=self.encoding.currentText(),
                param_encoding=self.param_encoding.currentText(),
                payload_encoding=self.payload_encoding.currentText(),
                skip_urlencode=self.skip_urlencode.isChecked(),
                skip_escape=self.skip_escape.isChecked()
            )
            
        # 获取自定义payload
        payloads = self.payload_edit.toPlainText().strip().split("\n")
        options.custom_payloads = [p.strip() for p in payloads if p.strip()]
        
        return options 