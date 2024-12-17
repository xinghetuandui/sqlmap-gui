import subprocess
import json
import os
import threading
from typing import Dict, List, Optional
import psutil
import time
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import logging
from src.utils.proxy_switcher import ProxySwitcher
from src.utils.proxy_pool import ProxyPool

class SQLMapWrapper:
    def __init__(self, sqlmap_path: str = "sqlmap", max_workers: int = 3):
        self.sqlmap_path = sqlmap_path
        self.process = None
        self.output_dir = "sqlmap_results"
        self.max_workers = max_workers
        self.task_queue = Queue()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.running_tasks = []
        
        # 性能监控
        self.performance_stats = {
            'cpu_usage': [],
            'memory_usage': [],
            'scan_duration': [],
            'success_rate': 0
        }
        
        # 配置日志
        logging.basicConfig(
            filename='sqlmap.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        self.proxy_switcher = None
        self.current_proxy = None
        
    def build_command(self, target_config: Dict, options: Dict = None) -> List[str]:
        """构建sqlmap命令"""
        cmd = [self.sqlmap_path]
        
        # 添加目标URL
        cmd.extend(["-u", target_config["url"]])
        
        # 添加HTTP方法
        if target_config.get("method"):
            cmd.extend(["--method", target_config["method"]])
            
        # 添加Headers
        if target_config.get("headers"):
            headers = target_config["headers"].strip()
            if headers:
                cmd.extend(["--headers", headers])
                
        # 添加Cookies
        if target_config.get("cookies"):
            cmd.extend(["--cookie", target_config["cookies"]])
            
        # 添加代理设置
        proxy = target_config.get("proxy", {})
        if proxy.get("enabled"):
            proxy_url = f"{proxy['type'].lower()}://{proxy['host']}:{proxy['port']}"
            cmd.extend(["--proxy", proxy_url])
            
        # 添加高级选项
        if options:
            # 如果选项是字符串列表（来自AdvancedOptions），直接扩展
            if isinstance(options, list):
                cmd.extend(options)
            # 否按原有方式处理
            else:
                if options.get('technique'):
                    cmd.extend(["--technique", options['technique']])
                    
                # 测试级别
                if options.get('level'):
                    cmd.extend(["--level", str(options['level'])])
                    
                # 风险等级
                if options.get('risk'):
                    cmd.extend(["--risk", str(options['risk'])])
                    
                # 线程数
                if options.get('threads'):
                    cmd.extend(["--threads", str(options['threads'])])
                    
                # 枚举选项
                if options.get('getDbs'):
                    cmd.append("--dbs")
                if options.get('getTables'):
                    cmd.append("--tables")
                if options.get('getColumns'):
                    cmd.append("--columns")
                if options.get('dumpData'):
                    cmd.append("--dump")
                    
                # 其他选项
                if options.get('verbose'):
                    cmd.append("-v")
                if options.get('batch'):
                    cmd.append("--batch")
                    
        # 添加输出目录
        cmd.extend(["--output-dir", self.output_dir])
        
        return cmd
        
    def start_scan(self, target_config: Dict, log_callback=None,
                  complete_callback=None, error_callback=None):
        """开始扫描"""
        if 'targets' in target_config:
            # 批量扫描使用线程池
            targets = target_config['targets']
            for target in targets:
                self.task_queue.put({
                    'target': target,
                    'callbacks': (log_callback, complete_callback, error_callback)
                })
            
            # 启动工作线程
            for _ in range(min(self.max_workers, len(targets))):
                self._start_worker()
        else:
            # 单一目标扫描
            self._scan_single_target(
                target_config,
                log_callback,
                complete_callback,
                error_callback
            )
            
    def _start_worker(self):
        """启动工作线程"""
        future = self.executor.submit(self._worker_loop)
        self.running_tasks.append(future)
        
    def _worker_loop(self):
        """工作线程循环"""
        while not self.task_queue.empty():
            task = self.task_queue.get()
            target = task['target']
            callbacks = task['callbacks']
            
            try:
                start_time = time.time()
                self._scan_single_target(target, *callbacks)
                duration = time.time() - start_time
                
                # 记录性能数据
                self._update_performance_stats(duration)
                
            except Exception as e:
                logging.error(f"扫描失败: {str(e)}")
                if callbacks[2]:  # error_callback
                    callbacks[2](str(e))
                    
            finally:
                self.task_queue.task_done()
                
    def _update_performance_stats(self, duration: float):
        """更新性能统计"""
        if self.process:
            try:
                process = psutil.Process(self.process.pid)
                self.performance_stats['cpu_usage'].append(
                    process.cpu_percent()
                )
                self.performance_stats['memory_usage'].append(
                    process.memory_info().rss / 1024 / 1024  # MB
                )
            except:
                pass
                
        self.performance_stats['scan_duration'].append(duration)
        
    def get_performance_stats(self) -> Dict:
        """获取性能统计"""
        stats = self.performance_stats.copy()
        if stats['scan_duration']:
            stats['avg_duration'] = sum(stats['scan_duration']) / len(stats['scan_duration'])
            stats['max_duration'] = max(stats['scan_duration'])
            stats['min_duration'] = min(stats['scan_duration'])
            
        if stats['cpu_usage']:
            stats['avg_cpu'] = sum(stats['cpu_usage']) / len(stats['cpu_usage'])
            stats['max_cpu'] = max(stats['cpu_usage'])
            
        if stats['memory_usage']:
            stats['avg_memory'] = sum(stats['memory_usage']) / len(stats['memory_usage'])
            stats['max_memory'] = max(stats['memory_usage'])
            
        return stats
        
    def optimize_performance(self):
        """性能优化"""
        stats = self.get_performance_stats()
        
        # 根据CPU使用率调整线程数
        if stats.get('avg_cpu', 0) > 80:
            self.max_workers = max(1, self.max_workers - 1)
        elif stats.get('avg_cpu', 0) < 50:
            self.max_workers += 1
            
        # 根据内存使用调整批处理大小
        if stats.get('avg_memory', 0) > 1024:  # 1GB
            self.batch_size = max(1, self.batch_size - 5)
        elif stats.get('avg_memory', 0) < 512:  # 512MB
            self.batch_size += 5
        
    def _scan_single_target(self, target_config: Dict, log_callback=None,
                           complete_callback=None, error_callback=None):
        """扫描单个目标"""
        cmd = self.build_command(target_config)
        
        def run_scan():
            try:
                self.process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                
                # 收集输出
                output_data = []
                while True:
                    output = self.process.stdout.readline()
                    if output == '' and self.process.poll() is not None:
                        break
                    if output:
                        output_data.append(output.strip())
                        if log_callback:
                            log_callback(output.strip())
                    
                return_code = self.process.poll()
                
                # 检查是否成功完成
                if return_code == 0:
                    # 读取结果文件
                    result = self.get_results()
                    if complete_callback:
                        complete_callback(result)
                else:
                    error_msg = f"扫描失败，返回码: {return_code}"
                    if error_callback:
                        error_callback(error_msg)
                    
            except Exception as e:
                if error_callback:
                    error_callback(str(e))
                    
        # 在新线程中运行扫描
        thread = threading.Thread(target=run_scan)
        thread.daemon = True
        thread.start()
        
    def stop_scan(self):
        """停止扫描"""
        if self.process:
            self.process.terminate()
            
    def get_results(self) -> Optional[Dict]:
        """获取扫描结果"""
        try:
            results_file = os.path.join(self.output_dir, "results.json")
            if os.path.exists(results_file):
                with open(results_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"读取结果文件出错: {str(e)}")
        return None 

    def set_proxy(self, proxy_config: dict):
        """设置代理配置"""
        if not proxy_config:
            if '--proxy' in self.options:
                del self.options['--proxy']
            return
        
        # 处理代理链
        if 'chain' in proxy_config:
            proxy_chain = []
            for proxy in proxy_config['chain']:
                proxy_url = f"{proxy['type']}://"
                if proxy.get('auth', {}).get('enabled'):
                    proxy_url += f"{proxy['auth']['username']}:{proxy['auth']['password']}@"
                proxy_url += f"{proxy['host']}:{proxy['port']}"
                proxy_chain.append(proxy_url)
            
            if proxy_chain:
                self.options['--proxy-chain'] = ','.join(proxy_chain)
            
        # 处理单个代理
        elif 'http' in proxy_config:
            self.options['--proxy'] = proxy_config['http']

    def set_proxy_pool(self, proxy_pool: ProxyPool):
        """设置代理池"""
        self.proxy_switcher = ProxySwitcher(proxy_pool)
        self.proxy_switcher.start(self._on_proxy_switch)
        
    def _on_proxy_switch(self, proxy: Dict):
        """代理切换回调"""
        self.current_proxy = proxy
        # 如果正在扫描，需要重新应用代理设置
        if self.process and self.process.poll() is None:
            self._apply_proxy_settings()
            
    def _apply_proxy_settings(self):
        """应用代理设置"""
        if not self.current_proxy:
            return
        
        proxy_url = f"{self.current_proxy['type'].lower()}://"
        if self.current_proxy.get('auth', {}).get('enabled'):
            auth = self.current_proxy['auth']
            proxy_url += f"{auth['username']}:{auth['password']}@"
        proxy_url += f"{self.current_proxy['host']}:{self.current_proxy['port']}"
        
        # 设置环境变量
        os.environ['HTTP_PROXY'] = proxy_url
        os.environ['HTTPS_PROXY'] = proxy_url