import os
import re

def fix_imports(file_path):
    """修复Python文件中的导入语句"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # 修复相对导入
    content = re.sub(
        r'from (core|gui|utils)\.',
        r'from src.\1.',
        content
    )
    
    # 修复直接导入
    content = re.sub(
        r'import (core|gui|utils)\.',
        r'import src.\1.',
        content
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def process_directory(directory):
    """处理目录下的所有Python文件"""
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                print(f"处理文件: {file_path}")
                fix_imports(file_path)

if __name__ == "__main__":
    # 处理src目录下的所有Python文件
    process_directory('src') 