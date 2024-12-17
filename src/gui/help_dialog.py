from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QTabWidget, QWidget,
                           QPushButton, QTextBrowser)
from PyQt5.QtCore import Qt

class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("使用帮助")
        self.resize(800, 600)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 创建选项卡
        tab_widget = QTabWidget()
        
        # 快速入门
        quick_start_tab = self._create_quick_start_tab()
        tab_widget.addTab(quick_start_tab, "快速入门")
        
        # 功能说明
        features_tab = self._create_features_tab()
        tab_widget.addTab(features_tab, "功能说明")
        
        # 常见问题
        faq_tab = self._create_faq_tab()
        tab_widget.addTab(faq_tab, "常见问题")
        
        layout.addWidget(tab_widget)
        
        # 确定按钮
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept)
        layout.addWidget(ok_btn)
        
        self.setLayout(layout)
        
    def _create_quick_start_tab(self) -> QWidget:
        """创建快速入门选项卡"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        text = QTextBrowser()
        text.setOpenExternalLinks(True)
        text.setHtml("""
        <h2>快速入门</h2>
        
        <h3>1. 配置目标</h3>
        <p>点击"配置目标"按钮或使用菜单"文件->新建扫描"来配置扫描目标。您可以：</p>
        <ul>
            <li>输入单个URL进行扫描</li>
            <li>导入多个目标进行批量扫描</li>
            <li>配置HTTP方法、Headers和Cookie等参数</li>
        </ul>
        
        <h3>2. 开始扫描</h3>
        <p>配置完目标后，点击"开始扫描"按钮开始扫描。扫描过程中您可以：</p>
        <ul>
            <li>查看实时扫描日志</li>
            <li>监控扫描进度</li>
            <li>随时暂停或停止扫描</li>
        </ul>
        
        <h3>3. 查看结果</h3>
        <p>扫描完成后，您可以：</p>
        <ul>
            <li>查看详细的扫描结果</li>
            <li>分析漏洞风险</li>
            <li>导出扫描报告</li>
        </ul>
        """)
        layout.addWidget(text)
        
        widget.setLayout(layout)
        return widget
        
    def _create_features_tab(self) -> QWidget:
        """创建功能说明选项卡"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        text = QTextBrowser()
        text.setOpenExternalLinks(True)
        text.setHtml("""
        <h2>功能说明</h2>
        
        <h3>扫描功能</h3>
        <ul>
            <li>单一目标扫描</li>
            <li>批量目标扫描</li>
            <li>自定义扫描参数</li>
            <li>扫描任务管理</li>
        </ul>
        
        <h3>代理功能</h3>
        <ul>
            <li>HTTP/HTTPS代理支持</li>
            <li>SOCKS代理支持</li>
            <li>代理认证</li>
            <li>代理链支持</li>
        </ul>
        
        <h3>编码工具</h3>
        <ul>
            <li>URL编码/解码</li>
            <li>Base64编码/解码</li>
            <li>HTML编码/解码</li>
            <li>Unicode编码/解码</li>
        </ul>
        
        <h3>性能监控</h3>
        <ul>
            <li>CPU使用监控</li>
            <li>内存使用监控</li>
            <li>响应时间监控</li>
            <li>自动性能优化</li>
        </ul>
        """)
        layout.addWidget(text)
        
        widget.setLayout(layout)
        return widget
        
    def _create_faq_tab(self) -> QWidget:
        """创建常见问题选项卡"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        text = QTextBrowser()
        text.setOpenExternalLinks(True)
        text.setHtml("""
        <h2>常见问题</h2>
        
        <h3>Q: 如何配置代理？</h3>
        <p>A: 在工具菜单中选择"代理设置"，可以配置HTTP/HTTPS代理或SOCKS代理。支持代理认证和代理链。</p>
        
        <h3>Q: 如何进行批量扫描？</h3>
        <p>A: 在目标配置对话框中切换到"批量目标"选项卡，可以导入TXT/CSV/JSON格式的目标列表。</p>
        
        <h3>Q: 如何自定义扫描参数？</h3>
        <p>A: 在扫描菜单中选择"高级设置"，可以配置详细的扫描参数，如测试级别、风险等级等。</p>
        
        <h3>Q: 如何导出扫描报告？</h3>
        <p>A: 在扫描完成后，可以通过"文件->保存结果"导出扫描报告，支持多种格式。</p>
        
        <h3>Q: 遇到问题如何反馈？</h3>
        <p>A: 您可以通过以下方式反馈问题：</p>
        <ul>
            <li>GitHub Issues</li>
            <li>发送邮件到支持邮箱</li>
            <li>在官方论坛发帖</li>
        </ul>
        """)
        layout.addWidget(text)
        
        widget.setLayout(layout)
        return widget 