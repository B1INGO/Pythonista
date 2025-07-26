"""
缓存管理模块

提供文件缓存和内存缓存功能
"""

import os
import json
import hashlib
import time
from typing import Any, Optional, Dict
from ..config import config
from .logger import get_logger

logger = get_logger(__name__)

class Cache:
    """缓存管理器"""
    
    def __init__(self):
        self.cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cache')
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.enabled = config.get('cache.enabled', True)
        self.max_size_mb = config.get('cache.max_size_mb', 500)
        self.ttl_hours = config.get('cache.ttl_hours', 24)
        
        if self.enabled:
            os.makedirs(self.cache_dir, exist_ok=True)
            self._cleanup_expired()
    
    def _get_cache_key(self, key: str) -> str:
        """生成缓存键的哈希值"""
        return hashlib.md5(key.encode('utf-8')).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> str:
        """获取缓存文件路径"""
        return os.path.join(self.cache_dir, f'{cache_key}.cache')
    
    def _is_expired(self, timestamp: float) -> bool:
        """检查缓存是否过期"""
        return time.time() - timestamp > self.ttl_hours * 3600
    
    def _cleanup_expired(self):
        """清理过期的缓存文件"""
        if not os.path.exists(self.cache_dir):
            return
        
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.cache'):
                    file_path = os.path.join(self.cache_dir, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            cache_data = json.load(f)
                        
                        if self._is_expired(cache_data.get('timestamp', 0)):
                            os.remove(file_path)
                            logger.debug(f"删除过期缓存文件: {filename}")
                    except Exception as e:
                        logger.warning(f"清理缓存文件失败 {filename}: {e}")
                        # 删除损坏的缓存文件
                        try:
                            os.remove(file_path)
                        except:
                            pass
        except Exception as e:
            logger.error(f"清理缓存目录失败: {e}")
    
    def set(self, key: str, value: Any, memory_only: bool = False) -> bool:
        """设置缓存"""
        if not self.enabled:
            return False
        
        cache_key = self._get_cache_key(key)
        cache_data = {
            'key': key,
            'value': value,
            'timestamp': time.time()
        }
        
        # 内存缓存
        self.memory_cache[cache_key] = cache_data
        
        # 文件缓存
        if not memory_only:
            try:
                cache_path = self._get_cache_path(cache_key)
                with open(cache_path, 'w', encoding='utf-8') as f:
                    json.dump(cache_data, f, ensure_ascii=False, indent=2)
                logger.debug(f"缓存已保存: {key}")
                return True
            except Exception as e:
                logger.error(f"保存缓存失败 {key}: {e}")
                return False
        
        return True
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if not self.enabled:
            return None
        
        cache_key = self._get_cache_key(key)
        
        # 先检查内存缓存
        if cache_key in self.memory_cache:
            cache_data = self.memory_cache[cache_key]
            if not self._is_expired(cache_data['timestamp']):
                logger.debug(f"从内存缓存获取: {key}")
                return cache_data['value']
            else:
                # 清理过期的内存缓存
                del self.memory_cache[cache_key]
        
        # 检查文件缓存
        cache_path = self._get_cache_path(cache_key)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                if not self._is_expired(cache_data['timestamp']):
                    # 重新加载到内存缓存
                    self.memory_cache[cache_key] = cache_data
                    logger.debug(f"从文件缓存获取: {key}")
                    return cache_data['value']
                else:
                    # 删除过期的文件缓存
                    os.remove(cache_path)
                    logger.debug(f"删除过期缓存: {key}")
            except Exception as e:
                logger.warning(f"读取缓存失败 {key}: {e}")
                # 删除损坏的缓存文件
                try:
                    os.remove(cache_path)
                except:
                    pass
        
        return None
    
    def delete(self, key: str) -> bool:
        """删除缓存"""
        cache_key = self._get_cache_key(key)
        
        # 删除内存缓存
        if cache_key in self.memory_cache:
            del self.memory_cache[cache_key]
        
        # 删除文件缓存
        cache_path = self._get_cache_path(cache_key)
        if os.path.exists(cache_path):
            try:
                os.remove(cache_path)
                logger.debug(f"缓存已删除: {key}")
                return True
            except Exception as e:
                logger.error(f"删除缓存失败 {key}: {e}")
                return False
        
        return True
    
    def clear(self) -> bool:
        """清空所有缓存"""
        try:
            # 清空内存缓存
            self.memory_cache.clear()
            
            # 清空文件缓存
            if os.path.exists(self.cache_dir):
                for filename in os.listdir(self.cache_dir):
                    if filename.endswith('.cache'):
                        os.remove(os.path.join(self.cache_dir, filename))
            
            logger.info("所有缓存已清空")
            return True
        except Exception as e:
            logger.error(f"清空缓存失败: {e}")
            return False
    
    def get_cache_size(self) -> Dict[str, float]:
        """获取缓存大小信息（MB）"""
        try:
            total_size = 0
            file_count = 0
            
            if os.path.exists(self.cache_dir):
                for filename in os.listdir(self.cache_dir):
                    if filename.endswith('.cache'):
                        file_path = os.path.join(self.cache_dir, filename)
                        total_size += os.path.getsize(file_path)
                        file_count += 1
            
            return {
                'total_size_mb': total_size / (1024 * 1024),
                'file_count': file_count,
                'memory_items': len(self.memory_cache)
            }
        except Exception as e:
            logger.error(f"获取缓存大小失败: {e}")
            return {'total_size_mb': 0, 'file_count': 0, 'memory_items': 0}

# 全局缓存实例
cache = Cache()