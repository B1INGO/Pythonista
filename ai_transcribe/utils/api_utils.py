"""
API工具模块

提供API调用的通用功能
"""

import json
import time
from typing import Dict, Any, Optional, Tuple
import requests
from .logger import get_logger

logger = get_logger(__name__)

class APIUtils:
    """API工具类"""
    
    @staticmethod
    def make_request(
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        发送HTTP请求
        
        Returns:
            (success, response_data, error_message)
        """
        
        if headers is None:
            headers = {}
        
        # 默认头部
        if 'User-Agent' not in headers:
            headers['User-Agent'] = 'AI-Transcribe/1.0.0'
        
        for attempt in range(max_retries):
            try:
                logger.debug(f"API请求: {method} {url} (尝试 {attempt + 1}/{max_retries})")
                
                # 发送请求
                response = requests.request(
                    method=method.upper(),
                    url=url,
                    headers=headers,
                    json=data if not files else None,
                    data=data if files else None,
                    files=files,
                    timeout=timeout
                )
                
                # 检查状态码
                if response.status_code == 200:
                    try:
                        result = response.json()
                        logger.debug(f"API请求成功: {method} {url}")
                        return True, result, None
                    except json.JSONDecodeError:
                        # 如果不是JSON响应，返回文本
                        return True, {'text': response.text}, None
                else:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    logger.warning(f"API请求失败: {error_msg}")
                    
                    # 对于客户端错误（4xx），不重试
                    if 400 <= response.status_code < 500:
                        return False, None, error_msg
                    
                    # 服务器错误（5xx）可以重试
                    if attempt == max_retries - 1:
                        return False, None, error_msg
            
            except requests.exceptions.Timeout:
                error_msg = f"请求超时 ({timeout}s)"
                logger.warning(f"API请求超时: {method} {url}")
                if attempt == max_retries - 1:
                    return False, None, error_msg
            
            except requests.exceptions.ConnectionError:
                error_msg = "网络连接错误"
                logger.warning(f"API连接错误: {method} {url}")
                if attempt == max_retries - 1:
                    return False, None, error_msg
            
            except Exception as e:
                error_msg = f"请求异常: {str(e)}"
                logger.error(f"API请求异常: {error_msg}")
                if attempt == max_retries - 1:
                    return False, None, error_msg
            
            # 重试延迟
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (2 ** attempt))  # 指数退避
        
        return False, None, "请求失败"
    
    @staticmethod
    def validate_api_key(api_key: str, service: str) -> bool:
        """验证API密钥格式"""
        if not api_key or not isinstance(api_key, str):
            return False
        
        # 移除首尾空格
        api_key = api_key.strip()
        
        if service == 'siliconflow':
            # 硅基流动API密钥格式验证
            return len(api_key) > 20 and api_key.startswith('sk-')
        elif service == 'deepseek':
            # DeepSeek API密钥格式验证
            return len(api_key) > 20 and api_key.startswith('sk-')
        
        # 默认基本验证
        return len(api_key) > 10
    
    @staticmethod
    def prepare_auth_headers(api_key: str, service: str) -> Dict[str, str]:
        """准备认证头部"""
        headers = {
            'Content-Type': 'application/json',
        }
        
        if service in ['siliconflow', 'deepseek']:
            headers['Authorization'] = f'Bearer {api_key}'
        
        return headers
    
    @staticmethod
    def chunk_text(text: str, max_length: int = 4000, overlap: int = 100) -> list:
        """将长文本分块处理"""
        if len(text) <= max_length:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + max_length
            
            if end >= len(text):
                # 最后一块
                chunks.append(text[start:])
                break
            
            # 尝试在句号、问号、感叹号处分割
            for i in range(end, start + max_length - overlap, -1):
                if text[i] in '.!?。！？':
                    end = i + 1
                    break
            
            chunks.append(text[start:end])
            start = end - overlap  # 保持重叠以避免语义断裂
        
        return chunks
    
    @staticmethod
    def estimate_tokens(text: str) -> int:
        """估算文本的token数量（粗略估算）"""
        # 中文字符按1个token计算，英文单词按1个token计算
        chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
        english_words = len(text.replace(''.join([c for c in text if '\u4e00' <= c <= '\u9fff']), '').split())
        
        return chinese_chars + english_words
    
    @staticmethod
    def format_error_message(error: str, context: str = '') -> str:
        """格式化错误消息"""
        if context:
            return f"{context}: {error}"
        return error
    
    @staticmethod
    def is_network_available() -> bool:
        """检查网络连接是否可用"""
        try:
            response = requests.get('https://httpbin.org/status/200', timeout=5)
            return response.status_code == 200
        except:
            return False