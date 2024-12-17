import os
import json
import shutil
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import hashlib

@dataclass
class ConfigVersion:
    version_id: str
    config_id: str
    content: Dict
    create_time: datetime
    comment: str
    author: str

class ConfigVersionManager:
    def __init__(self, version_dir: str = "configs/versions"):
        self.version_dir = version_dir
        os.makedirs(version_dir, exist_ok=True)
        
    def create_version(self, config_id: str, content: Dict, 
                      comment: str = "", author: str = "") -> ConfigVersion:
        """创建新版本"""
        # 生成版本ID
        version_id = self._generate_version_id(content)
        version = ConfigVersion(
            version_id=version_id,
            config_id=config_id,
            content=content,
            create_time=datetime.now(),
            comment=comment,
            author=author
        )
        
        # 保存版本
        self._save_version(version)
        return version
        
    def get_versions(self, config_id: str) -> List[ConfigVersion]:
        """获取配置的所有版本"""
        versions = []
        version_path = os.path.join(self.version_dir, config_id)
        if not os.path.exists(version_path):
            return versions
            
        for filename in os.listdir(version_path):
            if filename.endswith('.json'):
                with open(os.path.join(version_path, filename), 'r') as f:
                    data = json.load(f)
                    versions.append(ConfigVersion(
                        version_id=data['version_id'],
                        config_id=data['config_id'],
                        content=data['content'],
                        create_time=datetime.fromisoformat(data['create_time']),
                        comment=data['comment'],
                        author=data['author']
                    ))
                    
        # 按时间排序
        versions.sort(key=lambda x: x.create_time, reverse=True)
        return versions
        
    def get_version(self, config_id: str, version_id: str) -> Optional[ConfigVersion]:
        """获取特定版本"""
        version_file = os.path.join(self.version_dir, config_id, f"{version_id}.json")
        if not os.path.exists(version_file):
            return None
            
        with open(version_file, 'r') as f:
            data = json.load(f)
            return ConfigVersion(
                version_id=data['version_id'],
                config_id=data['config_id'],
                content=data['content'],
                create_time=datetime.fromisoformat(data['create_time']),
                comment=data['comment'],
                author=data['author']
            )
            
    def _generate_version_id(self, content: Dict) -> str:
        """生成版本ID"""
        content_str = json.dumps(content, sort_keys=True)
        return hashlib.sha1(content_str.encode()).hexdigest()[:8]
        
    def _save_version(self, version: ConfigVersion):
        """保存版本"""
        version_path = os.path.join(self.version_dir, version.config_id)
        os.makedirs(version_path, exist_ok=True)
        
        version_file = os.path.join(version_path, f"{version.version_id}.json")
        with open(version_file, 'w') as f:
            json.dump({
                'version_id': version.version_id,
                'config_id': version.config_id,
                'content': version.content,
                'create_time': version.create_time.isoformat(),
                'comment': version.comment,
                'author': version.author
            }, f, indent=2) 