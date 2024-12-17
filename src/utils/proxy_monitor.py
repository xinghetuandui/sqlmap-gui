import threading
import time
from typing import Dict, Callable
from src.utils.proxy_tester import ProxyTester

class ProxyMonitor:
    def __init__(self, proxy_config: Dict, status_callback: Callable = None):
        self.proxy_config = proxy_config
        self.status_callback = status_callback
        self.running = False
        self.thread = None
        
    def start(self):
        """开始监控"""
        if self.running:
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop)
        self.thread.daemon = True
        self.thread.start()
        
    def stop(self):
        """停止监控"""
        self.running = False
        if self.thread:
            self.thread.join()
            
    def _monitor_loop(self):
        """监控循环"""
        while self.running:
            success, error, latency = ProxyTester.test_proxy(self.proxy_config)
            
            if self.status_callback:
                self.status_callback({
                    'available': success,
                    'error': error,
                    'latency': latency
                })
                
            time.sleep(30)  # 每30秒检查一次 