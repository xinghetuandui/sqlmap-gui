from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextEdit,
                           QPushButton, QLabel, QSplitter, QWidget, QComboBox)
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt5.QtCore import Qt
import re
import sqlparse

class SQLHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # SQL关键字
        self.keywords = [
            'SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE',
            'DROP', 'CREATE', 'TABLE', 'DATABASE', 'ALTER', 'INDEX',
            'AND', 'OR', 'NOT', 'IN', 'LIKE', 'UNION', 'GROUP BY',
            'ORDER BY', 'HAVING', 'JOIN', 'LEFT', 'RIGHT', 'INNER',
            'VALUES', 'SET', 'INTO', 'LIMIT', 'OFFSET', 'AS', 'ON',
            'DISTINCT', 'COUNT', 'SUM', 'AVG', 'MAX', 'MIN', 'CASE',
            'WHEN', 'THEN', 'ELSE', 'END', 'NULL', 'IS', 'TRUE', 'FALSE'
        ]
        
        # 高亮规则
        self.rules = []
        
        # 关键字规则
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#0033CC"))  # 深蓝���
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
        comment_format.setFontItalic(True)
        self.rules.append((re.compile(r'--[^\n]*'), comment_format))
        self.rules.append((re.compile(r'/\*.*?\*/', re.DOTALL),
                          comment_format))
                          
        # 数字规则
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#CC0000"))  # 红色
        self.rules.append((re.compile(r'\b\d+\b'), number_format))
        
        # 函数规则
        function_format = QTextCharFormat()
        function_format.setForeground(QColor("#6600CC"))  # 紫色
        self.rules.append((re.compile(r'\b\w+(?=\s*\()'), function_format))
        
        # 括号规则
        bracket_format = QTextCharFormat()
        bracket_format.setForeground(QColor("#000000"))  # 黑色
        bracket_format.setFontWeight(QFont.Bold)
        self.rules.append((re.compile(r'[\(\)]'), bracket_format))
        
    def highlightBlock(self, text):
        """高亮文本块"""
        for pattern, format in self.rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(),
                             format)

class SQLDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SQL编辑器")
        self.resize(1000, 700)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 工具栏
        toolbar = QHBoxLayout()
        
        # 格式化选项
        self.format_combo = QComboBox()
        self.format_combo.addItems(["标准格式", "紧凑格式"])
        toolbar.addWidget(QLabel("格式化风格:"))
        toolbar.addWidget(self.format_combo)
        
        # 大小写选项
        self.case_combo = QComboBox()
        self.case_combo.addItems(["保持原样", "全部大写", "全部小写"])
        toolbar.addWidget(QLabel("关键字大小写:"))
        toolbar.addWidget(self.case_combo)
        
        toolbar.addStretch()
        
        # 按钮
        self.format_btn = QPushButton("格式化")
        self.copy_btn = QPushButton("复制")
        self.clear_btn = QPushButton("清除")
        
        toolbar.addWidget(self.format_btn)
        toolbar.addWidget(self.copy_btn)
        toolbar.addWidget(self.clear_btn)
        
        layout.addLayout(toolbar)
        
        # 创建分割器
        splitter = QSplitter(Qt.Vertical)
        
        # SQL编辑区
        self.sql_edit = QTextEdit()
        self.sql_edit.setFont(QFont("Consolas", 12))
        self.sql_edit.setPlaceholderText("在此输入SQL语句...")
        self.highlighter = SQLHighlighter(self.sql_edit.document())
        splitter.addWidget(self.sql_edit)
        
        # 格式化预览区
        self.preview_edit = QTextEdit()
        self.preview_edit.setFont(QFont("Consolas", 12))
        self.preview_edit.setReadOnly(True)
        self.preview_highlighter = SQLHighlighter(self.preview_edit.document())
        splitter.addWidget(self.preview_edit)
        
        layout.addWidget(splitter)
        
        self.setLayout(layout)
        
        # 连接信号
        self.format_btn.clicked.connect(self.format_sql)
        self.copy_btn.clicked.connect(self.copy_formatted)
        self.clear_btn.clicked.connect(self.clear_all)
        
    def format_sql(self):
        """格式化SQL"""
        sql = self.sql_edit.toPlainText().strip()
        if not sql:
            return
            
        try:
            # 格式化选项
            if self.format_combo.currentText() == "标准格式":
                formatted_sql = sqlparse.format(
                    sql,
                    reindent=True,
                    indent_width=4,
                    keyword_case=self._get_case_style(),
                    identifier_case=self._get_case_style(),
                    use_space_around_operators=True,
                    comma_first=False
                )
            else:
                formatted_sql = sqlparse.format(
                    sql,
                    reindent=False,
                    keyword_case=self._get_case_style(),
                    identifier_case=self._get_case_style(),
                    use_space_around_operators=False,
                    comma_first=False
                )
                
            self.preview_edit.setText(formatted_sql)
            
        except Exception as e:
            self.preview_edit.setText(f"格式化错误: {str(e)}")
            
    def _get_case_style(self) -> str:
        """获取大小写风格"""
        case_style = self.case_combo.currentText()
        if case_style == "全部大写":
            return "upper"
        elif case_style == "全部小写":
            return "lower"
        return None
        
    def copy_formatted(self):
        """复制格式化后的SQL"""
        formatted_sql = self.preview_edit.toPlainText()
        if formatted_sql:
            clipboard = QApplication.clipboard()
            clipboard.setText(formatted_sql)
            
    def clear_all(self):
        """清除所有内容"""
        self.sql_edit.clear()
        self.preview_edit.clear() 