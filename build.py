import os
import shutil
import subprocess
from pathlib import Path

def clean_build():
    """清理构建目录"""
    dirs_to_clean = ['build', 'dist', '__pycache__', '*.egg-info']
    for dir_name in dirs_to_clean:
        for path in Path('.').rglob(dir_name):
            if path.is_dir():
                shutil.rmtree(path)
            elif path.is_file():
                path.unlink()

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
    sqlmap_dir = Path('sqlmap')
    if not sqlmap_dir.exists():
        print("错误: 未找到SQLMap目录")
        return False
    return True

def build_app():
    """构建应用程序"""
    try:
        # 清理旧的构建文件
        clean_build()
        
        # 检查环境
        if not check_dependencies():
            return False
        if not check_sqlmap():
            return False
            
        # 创建必要的目录
        os.makedirs('dist', exist_ok=True)
        os.makedirs('build', exist_ok=True)
        
        # 运行PyInstaller
        subprocess.run([
            'pyinstaller',
            '--clean',
            '--noconfirm',
            'sqlmap_gui.spec'
        ], check=True)
        
        # 复制配置文件
        shutil.copytree('configs', 'dist/SQLMap GUI/configs', dirs_exist_ok=True)
        
        # 复制SQLMap
        shutil.copytree('sqlmap', 'dist/SQLMap GUI/sqlmap', dirs_exist_ok=True)
        
        print("构建完成!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"构建失败: {str(e)}")
        return False
    except Exception as e:
        print(f"错误: {str(e)}")
        return False

if __name__ == "__main__":
    build_app() 