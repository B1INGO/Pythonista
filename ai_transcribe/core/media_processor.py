"""
媒体处理器模块

支持多种音视频格式的预处理
"""

import os
from typing import Tuple, Optional, Dict, Any
from ..utils.logger import get_logger
from ..utils.file_utils import FileUtils
from .audio_extractor import AudioExtractor
from .format_converter import FormatConverter

logger = get_logger(__name__)

class MediaProcessor:
    """媒体处理器类"""
    
    def __init__(self):
        self.audio_extractor = AudioExtractor()
        self.format_converter = FormatConverter()
    
    def process_media_file(self, file_path: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        处理媒体文件，返回处理后的音频文件路径
        
        Args:
            file_path: 输入文件路径
            
        Returns:
            (success, audio_file_path, error_message)
        """
        try:
            # 验证文件
            is_valid, message = FileUtils.validate_file(file_path)
            if not is_valid:
                return False, None, message
            
            # 检查文件类型
            is_supported, file_type = FileUtils.is_supported_format(file_path)
            if not is_supported:
                return False, None, f"不支持的文件格式"
            
            logger.info(f"开始处理{file_type}文件: {os.path.basename(file_path)}")
            
            if file_type == 'audio':
                # 音频文件：检查格式是否需要转换
                return self._process_audio_file(file_path)
            elif file_type == 'video':
                # 视频文件：提取音频
                return self._process_video_file(file_path)
            else:
                return False, None, f"未知的文件类型: {file_type}"
        
        except Exception as e:
            logger.exception(f"处理媒体文件异常: {file_path}")
            return False, None, f"处理文件时发生错误: {str(e)}"
    
    def _process_audio_file(self, file_path: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """处理音频文件"""
        try:
            # 检查是否需要格式转换
            ext = FileUtils.get_file_extension(file_path)
            
            # 支持的格式直接返回
            if ext in ['.wav', '.mp3']:
                logger.info(f"音频文件格式无需转换: {ext}")
                return True, file_path, None
            
            # 需要转换的格式
            logger.info(f"音频文件需要格式转换: {ext} -> .wav")
            return self.format_converter.convert_to_wav(file_path)
        
        except Exception as e:
            logger.exception(f"处理音频文件异常: {file_path}")
            return False, None, f"处理音频文件错误: {str(e)}"
    
    def _process_video_file(self, file_path: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """处理视频文件"""
        try:
            logger.info(f"从视频文件提取音频: {os.path.basename(file_path)}")
            return self.audio_extractor.extract_audio(file_path)
        
        except Exception as e:
            logger.exception(f"处理视频文件异常: {file_path}")
            return False, None, f"处理视频文件错误: {str(e)}"
    
    def get_media_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """获取媒体文件信息"""
        try:
            if not os.path.exists(file_path):
                return None
            
            is_supported, file_type = FileUtils.is_supported_format(file_path)
            
            info = {
                'file_path': file_path,
                'file_name': os.path.basename(file_path),
                'file_size_mb': FileUtils.get_file_size_mb(file_path),
                'file_type': file_type,
                'is_supported': is_supported,
                'extension': FileUtils.get_file_extension(file_path)
            }
            
            # 尝试获取更详细的信息
            if file_type == 'audio':
                info.update(self._get_audio_info(file_path))
            elif file_type == 'video':
                info.update(self._get_video_info(file_path))
            
            return info
        
        except Exception as e:
            logger.error(f"获取媒体信息失败 {file_path}: {e}")
            return None
    
    def _get_audio_info(self, file_path: str) -> Dict[str, Any]:
        """获取音频文件详细信息"""
        # 在实际的Pythonista环境中，可以使用iOS的AudioToolbox框架
        # 这里提供基本实现
        try:
            # 基本信息
            info = {
                'duration_seconds': None,
                'sample_rate': None,
                'channels': None,
                'bit_rate': None
            }
            
            # 在实际部署时，可以集成音频分析库
            # 例如使用Python的librosa库或iOS原生框架
            
            return info
        
        except Exception as e:
            logger.warning(f"获取音频详细信息失败: {e}")
            return {}
    
    def _get_video_info(self, file_path: str) -> Dict[str, Any]:
        """获取视频文件详细信息"""
        try:
            # 基本信息
            info = {
                'duration_seconds': None,
                'resolution': None,
                'frame_rate': None,
                'video_codec': None,
                'audio_codec': None,
                'has_audio': True  # 假设视频都有音频轨道
            }
            
            # 在实际部署时，可以集成视频分析库
            # 例如使用Python的moviepy库或iOS的AVFoundation框架
            
            return info
        
        except Exception as e:
            logger.warning(f"获取视频详细信息失败: {e}")
            return {}
    
    def cleanup_temp_files(self):
        """清理临时文件"""
        try:
            self.audio_extractor.cleanup_temp_files()
            self.format_converter.cleanup_temp_files()
            logger.info("临时文件清理完成")
        except Exception as e:
            logger.error(f"清理临时文件失败: {e}")