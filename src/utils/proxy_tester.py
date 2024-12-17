import requests
import socket
import socks
from typing import Dict, Tuple
import time

class ProxyTester:
    @staticmethod
    def test_proxy(proxy_config: Dict, timeout: int = 5, retries: int = 3) -> Tuple[bool, str, float]:
        """测试代理连接
        Args:
            proxy_config: 代理配置
            timeout: 超时时间(秒)
            retries: 重试次数
        Returns:
            (成功与否, 错误信息, 延迟时间)
        """
        for i in range(retries):
            try:
                start_time = time.time()
                
                # 构建代理URL
                proxy_url = ProxyTester._build_proxy_url(proxy_config)
                
                # 发送测试请求
                response = requests.get(
                    'http://www.baidu.com',
                    proxies={'http': proxy_url, 'https': proxy_url},
                    timeout=timeout,
                    verify=False
                )
                response.raise_for_status()
                
                latency = time.time() - start_time
                return True, "", latency
                
            except requests.exceptions.ProxyError:
                if i == retries - 1:
                    return False, "代理服务器连接失败", 0
            except requests.exceptions.ConnectTimeout:
                if i == retries - 1:
                    return False, "连接超时", 0
            except requests.exceptions.RequestException as e:
                if i == retries - 1:
                    return False, str(e), 0
            except Exception as e:
                if i == retries - 1:
                    return False, f"未知错误: {str(e)}", 0
                
            # 重试前等待
            time.sleep(1)
            
        return False, "重试次数已用完", 0

    @staticmethod
    def _build_proxy_url(proxy_config: Dict) -> str:
        """构建代理URL"""
        proxy_url = f"{proxy_config['type'].lower()}://"
        
        # 添加认证信息
        if proxy_config.get('auth', {}).get('enabled'):
            auth = proxy_config['auth']
            proxy_url += f"{auth['username']}:{auth['password']}@"
            
        proxy_url += f"{proxy_config['host']}:{proxy_config['port']}"
        return proxy_url 