from typing import Dict, List, Tuple
import re
import json

class ConfigValidator:
    @staticmethod
    def validate_target_config(config: Dict) -> Tuple[bool, List[str]]:
        """验证目标配置"""
        errors = []
        
        # 验证URL
        if 'url' in config:
            if not isinstance(config['url'], str):
                errors.append("URL必须是字符串类型")
            elif not re.match(r'^https?://', config['url']):
                errors.append("URL必须以http://或https://开头")
                
        # 验证HTTP方法
        if 'method' in config:
            valid_methods = ['GET', 'POST', 'PUT', 'DELETE']
            if config['method'] not in valid_methods:
                errors.append(f"不支持的HTTP方法: {config['method']}")
                
        # 验证Headers
        if 'headers' in config:
            if isinstance(config['headers'], str):
                # 验证headers字符串格式
                for line in config['headers'].split('\n'):
                    if line.strip() and ':' not in line:
                        errors.append(f"无效的header格式: {line}")
            elif isinstance(config['headers'], dict):
                # headers字典格式验证
                for key, value in config['headers'].items():
                    if not isinstance(key, str) or not isinstance(value, str):
                        errors.append("Headers的键和值必须是字符串类型")
            else:
                errors.append("Headers必须是字符串或字典类型")
                
        return len(errors) == 0, errors
        
    @staticmethod
    def validate_scan_options(options: Dict) -> Tuple[bool, List[str]]:
        """验证扫描选项"""
        errors = []
        
        # 验证level
        if 'level' in options:
            if not isinstance(options['level'], int):
                errors.append("level必须是整数类型")
            elif not 1 <= options['level'] <= 5:
                errors.append("level必须在1-5之间")
                
        # 验证risk
        if 'risk' in options:
            if not isinstance(options['risk'], int):
                errors.append("risk必须是整数类型")
            elif not 1 <= options['risk'] <= 3:
                errors.append("risk必须在1-3之间")
                
        # 验证threads
        if 'threads' in options:
            if not isinstance(options['threads'], int):
                errors.append("threads必须是整数类型")
            elif not 1 <= options['threads'] <= 10:
                errors.append("threads必须在1-10之间")
                
        # 验证technique
        if 'technique' in options:
            valid_chars = set('BEUSTQ')
            if not all(c in valid_chars for c in options['technique']):
                errors.append("technique只能包含BEUSTQ字符")
                
        return len(errors) == 0, errors
        
    @staticmethod
    def validate_advanced_options(options: Dict) -> Tuple[bool, List[str]]:
        """验证高级选项"""
        errors = []
        
        # 验证auth配置
        if 'auth_config' in options:
            auth = options['auth_config']
            if not isinstance(auth, dict):
                errors.append("auth_config必须是字典类型")
            else:
                if 'type' not in auth:
                    errors.append("auth_config必须包含type字段")
                elif auth['type'] not in ['BASIC', 'DIGEST', 'NTLM', 'PKI']:
                    errors.append(f"不支持的认证类型: {auth['type']}")
                    
        # 验证WAF配置
        if 'waf_config' in options:
            waf = options['waf_config']
            if not isinstance(waf, dict):
                errors.append("waf_config必须是字典类型")
            else:
                if 'delay' in waf and not isinstance(waf['delay'], (int, float)):
                    errors.append("waf_config.delay必须是数字类型")
                    
        return len(errors) == 0, errors
        
    @staticmethod
    def validate_template(template: Dict) -> Tuple[bool, List[str]]:
        """验证完整的配置模板"""
        errors = []
        
        # 验证基本字段
        required_fields = ['name', 'description', 'target_config', 'scan_options']
        for field in required_fields:
            if field not in template:
                errors.append(f"缺少必需字段: {field}")
                
        # 验证各个部分
        if 'target_config' in template:
            valid, target_errors = ConfigValidator.validate_target_config(template['target_config'])
            errors.extend(target_errors)
            
        if 'scan_options' in template:
            valid, scan_errors = ConfigValidator.validate_scan_options(template['scan_options'])
            errors.extend(scan_errors)
            
        if 'advanced_options' in template:
            valid, adv_errors = ConfigValidator.validate_advanced_options(template['advanced_options'])
            errors.extend(adv_errors)
            
        return len(errors) == 0, errors 