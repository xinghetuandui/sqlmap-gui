import time
import psutil
import threading
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
import logging
from queue import Queue
import json
import os

@dataclass
class PerformanceMetrics:
    cpu_usage: float
    memory_usage: float  # MB
    response_time: float  # ms
    thread_count: int
    queue_size: int
    timestamp: float

class PerformanceManager:
    def __init__(self, config_path: str = "configs/performance.json"):
        self.config_path = config_path
        self.metrics_queue = Queue(maxsize=1000)
        self.metrics_history: List[PerformanceMetrics] = []
        self.running = False
        self.monitor_thread = None
        self.callbacks: List[Callable] = []
        
        # 性能阈值配置
        self.thresholds = self.load_thresholds()
        
        # 初始化日志
        self.logger = logging.getLogger('performance')
        self.logger.setLevel(logging.INFO)
        
    def load_thresholds(self) -> Dict:
        """加载性能阈值配置"""
        default_thresholds = {
            'cpu_warning': 80,  # CPU使用率警告阈值
            'memory_warning': 1024,  # 内存使用警告阈值(MB)
            'response_warning': 5000,  # 响应时间警告阈值(ms)
            'max_threads': 10,  # 最大线程数
            'max_queue_size': 1000  # 最大队列大小
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return {**default_thresholds, **json.load(f)}
        except Exception as e:
            self.logger.error(f"加载性能配置失败: {e}")
            
        return default_thresholds
        
    def start_monitoring(self):
        """开始性能监控"""
        if self.running:
            return
        
        try:
            self.running = True
            self.monitor_thread = threading.Thread(
                target=self._monitor_loop,
                daemon=True,
                name="PerformanceMonitor"
            )
            self.monitor_thread.start()
            self.logger.info("性能监控已启动")
            
        except Exception as e:
            self.running = False
            self.logger.error(f"启动性能监控失败: {str(e)}")
            raise
        
    def stop_monitoring(self):
        """停止性能监控"""
        if not self.running:
            return
        
        try:
            self.running = False
            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=1.0)  # 等待最多1秒
                if self.monitor_thread.is_alive():
                    self.logger.warning("性能监控线程未能正常停止")
                else:
                    self.logger.info("性能监控已停止")
                
        except Exception as e:
            self.logger.error(f"停止性能监控失败: {str(e)}")
        
    def _monitor_loop(self):
        """监控循环"""
        while self.running:
            try:
                metrics = self._collect_metrics()
                self._process_metrics(metrics)
                time.sleep(1)  # 每秒采一次
            except Exception as e:
                self.logger.error(f"性能监控错误: {e}")
                
    def _collect_metrics(self) -> PerformanceMetrics:
        """收集性能指标"""
        process = psutil.Process()
        
        return PerformanceMetrics(
            cpu_usage=process.cpu_percent(),
            memory_usage=process.memory_info().rss / 1024 / 1024,
            response_time=self._measure_response_time(),
            thread_count=threading.active_count(),
            queue_size=self.metrics_queue.qsize(),
            timestamp=time.time()
        )
        
    def _measure_response_time(self) -> float:
        """测量响应时间"""
        # TODO: 实现实际的响应时间测量
        return 0.0
        
    def _process_metrics(self, metrics: PerformanceMetrics):
        """处理性能指标"""
        # 添加到历史记录
        self.metrics_history.append(metrics)
        if len(self.metrics_history) > 1000:  # 保留最近1000条记录
            self.metrics_history.pop(0)
            
        # 检查是否超过阈值
        self._check_thresholds(metrics)
        
        # 通知回调函数
        for callback in self.callbacks:
            try:
                callback(metrics)
            except Exception as e:
                self.logger.error(f"性能回调错误: {e}")
                
    def _check_thresholds(self, metrics: PerformanceMetrics):
        """检查性能阈值"""
        if metrics.cpu_usage > self.thresholds['cpu_warning']:
            self.logger.warning(f"CPU使用率过高: {metrics.cpu_usage}%")
            self._optimize_cpu_usage()
            
        if metrics.memory_usage > self.thresholds['memory_warning']:
            self.logger.warning(f"内存使用过高: {metrics.memory_usage}MB")
            self._optimize_memory_usage()
            
        if metrics.response_time > self.thresholds['response_warning']:
            self.logger.warning(f"响应时间过长: {metrics.response_time}ms")
            self._optimize_response_time()
            
    def _optimize_cpu_usage(self):
        """优化CPU使用"""
        # 减少活动线程数
        if threading.active_count() > self.thresholds['max_threads']:
            self.logger.info("正在减少线程数...")
            # TODO: 实现线程数调整
            
    def _optimize_memory_usage(self):
        """优化内存使用"""
        # 清理缓存
        self.logger.info("正在清理内存...")
        if len(self.metrics_history) > 100:
            self.metrics_history = self.metrics_history[-100:]
            
    def _optimize_response_time(self):
        """优化响应时间"""
        # 调整队列大小
        if self.metrics_queue.qsize() > self.thresholds['max_queue_size']:
            self.logger.info("正在调整队列大小...")
            while not self.metrics_queue.empty():
                self.metrics_queue.get()
                
    def add_callback(self, callback: Callable[[PerformanceMetrics], None]):
        """添加性能回调函数"""
        self.callbacks.append(callback)
        
    def remove_callback(self, callback: Callable):
        """移除性能回调函数"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
            
    def get_metrics_summary(self) -> Dict:
        """获取性能指标摘要"""
        if not self.metrics_history:
            return {}
            
        return {
            'cpu': {
                'current': self.metrics_history[-1].cpu_usage,
                'avg': sum(m.cpu_usage for m in self.metrics_history) / len(self.metrics_history),
                'max': max(m.cpu_usage for m in self.metrics_history)
            },
            'memory': {
                'current': self.metrics_history[-1].memory_usage,
                'avg': sum(m.memory_usage for m in self.metrics_history) / len(self.metrics_history),
                'max': max(m.memory_usage for m in self.metrics_history)
            },
            'response_time': {
                'current': self.metrics_history[-1].response_time,
                'avg': sum(m.response_time for m in self.metrics_history) / len(self.metrics_history),
                'max': max(m.response_time for m in self.metrics_history)
            },
            'threads': {
                'current': self.metrics_history[-1].thread_count,
                'max': max(m.thread_count for m in self.metrics_history)
            },
            'queue': {
                'current': self.metrics_history[-1].queue_size,
                'max': max(m.queue_size for m in self.metrics_history)
            }
        } 

    def optimize_performance(self):
        """性能优化"""
        metrics = self.get_metrics_summary()
        
        # CPU优化
        if metrics['cpu']['current'] > self.thresholds['cpu_warning']:
            self._optimize_cpu()
            
        # 内存优化
        if metrics['memory']['current'] > self.thresholds['memory_warning']:
            self._optimize_memory()
            
        # 响应时间优化
        if metrics['response_time']['current'] > self.thresholds['response_warning']:
            self._optimize_response_time()
            
    def _optimize_cpu(self):
        """CPU优化"""
        # 减少活动线程数
        current_threads = threading.active_count()
        if current_threads > self.thresholds['max_threads']:
            # 通知应用程序减少线程数
            for callback in self.callbacks:
                try:
                    callback({
                        'type': 'optimize',
                        'target': 'cpu',
                        'action': 'reduce_threads',
                        'current': current_threads,
                        'target': self.thresholds['max_threads']
                    })
                except:
                    pass
                    
    def _optimize_memory(self):
        """内存优化"""
        # 清理历史数据
        if len(self.metrics_history) > 100:
            self.metrics_history = self.metrics_history[-100:]
            
        # 通知应用程序清理缓存
        for callback in self.callbacks:
            try:
                callback({
                    'type': 'optimize',
                    'target': 'memory',
                    'action': 'clear_cache'
                })
            except:
                pass
                
    def _optimize_response_time(self):
        """响应时间优化"""
        # 调整请求间隔
        for callback in self.callbacks:
            try:
                callback({
                    'type': 'optimize',
                    'target': 'response_time',
                    'action': 'adjust_interval'
                })
            except:
                pass 