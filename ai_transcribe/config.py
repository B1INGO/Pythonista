"""
配置管理模块

管理API密钥、应用设置和用户配置
"""

import json
import os
import keychain
from typing import Dict, Any, Optional

class Config:
    """配置管理类"""
    
    def __init__(self):
        self.config_file = os.path.join(os.path.dirname(__file__), 'config.json')
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        default_config = {
            'app_name': 'AI音视频转文字工具',
            'version': '1.0.0',
            'supported_formats': {
                'audio': ['.mp3', '.wav', '.aac', '.m4a', '.flac'],
                'video': ['.mp4', '.mov', '.avi', '.mkv', '.wmv']
            },
            'transcribe': {
                'max_file_size_mb': 100,
                'chunk_duration_seconds': 60,
                'api_timeout_seconds': 30,
                'api_base_url': 'https://api.siliconflow.cn/v1'
            },
            'ai_process': {
                'api_base_url': 'https://api.deepseek.com/v1',
                'model': 'deepseek-chat',
                'max_tokens': 4000,
                'temperature': 0.7
            },
            'ui': {
                'theme': 'light',
                'font_size': 16,
                'progress_update_interval': 0.5
            },
            'cache': {
                'enabled': True,
                'max_size_mb': 500,
                'ttl_hours': 24
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                # 合并默认配置和用户配置
                default_config.update(user_config)
            except Exception as e:
                print(f"警告：无法加载配置文件: {e}")
        
        return default_config
    
    def save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"警告：无法保存配置文件: {e}")
    
    def get(self, key: str, default=None):
        """获取配置值"""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        keys = key.split('.')
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save_config()
    
    def get_api_key(self, service: str) -> Optional[str]:
        """从keychain获取API密钥"""
        try:
            return keychain.get_password(f'ai_transcribe_{service}', 'api_key')
        except Exception as e:
            print(f"警告：无法获取{service}的API密钥: {e}")
            return None
    
    def set_api_key(self, service: str, api_key: str) -> bool:
        """设置API密钥到keychain"""
        try:
            keychain.set_password(f'ai_transcribe_{service}', 'api_key', api_key)
            return True
        except Exception as e:
            print(f"错误：无法设置{service}的API密钥: {e}")
            return False
    
    def delete_api_key(self, service: str) -> bool:
        """删除API密钥"""
        try:
            keychain.delete_password(f'ai_transcribe_{service}', 'api_key')
            return True
        except Exception as e:
            print(f"警告：无法删除{service}的API密钥: {e}")
            return False

# 全局配置实例
config = Config()