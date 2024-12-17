import os
import json
import time
from typing import Any, Dict, Optional
import hashlib

class CacheManager:
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        self.init_cache_dir()
        
    def init_cache_dir(self):
        """初始化缓存目录"""
        os.makedirs(self.cache_dir, exist_ok=True)
        
    def _get_cache_key(self, data: Any) -> str:
        """生成缓存键"""
        if isinstance(data, dict):
            # 对字典进行排序以确保相同内容生成相同的键
            sorted_data = {k: data[k] for k in sorted(data.keys())}
            data_str = json.dumps(sorted_data, sort_keys=True)
        else:
            data_str = str(data)
            
        return hashlib.md5(data_str.encode()).hexdigest()
        
    def _get_cache_path(self, key: str) -> str:
        """获取缓存文件路径"""
        return os.path.join(self.cache_dir, f"{key}.json")
        
    def set(self, key: str, value: Any, expire: int = 3600):
        """设置缓存
        Args:
            key: 缓存键
            value: 缓存值
            expire: 过期时间(秒)
        """
        cache_data = {
            'value': value,
            'expire': time.time() + expire
        }
        
        with open(self._get_cache_path(key), 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        try:
            cache_path = self._get_cache_path(key)
            if not os.path.exists(cache_path):
                return None
                
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                
            # 检查是否过期
            if time.time() > cache_data['expire']:
                os.remove(cache_path)
                return None
                
            return cache_data['value']
            
        except Exception as e:
            print(f"读取缓存失败: {str(e)}")
            return None
            
    def delete(self, key: str):
        """删除缓存"""
        try:
            cache_path = self._get_cache_path(key)
            if os.path.exists(cache_path):
                os.remove(cache_path)
        except Exception as e:
            print(f"删除缓存失败: {str(e)}")
            
    def clear(self):
        """清空缓存"""
        try:
            for filename in os.listdir(self.cache_dir):
                file_path = os.path.join(self.cache_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        except Exception as e:
            print(f"清空缓存失败: {str(e)}")
            
    def load_cache(self, name: str) -> Optional[Dict]:
        """加载指定名称的缓存"""
        cache_path = os.path.join(self.cache_dir, f"{name}.json")
        if not os.path.exists(cache_path):
            return None
            
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载缓存失败: {str(e)}")
            return None
            
    def save_cache(self, name: str, data: Dict):
        """保存缓存"""
        cache_path = os.path.join(self.cache_dir, f"{name}.json")
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存缓存失败: {str(e)}")