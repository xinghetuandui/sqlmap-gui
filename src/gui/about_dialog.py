from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, 
                           QTextBrowser)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("关于")
        self.resize(400, 300)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 版本信息
        version_label = QLabel("SQLMap GUI v1.0.0 - 零漏安全出品")
        version_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        version_label.setFont(font)
        layout.addWidget(version_label)
        
        # 简介
        desc_text = QTextBrowser()
        desc_text.setOpenExternalLinks(True)
        desc_text.setHtml("""
        <p style='text-align: center;'>
            SQLMap GUI是一个基于SQLMap的图形化SQL注入工具，<br>
            提供了直观的界面和丰富的功能，帮助用户更方便地进行SQL注入测试。
        </p>
        
        <h3>版权声明</h3>
        <p>Copyright © 2024 零漏安全. All rights reserved.</p>
        <p>本软件基于 GNU General Public License v3.0 开源协议发布。</p>
        
        <h3>开发者</h3>
        <p>无垢 (hanyan711@qq.com)</p>
        <p>公众号：零漏安全</p>
        
        <h3>免责声明</h3>
        <p>本软件仅供安全测试使用，请勿用于非法用途。<br>
        使用本软件造成的任何后果由使用者自行承担。</p>
        """)
        layout.addWidget(desc_text)
        
        # 确定按钮
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept)
        layout.addWidget(ok_btn)
        
        self.setLayout(layout) 