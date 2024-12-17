import os
import shutil
from typing import List, Dict
import importlib.util
import sys

class TamperManager:
    def __init__(self, sqlmap_path: str = None):
        # 默认 sqlmap tamper 脚本目录
        self.sqlmap_path = sqlmap_path or os.path.expanduser("~/.sqlmap")
        self.tamper_dir = os.path.join(self.sqlmap_path, "tamper")
        
        # 用户自定义 tamper 脚本目录
        self.user_tamper_dir = os.path.expanduser("~/.sqlmap/tamper-custom")
        os.makedirs(self.user_tamper_dir, exist_ok=True)
        
    def get_available_tampers(self) -> List[Dict]:
        """获取所有可用的 tamper 脚本"""
        tampers = []
        
        # 获取系统 tamper 脚本
        if os.path.exists(self.tamper_dir):
            tampers.extend(self._scan_tamper_dir(self.tamper_dir, is_system=True))
            
        # 获取用户自定义 tamper 脚本
        if os.path.exists(self.user_tamper_dir):
            tampers.extend(self._scan_tamper_dir(self.user_tamper_dir, is_system=False))
            
        return tampers
        
    def _scan_tamper_dir(self, directory: str, is_system: bool) -> List[Dict]:
        """扫描指定目录下的 tamper 脚本"""
        tampers = []
        
        for file in os.listdir(directory):
            if file.endswith('.py') and not file.startswith('__'):
                tamper_path = os.path.join(directory, file)
                try:
                    info = self._get_tamper_info(tamper_path)
                    info.update({
                        'name': os.path.splitext(file)[0],
                        'path': tamper_path,
                        'is_system': is_system
                    })
                    tampers.append(info)
                except Exception as e:
                    print(f"加载tamper脚本出错 {file}: {str(e)}")
                    
        return tampers
        
    def _get_tamper_info(self, tamper_path: str) -> Dict:
        """获取 tamper 脚本的信息"""
        spec = importlib.util.spec_from_file_location("tamper_module", tamper_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules["tamper_module"] = module
        spec.loader.exec_module(module)
        
        return {
            'description': getattr(module, '__doc__', '').strip() or '无描述',
            'dependencies': getattr(module, 'dependencies', []),
            'author': getattr(module, '__author__', '未��')
        }
        
    def create_tamper(self, name: str, content: str) -> str:
        """创建新的 tamper 脚本"""
        if not name.endswith('.py'):
            name += '.py'
            
        file_path = os.path.join(self.user_tamper_dir, name)
        
        if os.path.exists(file_path):
            raise FileExistsError(f"Tamper脚本 {name} 已存在")
            
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return file_path
        
    def edit_tamper(self, name: str, content: str):
        """编辑现有的 tamper 脚本"""
        if not name.endswith('.py'):
            name += '.py'
            
        file_path = os.path.join(self.user_tamper_dir, name)
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Tamper脚本 {name} 不存在")
            
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
    def delete_tamper(self, name: str):
        """删除 tamper 脚本"""
        if not name.endswith('.py'):
            name += '.py'
            
        file_path = os.path.join(self.user_tamper_dir, name)
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Tamper脚本 {name} 不���在")
            
        os.remove(file_path)
        
    def get_tamper_template(self) -> str:
        """获取 tamper 脚本模板"""
        return '''#!/usr/bin/env python

"""
Description: 自定义 tamper 脚本
Author: 您的名字
"""

from lib.core.enums import PRIORITY

__priority__ = PRIORITY.NORMAL

def dependencies():
    pass

def tamper(payload):
    """
    修改 SQL 注入 payload
    """
    # TODO: 在这里实现您的 tamper 逻辑
    return payload
''' 