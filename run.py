#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
from pathlib import Path

def init_logging():
    """初始化日志"""
    os.makedirs('logs', exist_ok=True)
    logging.basicConfig(
        filename='logs/sqlmap_gui.log',
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def init_directories():
    """初始化目录"""
    dirs = ['cache', 'configs', 'sqlmap_results']
    for dir_name in dirs:
        os.makedirs(dir_name, exist_ok=True)

def check_dependencies():
    """检查依赖"""
    try:
        import PyQt5
        import requests
        import psutil
        return True
    except ImportError as e:
        print(f"缺少依赖: {e}")
        return False

def check_sqlmap():
    """检查SQLMap"""
    if not os.path.exists('sqlmap'):
        print("错误: 未找到SQLMap目录")
        return False
    return True

def main():
    """主函数"""
    try:
        # 初始化
        init_logging()
        init_directories()
        
        # 检查环境
        if not check_dependencies():
            sys.exit(1)
        if not check_sqlmap():
            sys.exit(1)
            
        # 启动应用
        from PyQt5.QtWidgets import QApplication
        from src.main import MainWindow
        
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
        
    except Exception as e:
        logging.error(f"启动失败: {str(e)}", exc_info=True)
        print(f"启动失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 