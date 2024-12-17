from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class AuthConfig:
    type: str  # BASIC, DIGEST, NTLM, PKI
    username: str
    password: str
    domain: Optional[str] = None
    cert_file: Optional[str] = None
    key_file: Optional[str] = None

@dataclass
class WafConfig:
    # WAF/IPS/IDS 绕过选项
    techniques: List[str]  # 使用的绕过技术
    delay: int  # 请求延迟
    retries: int  # 重试次数
    random_agent: bool  # 随机User-Agent
    tamper_scripts: List[str]  # 使用的tamper脚本

@dataclass
class EncodingConfig:
    # 字符编码设置
    encoding: str  # 页面编码
    param_encoding: str  # 参数编码
    payload_encoding: str  # Payload编码
    skip_urlencode: bool  # 跳过URL编码
    skip_escape: bool  # 跳过特殊字符转义

class AdvancedOptions:
    def __init__(self):
        self.auth_config = None
        self.waf_config = None
        self.encoding_config = None
        self.custom_payloads = []
        
    def to_sqlmap_args(self) -> List[str]:
        """转换为SQLMap命令行参数"""
        args = []
        
        # 认证设置
        if self.auth_config:
            if self.auth_config.type == "BASIC":
                args.extend(["--auth-type", "Basic"])
                args.extend(["--auth-cred", f"{self.auth_config.username}:{self.auth_config.password}"])
            elif self.auth_config.type == "DIGEST":
                args.extend(["--auth-type", "Digest"])
                args.extend(["--auth-cred", f"{self.auth_config.username}:{self.auth_config.password}"])
            elif self.auth_config.type == "NTLM":
                args.extend(["--auth-type", "NTLM"])
                args.extend(["--auth-cred", f"{self.auth_config.username}:{self.auth_config.password}"])
                if self.auth_config.domain:
                    args.extend(["--auth-domain", self.auth_config.domain])
            elif self.auth_config.type == "PKI":
                if self.auth_config.cert_file:
                    args.extend(["--auth-cert", self.auth_config.cert_file])
                if self.auth_config.key_file:
                    args.extend(["--auth-key", self.auth_config.key_file])
                    
        # WAF绕过设置
        if self.waf_config:
            if self.waf_config.techniques:
                args.extend(["--skip-waf"])
            if self.waf_config.delay:
                args.extend(["--delay", str(self.waf_config.delay)])
            if self.waf_config.retries:
                args.extend(["--retries", str(self.waf_config.retries)])
            if self.waf_config.random_agent:
                args.append("--random-agent")
            if self.waf_config.tamper_scripts:
                args.extend(["--tamper", ",".join(self.waf_config.tamper_scripts)])
                
        # 编码设置
        if self.encoding_config:
            if self.encoding_config.encoding:
                args.extend(["--charset", self.encoding_config.encoding])
            if self.encoding_config.skip_urlencode:
                args.append("--skip-urlencode")
            if self.encoding_config.skip_escape:
                args.append("--skip-escape")
                
        # 自定义payload
        if self.custom_payloads:
            args.extend(["--custom-payload", self._format_custom_payloads()])
            
        return args
        
    def _format_custom_payloads(self) -> str:
        """格式化自定义payload"""
        return ";".join(self.custom_payloads) 