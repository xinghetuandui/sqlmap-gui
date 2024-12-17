import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ScanConfig:
    id: int
    name: str
    description: str
    target_config: Dict
    scan_options: Dict
    advanced_options: Optional[Dict] = None
    create_time: datetime = datetime.now()
    last_used: Optional[datetime] = None

class ConfigManager:
    def __init__(self, config_dir: str = "configs"):
        self.config_dir = config_dir
        self.templates_dir = os.path.join(config_dir, "templates")
        self.custom_dir = os.path.join(config_dir, "custom")
        self.init_dirs()
        
    def init_dirs(self):
        """初始化配置目录"""
        os.makedirs(self.templates_dir, exist_ok=True)
        os.makedirs(self.custom_dir, exist_ok=True)
        
        # 创建默认模板
        if not os.listdir(self.templates_dir):
            self.create_default_templates()
            
    def create_default_templates(self):
        """创建默认配置模板"""
        templates = [
            {
                "name": "快速扫描",
                "description": "使用基本选项进行快速扫描",
                "target_config": {
                    "method": "GET",
                    "headers": "User-Agent: Mozilla/5.0",
                },
                "scan_options": {
                    "level": 1,
                    "risk": 1,
                    "batch": True
                }
            },
            {
                "name": "深度扫描",
                "description": "使用全面的选项进行深度扫描",
                "target_config": {
                    "method": "GET",
                    "headers": "User-Agent: Mozilla/5.0",
                },
                "scan_options": {
                    "level": 5,
                    "risk": 3,
                    "threads": 5,
                    "getDbs": True,
                    "getTables": True,
                    "getColumns": True,
                    "technique": "BEUSTQ"
                }
            },
            {
                "name": "WAF绕过扫描",
                "description": "针对有WAF保护的目标的扫描配置",
                "target_config": {
                    "method": "GET",
                    "headers": "User-Agent: Mozilla/5.0",
                },
                "scan_options": {
                    "level": 3,
                    "risk": 2,
                },
                "advanced_options": {
                    "waf_config": {
                        "techniques": ["随机大小写", "URL编码", "Unicode编码"],
                        "delay": 2,
                        "retries": 3,
                        "random_agent": True
                    }
                }
            }
        ]
        
        for i, template in enumerate(templates):
            config = ScanConfig(
                id=i+1,
                name=template["name"],
                description=template["description"],
                target_config=template["target_config"],
                scan_options=template["scan_options"],
                advanced_options=template.get("advanced_options")
            )
            self.save_template(config)
            
    def save_template(self, config: ScanConfig):
        """保存配置模板"""
        filename = f"{config.id}_{config.name}.json"
        path = os.path.join(self.templates_dir, filename)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({
                'id': config.id,
                'name': config.name,
                'description': config.description,
                'target_config': config.target_config,
                'scan_options': config.scan_options,
                'advanced_options': config.advanced_options,
                'create_time': config.create_time.isoformat(),
                'last_used': config.last_used.isoformat() if config.last_used else None
            }, f, indent=2, ensure_ascii=False)
            
    def load_template(self, template_id: int) -> Optional[ScanConfig]:
        """加载配置模板"""
        for filename in os.listdir(self.templates_dir):
            if filename.startswith(f"{template_id}_"):
                path = os.path.join(self.templates_dir, filename)
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return ScanConfig(
                        id=data['id'],
                        name=data['name'],
                        description=data['description'],
                        target_config=data['target_config'],
                        scan_options=data['scan_options'],
                        advanced_options=data.get('advanced_options'),
                        create_time=datetime.fromisoformat(data['create_time']),
                        last_used=datetime.fromisoformat(data['last_used']) if data['last_used'] else None
                    )
        return None
        
    def get_all_templates(self) -> List[ScanConfig]:
        """获取所有配置模板"""
        templates = []
        for filename in os.listdir(self.templates_dir):
            if filename.endswith('.json'):
                path = os.path.join(self.templates_dir, filename)
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    templates.append(ScanConfig(
                        id=data['id'],
                        name=data['name'],
                        description=data['description'],
                        target_config=data['target_config'],
                        scan_options=data['scan_options'],
                        advanced_options=data.get('advanced_options'),
                        create_time=datetime.fromisoformat(data['create_time']),
                        last_used=datetime.fromisoformat(data['last_used']) if data['last_used'] else None
                    ))
        return templates
        
    def save_custom_config(self, config: Dict, name: str):
        """保存自定义配置"""
        filename = f"{name}.json"
        path = os.path.join(self.custom_dir, filename)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
            
    def load_custom_config(self, name: str) -> Optional[Dict]:
        """加载自定义配置"""
        path = os.path.join(self.custom_dir, f"{name}.json")
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
        
    def export_config(self, config: ScanConfig, filepath: str):
        """导出配置"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'name': config.name,
                'description': config.description,
                'target_config': config.target_config,
                'scan_options': config.scan_options,
                'advanced_options': config.advanced_options
            }, f, indent=2, ensure_ascii=False)
            
    def import_config(self, filepath: str) -> ScanConfig:
        """导入配置"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return ScanConfig(
                id=len(self.get_all_templates()) + 1,
                name=data['name'],
                description=data['description'],
                target_config=data['target_config'],
                scan_options=data['scan_options'],
                advanced_options=data.get('advanced_options')
            ) 

    def delete_template(self, template_id: int):
        """删除模板"""
        for filename in os.listdir(self.templates_dir):
            if filename.startswith(f"{template_id}_"):
                os.remove(os.path.join(self.templates_dir, filename))
                return
        raise FileNotFoundError(f"模板 ID {template_id} 不存在")

    def get_template_history(self, template_id: int) -> List[Dict]:
        """获取模板使用历史"""
        history_file = os.path.join(self.config_dir, "history.json")
        if not os.path.exists(history_file):
            return []
        
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
            return history.get(str(template_id), [])

    def add_template_history(self, template_id: int, scan_result: Dict):
        """添加模板使用历史"""
        history_file = os.path.join(self.config_dir, "history.json")
        history = {}
        
        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
                
        template_history = history.get(str(template_id), [])
        template_history.append({
            'time': datetime.now().isoformat(),
            'result': scan_result
        })
        
        # 只保留最近的10条记录
        if len(template_history) > 10:
            template_history = template_history[-10:]
            
        history[str(template_id)] = template_history
        
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False) 