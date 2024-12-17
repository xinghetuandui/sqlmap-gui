from typing import Dict, List, Optional
import json
import random
import time
from threading import Lock
from src.utils.proxy_tester import ProxyTester

class ProxyPool:
    def __init__(self):
        self.proxies: List[Dict] = []  # 代理列表
        self.working_proxies: List[Dict] = []  # 可用代理列表
        self.failed_proxies: List[Dict] = []  # 失败代理列表
        self.current_proxy: Optional[Dict] = None  # 当前使用的代理
        self.lock = Lock()  # 线程锁
        
    def add_proxy(self, proxy: Dict) -> bool:
        """添加代理到代理池"""
        with self.lock:
            # 检查代理是否已存在
            if self._proxy_exists(proxy):
                return False
                
            # 测试代理可用性
            success, _, latency = ProxyTester.test_proxy(proxy)
            if success:
                proxy['latency'] = latency
                proxy['last_used'] = 0
                proxy['fail_count'] = 0
                self.proxies.append(proxy)
                self.working_proxies.append(proxy)
                return True
            else:
                self.failed_proxies.append(proxy)
                return False
                
    def get_proxy(self) -> Optional[Dict]:
        """获取一个可用代理"""
        with self.lock:
            if not self.working_proxies:
                return None
                
            # 按延迟排序
            self.working_proxies.sort(key=lambda x: x['latency'])
            
            # 选择延迟最低的代理
            proxy = self.working_proxies[0]
            proxy['last_used'] = time.time()
            self.current_proxy = proxy
            return proxy
            
    def remove_proxy(self, proxy: Dict):
        """移除代理"""
        with self.lock:
            if proxy in self.proxies:
                self.proxies.remove(proxy)
            if proxy in self.working_proxies:
                self.working_proxies.remove(proxy)
            if proxy in self.failed_proxies:
                self.failed_proxies.remove(proxy)
                
    def mark_proxy_failed(self, proxy: Dict):
        """标记代理失败"""
        with self.lock:
            proxy['fail_count'] = proxy.get('fail_count', 0) + 1
            
            # 失败次数过多则移除
            if proxy['fail_count'] >= 3:
                self.remove_proxy(proxy)
                self.failed_proxies.append(proxy)
            elif proxy in self.working_proxies:
                self.working_proxies.remove(proxy)
                
    def refresh_proxies(self):
        """刷新代理状态"""
        with self.lock:
            for proxy in self.proxies[:]:  # 创建副本以避免迭代时修改
                success, _, latency = ProxyTester.test_proxy(proxy)
                if success:
                    proxy['latency'] = latency
                    if proxy not in self.working_proxies:
                        self.working_proxies.append(proxy)
                else:
                    self.mark_proxy_failed(proxy)
                    
    def _proxy_exists(self, proxy: Dict) -> bool:
        """检查代理是否已存在"""
        proxy_key = f"{proxy['type']}:{proxy['host']}:{proxy['port']}"
        for p in self.proxies:
            if f"{p['type']}:{p['host']}:{p['port']}" == proxy_key:
                return True
        return False
        
    def save_to_file(self, filename: str):
        """保存代理池到文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'proxies': self.proxies,
                'failed_proxies': self.failed_proxies
            }, f, indent=2)
            
    def load_from_file(self, filename: str):
        """从文件加载代理池"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.proxies = data.get('proxies', [])
                self.failed_proxies = data.get('failed_proxies', [])
                self.refresh_proxies()  # 刷新代理状态
        except FileNotFoundError:
            pass
            
    def get_stats(self) -> Dict:
        """获取代理池统计信息"""
        return {
            'total': len(self.proxies),
            'working': len(self.working_proxies),
            'failed': len(self.failed_proxies),
            'avg_latency': sum(p['latency'] for p in self.working_proxies) / len(self.working_proxies) if self.working_proxies else 0
        } 