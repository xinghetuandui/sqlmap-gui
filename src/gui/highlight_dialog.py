from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextEdit,
                           QPushButton, QLabel)
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt5.QtCore import Qt
import re

class SQLHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 关键字
        self.keywords = [
            'SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE',
            'DROP', 'CREATE', 'TABLE', 'DATABASE', 'ALTER', 'INDEX',
            'AND', 'OR', 'NOT', 'IN', 'LIKE', 'UNION', 'GROUP BY',
            'ORDER BY', 'HAVING', 'JOIN', 'LEFT', 'RIGHT', 'INNER'
        ]
        
        # 高亮规则
        self.rules = []
        
        # 关键字规则
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#0000FF"))  # 蓝色
        keyword_format.setFontWeight(QFont.Bold)
        
        for word in self.keywords:
            pattern = rf'\b{word}\b'
            self.rules.append((re.compile(pattern, re.IGNORECASE),
                             keyword_format))
                             
        # 字符串规则
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#008000"))  # 绿色
        self.rules.append((re.compile(r'"[^"]*"'), string_format))
        self.rules.append((re.compile(r"'[^']*'"), string_format))
        
        # 注释规则
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#808080"))  # 灰色
        self.rules.append((re.compile(r'--[^\n]*'), comment_format))
        self.rules.append((re.compile(r'/\*.*?\*/', re.DOTALL),
                          comment_format))
                          
        # 数字规则
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#FF0000"))  # 红色
        self.rules.append((re.compile(r'\b\d+\b'), number_format))
        
    def highlightBlock(self, text):
        """高亮文本块"""
        for pattern, format in self.rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(),
                             format)

class HighlightDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SQL语法高亮")
        self.resize(800, 600)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # SQL编辑器
        self.sql_edit = QTextEdit()
        self.sql_edit.setFont(QFont("Consolas", 12))
        self.highlighter = SQLHighlighter(self.sql_edit.document())
        layout.addWidget(self.sql_edit)
        
        # 按钮
        button_layout = QHBoxLayout()
        self.format_btn = QPushButton("格式化")
        self.clear_btn = QPushButton("清除")
        self.close_btn = QPushButton("关闭")
        
        button_layout.addWidget(self.format_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 连接信号
        self.format_btn.clicked.connect(self.format_sql)
        self.clear_btn.clicked.connect(self.sql_edit.clear)
        self.close_btn.clicked.connect(self.close)
        
    def format_sql(self):
        """格式化SQL"""
        try:
            from sqlparse import format
            sql = self.sql_edit.toPlainText()
            formatted_sql = format(sql,
                                 reindent=True,
                                 keyword_case='upper')
            self.sql_edit.setText(formatted_sql)
        except ImportError:
            self.sql_edit.append("\n# 请安装sqlparse包以支持格式化功能") 