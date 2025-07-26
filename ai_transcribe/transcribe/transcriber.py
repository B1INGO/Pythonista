"""
转录核心逻辑模块

协调转录流程和进度管理
"""

import os
from typing import Tuple, Optional, Callable, Dict, Any, List
from ..config import config
from ..utils.logger import get_logger
from ..utils.cache import cache
from ..utils.file_utils import FileUtils
from .siliconflow_client import SiliconFlowClient
from .segment_processor import SegmentProcessor

logger = get_logger(__name__)

class Transcriber:
    """转录器类"""
    
    def __init__(self):
        self.client = SiliconFlowClient()
        self.segment_processor = SegmentProcessor()
        self.use_cache = config.get('cache.enabled', True)
    
    def transcribe(
        self, 
        audio_path: str, 
        language: str = 'zh',
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        转录音频文件
        
        Args:
            audio_path: 音频文件路径
            language: 语言代码
            progress_callback: 进度回调函数 (progress: float, message: str)
            
        Returns:
            (success, transcribed_text, error_message)
        """
        try:
            if progress_callback:
                progress_callback(0.0, "开始转录...")
            
            # 验证文件
            if not os.path.exists(audio_path):
                return False, None, "音频文件不存在"
            
            # 检查缓存
            cache_key = self._get_cache_key(audio_path, language)
            cached_result = self._get_cached_transcription(cache_key)
            if cached_result:
                logger.info("使用缓存的转录结果")
                if progress_callback:
                    progress_callback(1.0, "转录完成（来自缓存）")
                return True, cached_result, None
            
            if progress_callback:
                progress_callback(0.1, "检查音频文件...")
            
            # 获取音频信息
            audio_info = self._get_audio_info(audio_path)
            logger.info(f"音频文件信息: {audio_info}")
            
            if progress_callback:
                progress_callback(0.2, "准备转录...")
            
            # 决定是否需要分段处理
            if self._should_split_audio(audio_path, audio_info):
                logger.info("音频文件较大，使用分段转录")
                success, text, error = self._transcribe_with_segments(
                    audio_path, language, progress_callback
                )
            else:
                logger.info("音频文件较小，直接转录")
                success, text, error = self._transcribe_single_file(
                    audio_path, language, progress_callback
                )
            
            # 缓存结果
            if success and text and self.use_cache:
                self._cache_transcription(cache_key, text)
            
            if progress_callback:
                if success:
                    progress_callback(1.0, "转录完成")
                else:
                    progress_callback(0.0, f"转录失败: {error}")
            
            return success, text, error
        
        except Exception as e:
            logger.exception(f"转录异常: {audio_path}")
            error_msg = f"转录过程发生错误: {str(e)}"
            if progress_callback:
                progress_callback(0.0, error_msg)
            return False, None, error_msg
    
    def _get_cache_key(self, audio_path: str, language: str) -> str:
        """生成缓存键"""
        try:
            file_hash = FileUtils.get_file_hash(audio_path)
            if file_hash:
                return f"transcribe_{file_hash}_{language}"
            else:
                # 备用键（基于文件名和大小）
                file_name = os.path.basename(audio_path)
                file_size = FileUtils.get_file_size_mb(audio_path)
                return f"transcribe_{file_name}_{file_size:.2f}mb_{language}"
        except Exception as e:
            logger.warning(f"生成缓存键失败: {e}")
            return f"transcribe_{os.path.basename(audio_path)}_{language}"
    
    def _get_cached_transcription(self, cache_key: str) -> Optional[str]:
        """获取缓存的转录结果"""
        if not self.use_cache:
            return None
        
        try:
            cached_text = cache.get(cache_key)
            if cached_text and isinstance(cached_text, str):
                logger.debug(f"找到缓存的转录结果: {len(cached_text)} 字符")
                return cached_text
        except Exception as e:
            logger.warning(f"获取缓存转录结果失败: {e}")
        
        return None
    
    def _cache_transcription(self, cache_key: str, text: str):
        """缓存转录结果"""
        if not self.use_cache:
            return
        
        try:
            cache.set(cache_key, text)
            logger.debug(f"转录结果已缓存: {len(text)} 字符")
        except Exception as e:
            logger.warning(f"缓存转录结果失败: {e}")
    
    def _get_audio_info(self, audio_path: str) -> Dict[str, Any]:
        """获取音频文件信息"""
        try:
            # 基本文件信息
            info = {
                'file_path': audio_path,
                'file_name': os.path.basename(audio_path),
                'file_size_mb': FileUtils.get_file_size_mb(audio_path),
                'extension': FileUtils.get_file_extension(audio_path)
            }
            
            # 尝试获取音频详细信息
            try:
                from ..core.format_converter import FormatConverter
                converter = FormatConverter()
                audio_details = converter.get_audio_info(audio_path)
                info.update(audio_details)
            except Exception as e:
                logger.debug(f"获取音频详细信息失败: {e}")
            
            return info
        except Exception as e:
            logger.warning(f"获取音频信息失败: {e}")
            return {'file_path': audio_path}
    
    def _should_split_audio(self, audio_path: str, audio_info: Dict[str, Any]) -> bool:
        """判断是否需要分段处理"""
        try:
            # 基于文件大小判断
            file_size_mb = audio_info.get('file_size_mb', 0)
            max_size_mb = config.get('transcribe.max_file_size_mb', 100)
            
            if file_size_mb > max_size_mb * 0.8:  # 80%阈值
                logger.info(f"文件大小 {file_size_mb:.1f}MB 超过阈值，需要分段")
                return True
            
            # 基于时长判断
            duration = audio_info.get('duration')
            if duration is not None:
                max_duration = config.get('transcribe.chunk_duration_seconds', 60) * 2
                if duration > max_duration:
                    logger.info(f"音频时长 {duration:.1f}秒 超过阈值，需要分段")
                    return True
            
            return False
        except Exception as e:
            logger.warning(f"判断是否分段失败: {e}")
            return False  # 出错时不分段
    
    def _transcribe_single_file(
        self, 
        audio_path: str, 
        language: str,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """转录单个文件"""
        try:
            if progress_callback:
                progress_callback(0.3, "正在上传音频文件...")
            
            # 调用API转录
            success, text, error = self.client.transcribe_audio(audio_path, language)
            
            if progress_callback:
                if success:
                    progress_callback(0.9, "转录完成，正在处理结果...")
                else:
                    progress_callback(0.3, f"转录失败: {error}")
            
            return success, text, error
        
        except Exception as e:
            logger.exception(f"单文件转录异常: {audio_path}")
            return False, None, f"单文件转录错误: {str(e)}"
    
    def _transcribe_with_segments(
        self, 
        audio_path: str, 
        language: str,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """分段转录音频文件"""
        try:
            if progress_callback:
                progress_callback(0.3, "正在分割音频文件...")
            
            # 分割音频
            success, segments, error = self.segment_processor.split_audio(
                audio_path, progress_callback
            )
            
            if not success or not segments:
                return False, None, error or "音频分割失败"
            
            logger.info(f"音频分割完成，共 {len(segments)} 个片段")
            
            if progress_callback:
                progress_callback(0.4, f"开始转录 {len(segments)} 个音频片段...")
            
            # 转录每个片段
            segment_results = []
            for i, segment_path in enumerate(segments):
                try:
                    logger.info(f"转录片段 {i+1}/{len(segments)}: {os.path.basename(segment_path)}")
                    
                    if progress_callback:
                        base_progress = 0.4 + (i / len(segments)) * 0.5
                        progress_callback(base_progress, f"转录片段 {i+1}/{len(segments)}...")
                    
                    result = self.client.transcribe_audio(segment_path, language)
                    segment_results.append(result)
                    
                    if result[0]:  # 成功
                        logger.debug(f"片段 {i+1} 转录成功")
                    else:
                        logger.warning(f"片段 {i+1} 转录失败: {result[2]}")
                
                except Exception as e:
                    logger.error(f"转录片段 {i+1} 异常: {e}")
                    segment_results.append((False, None, str(e)))
            
            if progress_callback:
                progress_callback(0.9, "合并转录结果...")
            
            # 合并结果
            success, merged_text, warning = self.segment_processor.merge_transcripts(segment_results)
            
            # 清理临时文件
            self.segment_processor.cleanup_temp_files()
            
            return success, merged_text, warning
        
        except Exception as e:
            logger.exception(f"分段转录异常: {audio_path}")
            # 确保清理临时文件
            try:
                self.segment_processor.cleanup_temp_files()
            except:
                pass
            return False, None, f"分段转录错误: {str(e)}"
    
    def validate_setup(self) -> Tuple[bool, List[str]]:
        """验证转录设置"""
        issues = []
        
        try:
            # 检查API密钥
            api_key_valid, api_error = self.client.validate_api_key()
            if not api_key_valid:
                issues.append(f"硅基流动API密钥无效: {api_error}")
            
            # 检查网络连接
            from ..utils.api_utils import APIUtils
            if not APIUtils.is_network_available():
                issues.append("网络连接不可用")
            
            # 检查缓存目录
            if self.use_cache:
                try:
                    cache.set('test_key', 'test_value', memory_only=True)
                    test_value = cache.get('test_key')
                    if test_value != 'test_value':
                        issues.append("缓存系统异常")
                except Exception as e:
                    issues.append(f"缓存系统错误: {str(e)}")
            
            success = len(issues) == 0
            if success:
                logger.info("转录设置验证通过")
            else:
                logger.warning(f"转录设置存在问题: {issues}")
            
            return success, issues
        
        except Exception as e:
            logger.exception("验证转录设置异常")
            issues.append(f"验证过程发生错误: {str(e)}")
            return False, issues
    
    def get_transcription_stats(self) -> Dict[str, Any]:
        """获取转录统计信息"""
        try:
            cache_info = cache.get_cache_size()
            
            stats = {
                'cache_enabled': self.use_cache,
                'cache_size_mb': cache_info.get('total_size_mb', 0),
                'cached_items': cache_info.get('file_count', 0),
                'memory_items': cache_info.get('memory_items', 0),
                'api_configured': bool(self.client.api_key),
                'chunk_duration': self.segment_processor.chunk_duration
            }
            
            return stats
        except Exception as e:
            logger.error(f"获取转录统计信息失败: {e}")
            return {}
    
    def clear_cache(self) -> bool:
        """清理转录缓存"""
        try:
            return cache.clear()
        except Exception as e:
            logger.error(f"清理转录缓存失败: {e}")
            return False
    
    def cleanup(self):
        """清理资源"""
        try:
            self.segment_processor.cleanup_temp_files()
            logger.debug("转录器资源清理完成")
        except Exception as e:
            logger.error(f"清理转录器资源失败: {e}")