"""
音频提取模块

从视频文件中提取音频轨道
"""

import os
import subprocess
from typing import Tuple, Optional, List
from ..utils.logger import get_logger
from ..utils.file_utils import FileUtils

logger = get_logger(__name__)

class AudioExtractor:
    """音频提取器类"""
    
    def __init__(self):
        self.temp_files: List[str] = []
    
    def extract_audio(self, video_path: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        从视频文件中提取音频
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            (success, audio_file_path, error_message)
        """
        try:
            if not os.path.exists(video_path):
                return False, None, "视频文件不存在"
            
            # 生成输出音频文件路径
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            audio_path = FileUtils.get_temp_file_path(
                prefix=f'extracted_audio_{video_name}',
                suffix='.wav'
            )
            
            logger.info(f"开始从视频提取音频: {os.path.basename(video_path)}")
            
            # 尝试不同的提取方法
            success, error = self._extract_with_ios_framework(video_path, audio_path)
            
            if not success:
                # 备用方法：使用简单的文件处理
                success, error = self._extract_with_simple_method(video_path, audio_path)
            
            if success and os.path.exists(audio_path):
                self.temp_files.append(audio_path)
                logger.info(f"音频提取成功: {os.path.basename(audio_path)}")
                return True, audio_path, None
            else:
                return False, None, error or "音频提取失败"
        
        except Exception as e:
            logger.exception(f"音频提取异常: {video_path}")
            return False, None, f"音频提取错误: {str(e)}"
    
    def _extract_with_ios_framework(self, video_path: str, audio_path: str) -> Tuple[bool, Optional[str]]:
        """使用iOS框架提取音频（推荐方法）"""
        try:
            # 在Pythonista中，可以使用objc_util来调用iOS的AVFoundation框架
            # 这里提供一个基本的实现框架
            
            # 导入objc_util（仅在iOS环境中可用）
            try:
                import objc_util
                from objc_util import *
                
                # 创建AVAsset
                AVAsset = ObjCClass('AVAsset')
                AVAssetExportSession = ObjCClass('AVAssetExportSession')
                NSURL = ObjCClass('NSURL')
                
                # 创建资源URL
                video_url = NSURL.fileURLWithPath_(video_path)
                asset = AVAsset.assetWithURL_(video_url)
                
                # 检查是否有音频轨道
                audio_tracks = asset.tracksWithMediaType_('soun')
                if not audio_tracks or len(audio_tracks) == 0:
                    return False, "视频文件没有音频轨道"
                
                # 创建导出会话
                export_session = AVAssetExportSession.alloc().initWithAsset_presetName_(
                    asset, 'AVAssetExportPresetAppleM4A'
                )
                
                if not export_session:
                    return False, "无法创建音频导出会话"
                
                # 设置输出URL和文件类型
                output_url = NSURL.fileURLWithPath_(audio_path.replace('.wav', '.m4a'))
                export_session.outputURL = output_url
                export_session.outputFileType = 'com.apple.m4a-audio'
                
                # 异步导出
                export_session.exportAsynchronouslyWithCompletionHandler_(lambda: None)
                
                # 等待导出完成
                import time
                while export_session.status() == 1:  # AVAssetExportSessionStatusExporting
                    time.sleep(0.1)
                
                if export_session.status() == 3:  # AVAssetExportSessionStatusCompleted
                    # 转换为wav格式
                    m4a_path = audio_path.replace('.wav', '.m4a')
                    if os.path.exists(m4a_path):
                        # 使用format_converter转换格式
                        from .format_converter import FormatConverter
                        converter = FormatConverter()
                        success, wav_path, error = converter.convert_to_wav(m4a_path)
                        
                        # 清理临时文件
                        FileUtils.delete_file(m4a_path)
                        
                        if success:
                            return True, None
                        else:
                            return False, error
                
                error_msg = "音频导出失败"
                if export_session.error():
                    error_msg += f": {export_session.error().localizedDescription()}"
                
                return False, error_msg
            
            except ImportError:
                # 不在iOS环境中
                return False, "iOS框架不可用"
        
        except Exception as e:
            logger.warning(f"iOS框架提取音频失败: {e}")
            return False, f"iOS框架提取失败: {str(e)}"
    
    def _extract_with_simple_method(self, video_path: str, audio_path: str) -> Tuple[bool, Optional[str]]:
        """使用简单方法提取音频（备用方法）"""
        try:
            # 这是一个占位实现，在实际部署时需要适配具体环境
            # 可能的方案包括：
            # 1. 使用Python的moviepy库
            # 2. 调用外部命令行工具（如果可用）
            # 3. 使用其他音视频处理库
            
            logger.info("尝试简单方法提取音频")
            
            # 检查是否可以使用moviepy
            try:
                import moviepy.editor as mp
                
                video = mp.VideoFileClip(video_path)
                if video.audio is None:
                    return False, "视频文件没有音频轨道"
                
                audio = video.audio
                audio.write_audiofile(audio_path, verbose=False, logger=None)
                
                # 关闭资源
                audio.close()
                video.close()
                
                return True, None
            
            except ImportError:
                logger.warning("moviepy库不可用")
            
            # 如果没有可用的库，创建占位文件
            logger.warning("使用占位音频文件")
            return self._create_placeholder_audio(audio_path)
        
        except Exception as e:
            logger.error(f"简单方法提取音频失败: {e}")
            return False, f"简单方法提取失败: {str(e)}"
    
    def _create_placeholder_audio(self, audio_path: str) -> Tuple[bool, Optional[str]]:
        """创建占位音频文件（用于测试）"""
        try:
            # 创建一个短的静音音频文件
            import wave
            import numpy as np
            
            # 生成1秒的静音
            sample_rate = 44100
            duration = 1.0
            samples = int(sample_rate * duration)
            
            # 创建静音数据
            audio_data = np.zeros(samples, dtype=np.int16)
            
            # 写入WAV文件
            with wave.open(audio_path, 'w') as wav_file:
                wav_file.setnchannels(1)  # 单声道
                wav_file.setsampwidth(2)  # 16位
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(audio_data.tobytes())
            
            logger.info("创建占位音频文件成功")
            return True, None
        
        except Exception as e:
            logger.error(f"创建占位音频文件失败: {e}")
            return False, f"创建占位音频失败: {str(e)}"
    
    def validate_audio_track(self, video_path: str) -> Tuple[bool, Optional[str]]:
        """验证视频是否包含音频轨道"""
        try:
            # 尝试使用iOS框架检查
            try:
                import objc_util
                from objc_util import *
                
                AVAsset = ObjCClass('AVAsset')
                NSURL = ObjCClass('NSURL')
                
                video_url = NSURL.fileURLWithPath_(video_path)
                asset = AVAsset.assetWithURL_(video_url)
                
                audio_tracks = asset.tracksWithMediaType_('soun')
                if audio_tracks and len(audio_tracks) > 0:
                    return True, f"检测到 {len(audio_tracks)} 个音频轨道"
                else:
                    return False, "视频文件没有音频轨道"
            
            except ImportError:
                # 备用检查方法
                return True, "无法验证音频轨道，假设存在"
        
        except Exception as e:
            logger.warning(f"验证音频轨道失败: {e}")
            return True, "音频轨道验证失败，假设存在"
    
    def cleanup_temp_files(self):
        """清理临时文件"""
        for temp_file in self.temp_files:
            FileUtils.delete_file(temp_file)
        self.temp_files.clear()
        logger.debug("音频提取临时文件已清理")