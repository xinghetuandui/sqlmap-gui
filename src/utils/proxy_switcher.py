from typing import Dict, Optional, Callable
import threading
import time
from src.utils.proxy_pool import ProxyPool
from src.utils.proxy_tester import ProxyTester

class ProxySwitcher:
    def __init__(self, proxy_pool: ProxyPool):
        self.proxy_pool = proxy_pool
        self.current_proxy = None
        self.running = False
        self.monitor_thread = None
        self.switch_callback = None
        self.check_interval = 30  # 检查间隔(秒)
        
    def start(self, switch_callback: Callable[[Dict], None]):
        """启动代理切换器"""
        if self.running:
            return
            
        self.running = True
        self.switch_callback = switch_callback
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True,
            name="ProxySwitcher"
        )
        self.monitor_thread.start()
        
    def stop(self):
        """停止代理切换器"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
            
    def _monitor_loop(self):
        """监控循环"""
        while self.running:
            try:
                self._check_and_switch()
                time.sleep(self.check_interval)
            except Exception as e:
                print(f"代理切换错误: {str(e)}")
                
    def _check_and_switch(self):
        """检查并切换代理"""
        # 当前代理可用性检查
        if self.current_proxy:
            success, _, _ = ProxyTester.test_proxy(self.current_proxy)
            if success:
                return  # 当前代理可用，继续使用
            
            # 标记当前代理失败
            self.proxy_pool.mark_proxy_failed(self.current_proxy)
            
        # 获取新代理
        new_proxy = self.proxy_pool.get_proxy()
        if new_proxy:
            self.current_proxy = new_proxy
            if self.switch_callback:
                self.switch_callback(new_proxy) 