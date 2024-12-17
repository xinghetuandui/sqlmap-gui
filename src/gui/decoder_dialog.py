from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, 
                           QPushButton, QComboBox, QLabel, QWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from src.utils.http_decoder import HTTPDecoder
from src.utils.binary_decoder import BinaryDecoder

class DecoderDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("编码/解码工具")
        self.resize(800, 600)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 编码类型选择
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("编码类型:"))
        self.decoder_type = QComboBox()
        self.decoder_type.addItems([
            "URL编码", "URL编码(+空格)", 
            "HTML编码", "HTML编码(不含引号)",
            "Unicode编码", "Unicode编码(%u)",
            "Base64编码",
            "十六进制编码",
            "JSON格式化",
            "JWT解码",
            "MD5哈希",
            "SHA1哈希",
            "SHA256哈希",
            "SHA512哈希",
            "Gzip压缩"
        ])
        type_layout.addWidget(self.decoder_type)
        layout.addLayout(type_layout)
        
        # 输入区域
        layout.addWidget(QLabel("输入:"))
        self.input_text = QTextEdit()
        self.input_text.setFont(QFont("Courier New", 10))
        layout.addWidget(self.input_text)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        self.encode_button = QPushButton("编码")
        self.decode_button = QPushButton("解码")
        button_layout.addWidget(self.encode_button)
        button_layout.addWidget(self.decode_button)
        layout.addLayout(button_layout)
        
        # 输出区域
        layout.addWidget(QLabel("输出:"))
        self.output_text = QTextEdit()
        self.output_text.setFont(QFont("Courier New", 10))
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)
        
        self.setLayout(layout)
        
        # 连接信号
        self.connect_signals()
        
    def connect_signals(self):
        self.encode_button.clicked.connect(self.encode_text)
        self.decode_button.clicked.connect(self.decode_text)
        
    def encode_text(self):
        """编码文本"""
        text = self.input_text.toPlainText()
        decoder_type = self.decoder_type.currentText()
        
        if decoder_type == "URL编码":
            result = HTTPDecoder.url_encode(text)
        elif decoder_type == "URL编码(+空格)":
            result = HTTPDecoder.url_encode(text, plus_space=True)
        elif decoder_type == "HTML编码":
            result = HTTPDecoder.html_encode(text)
        elif decoder_type == "HTML编码(不含引号)":
            result = HTTPDecoder.html_encode(text, quote=False)
        elif decoder_type == "Unicode编码":
            result = HTTPDecoder.unicode_encode(text)
        elif decoder_type == "Unicode编码(%u)":
            result = HTTPDecoder.unicode_encode(text, prefix="%u")
        elif decoder_type == "Base64编码":
            result = BinaryDecoder.base64_encode(text)
        elif decoder_type == "十六进制编码":
            result = BinaryDecoder.hex_encode(text)
        elif decoder_type == "JSON格式化":
            result = HTTPDecoder.json_encode(text)
        elif decoder_type == "MD5哈希":
            result = BinaryDecoder.hash_encode(text, 'md5')
        elif decoder_type == "SHA1哈希":
            result = BinaryDecoder.hash_encode(text, 'sha1')
        elif decoder_type == "SHA256哈希":
            result = BinaryDecoder.hash_encode(text, 'sha256')
        elif decoder_type == "SHA512哈希":
            result = BinaryDecoder.hash_encode(text, 'sha512')
        elif decoder_type == "Gzip压缩":
            result = BinaryDecoder.gzip_encode(text)
            
        self.output_text.setText(result)
        
    def decode_text(self):
        """解码文本"""
        text = self.input_text.toPlainText()
        decoder_type = self.decoder_type.currentText()
        
        if decoder_type == "URL编码" or decoder_type == "URL编码(+空格)":
            result = HTTPDecoder.url_decode(text, '+空格' in decoder_type)
        elif decoder_type == "HTML编码" or decoder_type == "HTML编码(不含引号)":
            result = HTTPDecoder.html_decode(text)
        elif decoder_type == "Unicode编码" or decoder_type == "Unicode编码(%u)":
            result = HTTPDecoder.unicode_decode(text)
        elif decoder_type == "Base64编码":
            result = BinaryDecoder.base64_decode(text)
        elif decoder_type == "十六进制编码":
            result = BinaryDecoder.hex_decode(text)
        elif decoder_type == "JSON格式化":
            result = HTTPDecoder.json_encode(text)
        elif decoder_type == "JWT解码":
            result = HTTPDecoder.jwt_decode(text)
        elif decoder_type == "Gzip压缩":
            result = BinaryDecoder.gzip_decode(text)
        else:
            result = "此编码类型不支持解码"
            
        self.output_text.setText(result) 