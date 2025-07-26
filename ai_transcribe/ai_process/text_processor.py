"""
文本处理核心模块

协调AI文本处理流程
"""

from typing import Tuple, Optional, Callable, Dict, Any, List
from ..config import config
from ..utils.logger import get_logger
from ..utils.cache import cache
from .deepseek_client import DeepSeekClient
# Note: Import removed - now using unified config system

logger = get_logger(__name__)

class TextProcessor:
    """文本处理器类"""
    
    def __init__(self):
        self.client = DeepSeekClient()
        self.use_cache = config.get('cache.enabled', True)
    
    def process_with_template(
        self,
        text: str,
        template_id: str,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        使用模板处理文本
        
        Args:
            text: 要处理的文本
            template_id: 模板ID
            progress_callback: 进度回调函数
            
        Returns:
            (success, processed_text, error_message)
        """
        try:
            if progress_callback:
                progress_callback(0.0, "准备处理...")
            
            # 获取模板
            template = self._get_template(template_id)
            if not template:
                return False, None, f"模板不存在: {template_id}"
            
            if progress_callback:
                progress_callback(0.1, "加载模板...")
            
            # 检查缓存
            cache_key = self._get_cache_key(text, template_id)
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                logger.info("使用缓存的处理结果")
                if progress_callback:
                    progress_callback(1.0, "处理完成（来自缓存）")
                return True, cached_result, None
            
            if progress_callback:
                progress_callback(0.2, "开始AI处理...")
            
            # 使用AI处理文本
            success, processed_text, error = self.client.process_text(
                text=text,
                prompt=template.get('user_prompt', ''),
                system_prompt=template.get('system_prompt')
            )
            
            # 更新模板使用统计（暂时移除，等待后续实现）
            # if success and template_id.startswith('custom_'):
            #     custom_prompts.increment_usage(template_id.replace('custom_', ''))
            
            # 缓存结果
            if success and processed_text and self.use_cache:
                self._cache_result(cache_key, processed_text)
            
            if progress_callback:
                if success:
                    progress_callback(1.0, "处理完成")
                else:
                    progress_callback(0.2, f"处理失败: {error}")
            
            return success, processed_text, error
        
        except Exception as e:
            logger.exception(f"模板处理异常: {template_id}")
            error_msg = f"处理过程发生错误: {str(e)}"
            if progress_callback:
                progress_callback(0.0, error_msg)
            return False, None, error_msg
    
    def process_with_custom_prompt(
        self,
        text: str,
        user_prompt: str,
        system_prompt: Optional[str] = None,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        使用自定义提示词处理文本
        
        Args:
            text: 要处理的文本
            user_prompt: 用户提示词
            system_prompt: 系统提示词（可选）
            progress_callback: 进度回调函数
            
        Returns:
            (success, processed_text, error_message)
        """
        try:
            if progress_callback:
                progress_callback(0.0, "准备处理...")
            
            if not user_prompt or not user_prompt.strip():
                return False, None, "用户提示词不能为空"
            
            if progress_callback:
                progress_callback(0.1, "验证输入...")
            
            # 检查缓存
            cache_key = self._get_cache_key_for_custom(text, user_prompt, system_prompt)
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                logger.info("使用缓存的处理结果")
                if progress_callback:
                    progress_callback(1.0, "处理完成（来自缓存）")
                return True, cached_result, None
            
            if progress_callback:
                progress_callback(0.2, "开始AI处理...")
            
            # 使用AI处理文本
            success, processed_text, error = self.client.process_text(
                text=text,
                prompt=user_prompt,
                system_prompt=system_prompt
            )
            
            # 缓存结果
            if success and processed_text and self.use_cache:
                self._cache_result(cache_key, processed_text)
            
            if progress_callback:
                if success:
                    progress_callback(1.0, "处理完成")
                else:
                    progress_callback(0.2, f"处理失败: {error}")
            
            return success, processed_text, error
        
        except Exception as e:
            logger.exception("自定义提示词处理异常")
            error_msg = f"处理过程发生错误: {str(e)}"
            if progress_callback:
                progress_callback(0.0, error_msg)
            return False, None, error_msg
    
    def _get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """获取模板（使用统一配置系统）"""
        try:
            # 使用统一的配置系统获取提示词
            template = config.get_prompt(template_id)
            if template:
                return template
            
            # 为了向后兼容，检查是否有 custom_ 前缀
            if template_id.startswith('custom_'):
                custom_id = template_id.replace('custom_', '')
                template = config.get_prompt(custom_id)
                if template:
                    return template
            
            logger.warning(f"模板未找到: {template_id}")
            return None
        
        except Exception as e:
            logger.error(f"获取模板异常: {e}")
            return None
    
    def get_available_templates(self) -> Dict[str, Dict[str, Any]]:
        """获取所有可用模板"""
        return config.get_all_prompts()
    
    def get_template_categories(self) -> List[str]:
        """获取模板分类"""
        return config.get_prompt_categories()
    
    def search_templates(self, keyword: str) -> Dict[str, Dict[str, Any]]:
        """搜索模板"""
        return config.search_prompts(keyword)
    
    def _get_cache_key(self, text: str, template_id: str) -> str:
        """生成缓存键"""
        import hashlib
        
        try:
            # 生成文本的哈希
            text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()[:16]
            return f"ai_process_{template_id}_{text_hash}"
        except Exception as e:
            logger.warning(f"生成缓存键失败: {e}")
            return f"ai_process_{template_id}_{len(text)}"
    
    def _get_cache_key_for_custom(self, text: str, user_prompt: str, system_prompt: Optional[str] = None) -> str:
        """为自定义提示词生成缓存键"""
        import hashlib
        
        try:
            # 合并所有输入生成哈希
            combined = f"{text}|{user_prompt}|{system_prompt or ''}"
            combined_hash = hashlib.md5(combined.encode('utf-8')).hexdigest()[:16]
            return f"ai_process_custom_{combined_hash}"
        except Exception as e:
            logger.warning(f"生成自定义缓存键失败: {e}")
            return f"ai_process_custom_{len(text)}_{len(user_prompt)}"
    
    def _get_cached_result(self, cache_key: str) -> Optional[str]:
        """获取缓存的处理结果"""
        if not self.use_cache:
            return None
        
        try:
            cached_result = cache.get(cache_key)
            if cached_result and isinstance(cached_result, str):
                logger.debug(f"找到缓存的处理结果: {len(cached_result)} 字符")
                return cached_result
        except Exception as e:
            logger.warning(f"获取缓存处理结果失败: {e}")
        
        return None
    
    def _cache_result(self, cache_key: str, result: str):
        """缓存处理结果"""
        if not self.use_cache:
            return
        
        try:
            cache.set(cache_key, result)
            logger.debug(f"处理结果已缓存: {len(result)} 字符")
        except Exception as e:
            logger.warning(f"缓存处理结果失败: {e}")
    
    def get_available_templates(self) -> Dict[str, Dict[str, Any]]:
        """获取所有可用的模板"""
        try:
            available_templates = {}
            
            # 内置模板
            builtin_templates = templates.get_all_templates()
            for tid, template in builtin_templates.items():
                available_templates[tid] = {
                    'id': tid,
                    'name': template.get('name', ''),
                    'description': template.get('description', ''),
                    'category': template.get('category', ''),
                    'tags': template.get('tags', []),
                    'type': 'builtin'
                }
            
            # 自定义模板
            custom_templates = custom_prompts.get_all_prompts()
            for cid, template in custom_templates.items():
                template_id = f'custom_{cid}'
                available_templates[template_id] = {
                    'id': template_id,
                    'name': template.get('name', ''),
                    'description': template.get('description', ''),
                    'category': '自定义',
                    'tags': template.get('tags', []),
                    'type': 'custom',
                    'usage_count': template.get('usage_count', 0)
                }
            
            return available_templates
        
        except Exception as e:
            logger.error(f"获取可用模板失败: {e}")
            return {}
    
    def search_templates(self, keyword: str) -> Dict[str, Dict[str, Any]]:
        """搜索模板"""
        try:
            results = {}
            
            # 搜索内置模板
            builtin_results = templates.search_templates(keyword)
            for tid, template in builtin_results.items():
                results[tid] = {
                    'id': tid,
                    'name': template.get('name', ''),
                    'description': template.get('description', ''),
                    'category': template.get('category', ''),
                    'tags': template.get('tags', []),
                    'type': 'builtin'
                }
            
            # 搜索自定义模板
            custom_results = custom_prompts.search_prompts(keyword)
            for cid, template in custom_results.items():
                template_id = f'custom_{cid}'
                results[template_id] = {
                    'id': template_id,
                    'name': template.get('name', ''),
                    'description': template.get('description', ''),
                    'category': '自定义',
                    'tags': template.get('tags', []),
                    'type': 'custom',
                    'usage_count': template.get('usage_count', 0)
                }
            
            return results
        
        except Exception as e:
            logger.error(f"搜索模板失败: {e}")
            return {}
    
    def get_templates_by_category(self, category: str) -> Dict[str, Dict[str, Any]]:
        """按分类获取模板"""
        try:
            results = {}
            
            # 内置模板
            if category != '自定义':
                builtin_results = templates.get_templates_by_category(category)
                for tid, template in builtin_results.items():
                    results[tid] = {
                        'id': tid,
                        'name': template.get('name', ''),
                        'description': template.get('description', ''),
                        'category': template.get('category', ''),
                        'tags': template.get('tags', []),
                        'type': 'builtin'
                    }
            
            # 自定义模板
            if category == '自定义':
                custom_templates = custom_prompts.get_all_prompts()
                for cid, template in custom_templates.items():
                    template_id = f'custom_{cid}'
                    results[template_id] = {
                        'id': template_id,
                        'name': template.get('name', ''),
                        'description': template.get('description', ''),
                        'category': '自定义',
                        'tags': template.get('tags', []),
                        'type': 'custom',
                        'usage_count': template.get('usage_count', 0)
                    }
            
            return results
        
        except Exception as e:
            logger.error(f"按分类获取模板失败: {e}")
            return {}
    
    def get_popular_templates(self, limit: int = 10) -> Dict[str, Dict[str, Any]]:
        """获取热门模板"""
        try:
            results = {}
            
            # 获取使用次数最多的自定义模板
            popular_custom = custom_prompts.get_popular_prompts(limit)
            for cid, template in popular_custom.items():
                if template.get('usage_count', 0) > 0:
                    template_id = f'custom_{cid}'
                    results[template_id] = {
                        'id': template_id,
                        'name': template.get('name', ''),
                        'description': template.get('description', ''),
                        'category': '自定义',
                        'tags': template.get('tags', []),
                        'type': 'custom',
                        'usage_count': template.get('usage_count', 0)
                    }
            
            # 如果自定义模板不够，添加一些常用的内置模板
            if len(results) < limit:
                builtin_popular = ['meeting_notes', 'study_notes', 'content_summary', 'custom_cleanup']
                for tid in builtin_popular:
                    if len(results) >= limit:
                        break
                    template = templates.get_template(tid)
                    if template:
                        results[tid] = {
                            'id': tid,
                            'name': template.get('name', ''),
                            'description': template.get('description', ''),
                            'category': template.get('category', ''),
                            'tags': template.get('tags', []),
                            'type': 'builtin'
                        }
            
            return results
        
        except Exception as e:
            logger.error(f"获取热门模板失败: {e}")
            return {}
    
    def validate_setup(self) -> Tuple[bool, List[str]]:
        """验证AI处理设置"""
        issues = []
        
        try:
            # 检查API密钥
            api_key_valid, api_error = self.client.validate_api_key()
            if not api_key_valid:
                issues.append(f"DeepSeek API密钥无效: {api_error}")
            
            # 检查网络连接
            from ..utils.api_utils import APIUtils
            if not APIUtils.is_network_available():
                issues.append("网络连接不可用")
            
            # 检查模板加载
            templates_count = len(templates.get_all_templates())
            if templates_count == 0:
                issues.append("内置模板加载失败")
            
            # 检查缓存系统
            if self.use_cache:
                try:
                    cache.set('test_ai_key', 'test_value', memory_only=True)
                    test_value = cache.get('test_ai_key')
                    if test_value != 'test_value':
                        issues.append("缓存系统异常")
                except Exception as e:
                    issues.append(f"缓存系统错误: {str(e)}")
            
            success = len(issues) == 0
            if success:
                logger.info("AI文本处理设置验证通过")
            else:
                logger.warning(f"AI文本处理设置存在问题: {issues}")
            
            return success, issues
        
        except Exception as e:
            logger.exception("验证AI处理设置异常")
            issues.append(f"验证过程发生错误: {str(e)}")
            return False, issues
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """获取处理统计信息"""
        try:
            cache_info = cache.get_cache_size()
            custom_stats = custom_prompts.get_statistics()
            
            stats = {
                'cache_enabled': self.use_cache,
                'cache_size_mb': cache_info.get('total_size_mb', 0),
                'cached_items': cache_info.get('file_count', 0),
                'api_configured': bool(self.client.api_key),
                'builtin_templates': len(templates.get_all_templates()),
                'custom_templates': custom_stats.get('total_count', 0),
                'total_custom_usage': custom_stats.get('total_usage', 0),
                'model_info': {
                    'model': self.client.model,
                    'max_tokens': self.client.max_tokens,
                    'temperature': self.client.temperature
                }
            }
            
            return stats
        except Exception as e:
            logger.error(f"获取处理统计信息失败: {e}")
            return {}
    
    def clear_cache(self) -> bool:
        """清理处理缓存"""
        try:
            return cache.clear()
        except Exception as e:
            logger.error(f"清理处理缓存失败: {e}")
            return False