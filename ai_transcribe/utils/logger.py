"""
日志系统模块

提供完整的日志记录和错误追踪功能
"""

import logging
import os
from datetime import datetime
from typing import Optional

class Logger:
    """日志管理器"""
    
    def __init__(self, name: str = 'ai_transcribe', level: int = logging.INFO):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # 避免重复添加handler
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """设置日志处理器"""
        # 创建日志目录
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # 文件处理器
        log_file = os.path.join(log_dir, f'{self.name}_{datetime.now().strftime("%Y%m%d")}.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str, *args, **kwargs):
        """调试日志"""
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """信息日志"""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """警告日志"""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """错误日志"""
        self.logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """严重错误日志"""
        self.logger.critical(message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs):
        """异常日志（会记录堆栈跟踪）"""
        self.logger.exception(message, *args, **kwargs)

# 全局日志实例
_global_logger: Optional[Logger] = None

def get_logger(name: str = 'ai_transcribe', level: int = logging.INFO) -> Logger:
    """获取日志器实例"""
    global _global_logger
    if _global_logger is None or _global_logger.name != name:
        _global_logger = Logger(name, level)
    return _global_logger