import os
import json
import shutil
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import xml.etree.ElementTree as ET
from src.core.config_version_manager import ConfigVersionManager
from src.core.config_validator import ConfigValidator

@dataclass
class ConfigTemplate:
    name: str
    description: str
    category: str  # 如：常用、自定义、团队共享等
    target_config: Dict
    scan_options: Dict
    advanced_options: Optional[Dict] = None
    create_time: datetime = datetime.now()
    last_used: Optional[datetime] = None
    tags: List[str] = None
    author: str = ""
    version: str = "1.0"

class ConfigTemplateManager:
    def __init__(self, config_dir: str = "configs"):
        self.config_dir = config_dir
        self.templates_dir = os.path.join(config_dir, "templates")
        self.quick_configs_dir = os.path.join(config_dir, "quick_configs")
        self.version_manager = ConfigVersionManager()
        self.validator = ConfigValidator()
        self.init_dirs()
        
    def init_dirs(self):
        """初始化配置目录"""
        os.makedirs(self.templates_dir, exist_ok=True)
        os.makedirs(self.quick_configs_dir, exist_ok=True)
        
        # 创建默认快捷配置
        if not os.listdir(self.quick_configs_dir):
            self.create_default_quick_configs()
            
    def create_default_quick_configs(self):
        """创建默认快捷配置"""
        quick_configs = [
            {
                "name": "快速扫描",
                "description": "基本的SQL注入检测",
                "category": "常用",
                "target_config": {
                    "method": "GET",
                    "headers": {"User-Agent": "Mozilla/5.0"}
                },
                "scan_options": {
                    "level": 1,
                    "risk": 1,
                    "batch": True
                },
                "tags": ["快速", "基本"]
            },
            {
                "name": "完整扫描",
                "description": "全面的SQL注入漏洞检测",
                "category": "常用",
                "target_config": {
                    "method": "GET",
                    "headers": {"User-Agent": "Mozilla/5.0"}
                },
                "scan_options": {
                    "level": 5,
                    "risk": 2,
                    "getDbs": True,
                    "getTables": True,
                    "getColumns": True
                },
                "tags": ["完整", "深度"]
            }
        ]
        
        for config in quick_configs:
            template = ConfigTemplate(**config)
            self.save_quick_config(template)
            
    def save_template(self, template: ConfigTemplate) -> str:
        """保存配置模板"""
        # 验证配置
        valid, errors = self.validator.validate_template({
            'name': template.name,
            'description': template.description,
            'target_config': template.target_config,
            'scan_options': template.scan_options,
            'advanced_options': template.advanced_options
        })
        
        if not valid:
            raise ValueError("\n".join(errors))
            
        # 创建新版本
        version = self.version_manager.create_version(
            config_id=template.name,
            content={
                'target_config': template.target_config,
                'scan_options': template.scan_options,
                'advanced_options': template.advanced_options
            },
            comment="保存模板",
            author=template.author
        )
        
        # 保存模板文件
        path = super().save_template(template)
        return path
        
    def load_template(self, filename: str) -> Optional[ConfigTemplate]:
        """加载配置模板"""
        path = os.path.join(self.templates_dir, filename)
        if not os.path.exists(path):
            return None
            
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data['create_time'] = datetime.fromisoformat(data['create_time'])
            if data.get('last_used'):
                data['last_used'] = datetime.fromisoformat(data['last_used'])
            return ConfigTemplate(**data)
            
    def get_all_templates(self) -> List[ConfigTemplate]:
        """获取所有配置模板"""
        templates = []
        for filename in os.listdir(self.templates_dir):
            if filename.endswith('.json'):
                template = self.load_template(filename)
                if template:
                    templates.append(template)
        return templates
        
    def save_quick_config(self, config: ConfigTemplate):
        """保存快捷配置"""
        filename = f"{config.name}.json"
        path = os.path.join(self.quick_configs_dir, filename)
        
        config_data = asdict(config)
        config_data['create_time'] = config.create_time.isoformat()
        if config.last_used:
            config_data['last_used'] = config.last_used.isoformat()
            
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
            
    def get_quick_configs(self) -> List[ConfigTemplate]:
        """获取所有快捷配置"""
        configs = []
        for filename in os.listdir(self.quick_configs_dir):
            if filename.endswith('.json'):
                path = os.path.join(self.quick_configs_dir, filename)
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['create_time'] = datetime.fromisoformat(data['create_time'])
                    if data.get('last_used'):
                        data['last_used'] = datetime.fromisoformat(data['last_used'])
                    configs.append(ConfigTemplate(**data))
        return configs
        
    def export_template(self, template: ConfigTemplate, filepath: str, format: str = 'json'):
        """导出配置模板
        Args:
            template: 要导出的模板
            filepath: 导出文件路径
            format: 导出格式（json/xml）
        """
        if format == 'json':
            self._export_json(template, filepath)
        elif format == 'xml':
            self._export_xml(template, filepath)
        else:
            raise ValueError(f"不支持的导出格式: {format}")
            
    def _export_json(self, template: ConfigTemplate, filepath: str):
        """导出为JSON格式"""
        template_data = asdict(template)
        template_data['create_time'] = template.create_time.isoformat()
        if template.last_used:
            template_data['last_used'] = template.last_used.isoformat()
            
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(template_data, f, indent=2, ensure_ascii=False)
            
    def _export_xml(self, template: ConfigTemplate, filepath: str):
        """导出为XML格式"""
        root = ET.Element("config_template")
        
        # 基本信息
        basic_info = ET.SubElement(root, "basic_info")
        ET.SubElement(basic_info, "name").text = template.name
        ET.SubElement(basic_info, "description").text = template.description
        ET.SubElement(basic_info, "category").text = template.category
        ET.SubElement(basic_info, "create_time").text = template.create_time.isoformat()
        if template.last_used:
            ET.SubElement(basic_info, "last_used").text = template.last_used.isoformat()
            
        # 目标配置
        target_config = ET.SubElement(root, "target_config")
        for key, value in template.target_config.items():
            ET.SubElement(target_config, key).text = str(value)
            
        # 扫描选项
        scan_options = ET.SubElement(root, "scan_options")
        for key, value in template.scan_options.items():
            ET.SubElement(scan_options, key).text = str(value)
            
        # 高级选项
        if template.advanced_options:
            advanced_options = ET.SubElement(root, "advanced_options")
            for key, value in template.advanced_options.items():
                ET.SubElement(advanced_options, key).text = str(value)
                
        # 标签
        if template.tags:
            tags = ET.SubElement(root, "tags")
            for tag in template.tags:
                ET.SubElement(tags, "tag").text = tag
                
        tree = ET.ElementTree(root)
        tree.write(filepath, encoding='utf-8', xml_declaration=True)
        
    def import_template(self, filepath: str) -> ConfigTemplate:
        """导入配置模板"""
        if filepath.endswith('.json'):
            return self._import_json(filepath)
        elif filepath.endswith('.xml'):
            return self._import_xml(filepath)
        else:
            raise ValueError("不支持的文件格式")
            
    def _import_json(self, filepath: str) -> ConfigTemplate:
        """从JSON文件导入"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data['create_time'] = datetime.fromisoformat(data['create_time'])
            if data.get('last_used'):
                data['last_used'] = datetime.fromisoformat(data['last_used'])
            return ConfigTemplate(**data)
            
    def _import_xml(self, filepath: str) -> ConfigTemplate:
        """从XML文件导入"""
        tree = ET.parse(filepath)
        root = tree.getroot()
        
        # 解析基本信息
        basic_info = root.find('basic_info')
        template_data = {
            'name': basic_info.find('name').text,
            'description': basic_info.find('description').text,
            'category': basic_info.find('category').text,
            'create_time': datetime.fromisoformat(basic_info.find('create_time').text)
        }
        
        if basic_info.find('last_used') is not None:
            template_data['last_used'] = datetime.fromisoformat(basic_info.find('last_used').text)
            
        # 解析目标配置
        target_config = {}
        for elem in root.find('target_config'):
            target_config[elem.tag] = elem.text
        template_data['target_config'] = target_config
        
        # 解析扫描选项
        scan_options = {}
        for elem in root.find('scan_options'):
            scan_options[elem.tag] = elem.text
        template_data['scan_options'] = scan_options
        
        # 解析高级选项
        advanced_elem = root.find('advanced_options')
        if advanced_elem is not None:
            advanced_options = {}
            for elem in advanced_elem:
                advanced_options[elem.tag] = elem.text
            template_data['advanced_options'] = advanced_options
            
        # 解析标签
        tags_elem = root.find('tags')
        if tags_elem is not None:
            template_data['tags'] = [tag.text for tag in tags_elem.findall('tag')]
            
        return ConfigTemplate(**template_data) 
        
    def get_template_versions(self, template_name: str) -> List[ConfigVersion]:
        """获取模板的所有版本"""
        return self.version_manager.get_versions(template_name)
        
    def rollback_template(self, template_name: str, version_id: str) -> Optional[ConfigTemplate]:
        """回滚到指定版本"""
        version = self.version_manager.get_version(template_name, version_id)
        if not version:
            return None
        
        template = self.load_template(f"{template_name}.json")
        if not template:
            return None
        
        template.target_config = version.content['target_config']
        template.scan_options = version.content['scan_options']
        template.advanced_options = version.content.get('advanced_options')
        
        self.save_template(template)
        return template 