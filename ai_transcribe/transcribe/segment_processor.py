"""
分段处理器模块

支持长音频的分段转录
"""

import os
import math
from typing import List, Tuple, Optional, Callable, Dict, Any
from ..config import config
from ..utils.logger import get_logger
from ..utils.file_utils import FileUtils

logger = get_logger(__name__)

class SegmentProcessor:
    """音频分段处理器"""
    
    def __init__(self):
        self.chunk_duration = config.get('transcribe.chunk_duration_seconds', 60)
        self.temp_files: List[str] = []
    
    def split_audio(self, audio_path: str, progress_callback: Optional[Callable[[float, str], None]] = None) -> Tuple[bool, List[str], Optional[str]]:
        """
        将长音频文件分割为多个段
        
        Args:
            audio_path: 音频文件路径
            progress_callback: 进度回调函数
            
        Returns:
            (success, segment_paths, error_message)
        """
        try:
            if not os.path.exists(audio_path):
                return False, [], "音频文件不存在"
            
            # 获取音频信息
            audio_info = self._get_audio_duration(audio_path)
            if not audio_info or audio_info['duration'] is None:
                logger.warning("无法获取音频时长，使用默认分割策略")
                return self._split_by_file_size(audio_path, progress_callback)
            
            duration = audio_info['duration']
            logger.info(f"音频时长: {duration:.1f}秒")
            
            # 如果音频较短，不需要分割
            if duration <= self.chunk_duration:
                logger.info("音频时长较短，无需分割")
                return True, [audio_path], None
            
            # 计算分段数量
            num_segments = math.ceil(duration / self.chunk_duration)
            logger.info(f"将音频分割为 {num_segments} 段")
            
            if progress_callback:
                progress_callback(0.0, "开始分割音频...")
            
            # 执行分割
            segments = self._perform_audio_split(audio_path, duration, num_segments, progress_callback)
            
            if segments:
                logger.info(f"音频分割完成，生成 {len(segments)} 个片段")
                self.temp_files.extend(segments)
                return True, segments, None
            else:
                return False, [], "音频分割失败"
        
        except Exception as e:
            logger.exception(f"音频分割异常: {audio_path}")
            return False, [], f"分割音频时发生错误: {str(e)}"
    
    def _get_audio_duration(self, audio_path: str) -> Optional[Dict[str, Any]]:
        """获取音频时长信息"""
        try:
            # 尝试使用不同的方法获取音频时长
            
            # 方法1: 使用iOS框架
            duration = self._get_duration_with_ios(audio_path)
            if duration is not None:
                return {'duration': duration, 'method': 'ios'}
            
            # 方法2: 使用Python库
            duration = self._get_duration_with_python(audio_path)
            if duration is not None:
                return {'duration': duration, 'method': 'python'}
            
            # 方法3: 估算（基于文件大小）
            duration = self._estimate_duration(audio_path)
            if duration is not None:
                return {'duration': duration, 'method': 'estimated'}
            
            return None
        
        except Exception as e:
            logger.error(f"获取音频时长失败: {e}")
            return None
    
    def _get_duration_with_ios(self, audio_path: str) -> Optional[float]:
        """使用iOS框架获取音频时长"""
        try:
            import objc_util
            from objc_util import *
            
            AVAsset = ObjCClass('AVAsset')
            NSURL = ObjCClass('NSURL')
            
            audio_url = NSURL.fileURLWithPath_(audio_path)
            asset = AVAsset.assetWithURL_(audio_url)
            
            # 获取时长
            duration_seconds = asset.duration().value / asset.duration().timescale
            
            logger.debug(f"iOS框架获取音频时长: {duration_seconds}秒")
            return float(duration_seconds)
        
        except ImportError:
            logger.debug("iOS框架不可用")
            return None
        except Exception as e:
            logger.debug(f"iOS框架获取时长失败: {e}")
            return None
    
    def _get_duration_with_python(self, audio_path: str) -> Optional[float]:
        """使用Python库获取音频时长"""
        try:
            # 尝试使用wave库
            if audio_path.endswith('.wav'):
                import wave
                with wave.open(audio_path, 'rb') as wav_file:
                    frames = wav_file.getnframes()
                    rate = wav_file.getframerate()
                    duration = frames / float(rate)
                    logger.debug(f"wave库获取音频时长: {duration}秒")
                    return duration
            
            # 尝试使用pydub
            try:
                from pydub import AudioSegment
                audio = AudioSegment.from_file(audio_path)
                duration = len(audio) / 1000.0  # 转换为秒
                logger.debug(f"pydub库获取音频时长: {duration}秒")
                return duration
            except ImportError:
                logger.debug("pydub库不可用")
            
            return None
        
        except Exception as e:
            logger.debug(f"Python库获取时长失败: {e}")
            return None
    
    def _estimate_duration(self, audio_path: str) -> Optional[float]:
        """根据文件大小估算音频时长"""
        try:
            file_size_mb = FileUtils.get_file_size_mb(audio_path)
            
            # 粗略估算：假设每分钟音频约1MB（可调整）
            estimated_duration = file_size_mb * 60  # 秒
            
            logger.debug(f"根据文件大小估算音频时长: {estimated_duration}秒")
            return estimated_duration
        
        except Exception as e:
            logger.debug(f"估算音频时长失败: {e}")
            return None
    
    def _perform_audio_split(self, audio_path: str, duration: float, num_segments: int, progress_callback: Optional[Callable[[float, str], None]] = None) -> List[str]:
        """执行音频分割"""
        try:
            segments = []
            segment_duration = duration / num_segments
            
            # 尝试使用不同的分割方法
            segments = self._split_with_ios(audio_path, segment_duration, num_segments, progress_callback)
            
            if not segments:
                segments = self._split_with_python(audio_path, segment_duration, num_segments, progress_callback)
            
            if not segments:
                segments = self._split_by_file_size(audio_path, progress_callback)[1]
            
            return segments
        
        except Exception as e:
            logger.error(f"执行音频分割失败: {e}")
            return []
    
    def _split_with_ios(self, audio_path: str, segment_duration: float, num_segments: int, progress_callback: Optional[Callable[[float, str], None]] = None) -> List[str]:
        """使用iOS框架分割音频"""
        try:
            import objc_util
            from objc_util import *
            
            segments = []
            base_name = os.path.splitext(os.path.basename(audio_path))[0]
            
            AVAsset = ObjCClass('AVAsset')
            AVAssetExportSession = ObjCClass('AVAssetExportSession')
            NSURL = ObjCClass('NSURL')
            CMTime = ObjCClass('CMTime')
            CMTimeRange = ObjCClass('CMTimeRange')
            
            # 创建资源
            audio_url = NSURL.fileURLWithPath_(audio_path)
            asset = AVAsset.assetWithURL_(audio_url)
            
            for i in range(num_segments):
                try:
                    # 计算时间范围
                    start_time = i * segment_duration
                    end_time = min((i + 1) * segment_duration, asset.duration().value / asset.duration().timescale)
                    
                    # 创建输出路径
                    segment_path = FileUtils.get_temp_file_path(
                        prefix=f'{base_name}_segment_{i:03d}',
                        suffix='.m4a'
                    )
                    
                    # 创建导出会话
                    export_session = AVAssetExportSession.alloc().initWithAsset_presetName_(
                        asset, 'AVAssetExportPresetAppleM4A'
                    )
                    
                    if export_session:
                        # 设置时间范围
                        start_cmtime = CMTime.CMTimeMakeWithSeconds_preferredTimescale_(start_time, 600)
                        duration_cmtime = CMTime.CMTimeMakeWithSeconds_preferredTimescale_(end_time - start_time, 600)
                        time_range = CMTimeRange.CMTimeRangeMake_(start_cmtime, duration_cmtime)
                        
                        export_session.timeRange = time_range
                        export_session.outputURL = NSURL.fileURLWithPath_(segment_path)
                        export_session.outputFileType = 'com.apple.m4a-audio'
                        
                        # 导出音频片段
                        export_session.exportAsynchronouslyWithCompletionHandler_(lambda: None)
                        
                        # 等待导出完成
                        import time
                        while export_session.status() == 1:  # AVAssetExportSessionStatusExporting
                            time.sleep(0.1)
                        
                        if export_session.status() == 3:  # AVAssetExportSessionStatusCompleted
                            segments.append(segment_path)
                            logger.debug(f"分割片段完成: {os.path.basename(segment_path)}")
                        else:
                            logger.warning(f"分割片段失败: segment {i}")
                    
                    # 更新进度
                    if progress_callback:
                        progress = (i + 1) / num_segments
                        progress_callback(progress * 0.8, f"正在分割音频片段 {i+1}/{num_segments}")
                
                except Exception as e:
                    logger.warning(f"分割片段 {i} 失败: {e}")
            
            logger.info(f"iOS框架分割完成，生成 {len(segments)} 个片段")
            return segments
        
        except ImportError:
            logger.debug("iOS框架不可用")
            return []
        except Exception as e:
            logger.error(f"iOS框架分割失败: {e}")
            return []
    
    def _split_with_python(self, audio_path: str, segment_duration: float, num_segments: int, progress_callback: Optional[Callable[[float, str], None]] = None) -> List[str]:
        """使用Python库分割音频"""
        try:
            from pydub import AudioSegment
            
            # 加载音频
            audio = AudioSegment.from_file(audio_path)
            segments = []
            base_name = os.path.splitext(os.path.basename(audio_path))[0]
            
            segment_length_ms = int(segment_duration * 1000)  # 转换为毫秒
            
            for i in range(num_segments):
                try:
                    start_ms = i * segment_length_ms
                    end_ms = min((i + 1) * segment_length_ms, len(audio))
                    
                    # 提取片段
                    segment = audio[start_ms:end_ms]
                    
                    # 保存片段
                    segment_path = FileUtils.get_temp_file_path(
                        prefix=f'{base_name}_segment_{i:03d}',
                        suffix='.wav'
                    )
                    
                    segment.export(segment_path, format="wav")
                    segments.append(segment_path)
                    
                    logger.debug(f"分割片段完成: {os.path.basename(segment_path)}")
                    
                    # 更新进度
                    if progress_callback:
                        progress = (i + 1) / num_segments
                        progress_callback(progress * 0.8, f"正在分割音频片段 {i+1}/{num_segments}")
                
                except Exception as e:
                    logger.warning(f"分割片段 {i} 失败: {e}")
            
            logger.info(f"Python库分割完成，生成 {len(segments)} 个片段")
            return segments
        
        except ImportError:
            logger.debug("pydub库不可用")
            return []
        except Exception as e:
            logger.error(f"Python库分割失败: {e}")
            return []
    
    def _split_by_file_size(self, audio_path: str, progress_callback: Optional[Callable[[float, str], None]] = None) -> Tuple[bool, List[str]]:
        """按文件大小分割（备用方法）"""
        try:
            file_size_mb = FileUtils.get_file_size_mb(audio_path)
            
            # 如果文件小于设定阈值，不分割
            max_chunk_size_mb = 25  # 每个片段最大25MB
            if file_size_mb <= max_chunk_size_mb:
                return True, [audio_path]
            
            # 简单分割策略：复制原文件为多个片段（占位实现）
            num_chunks = math.ceil(file_size_mb / max_chunk_size_mb)
            segments = []
            base_name = os.path.splitext(os.path.basename(audio_path))[0]
            
            for i in range(num_chunks):
                segment_path = FileUtils.get_temp_file_path(
                    prefix=f'{base_name}_chunk_{i:03d}',
                    suffix=FileUtils.get_file_extension(audio_path)
                )
                
                # 简单复制（实际应用中需要真正的分割）
                if FileUtils.copy_file(audio_path, segment_path):
                    segments.append(segment_path)
                
                if progress_callback:
                    progress = (i + 1) / num_chunks
                    progress_callback(progress * 0.8, f"正在准备音频片段 {i+1}/{num_chunks}")
            
            logger.info(f"按文件大小分割完成，生成 {len(segments)} 个片段")
            return True, segments
        
        except Exception as e:
            logger.error(f"按文件大小分割失败: {e}")
            return False, []
    
    def merge_transcripts(self, segment_results: List[Tuple[bool, Optional[str], Optional[str]]]) -> Tuple[bool, Optional[str], Optional[str]]:
        """合并多个片段的转录结果"""
        try:
            successful_results = []
            failed_count = 0
            
            for i, (success, text, error) in enumerate(segment_results):
                if success and text:
                    successful_results.append(text.strip())
                else:
                    failed_count += 1
                    logger.warning(f"片段 {i} 转录失败: {error}")
            
            if not successful_results:
                return False, None, "所有音频片段转录都失败了"
            
            # 合并文本
            merged_text = '\n'.join(successful_results)
            
            logger.info(f"转录结果合并完成，成功: {len(successful_results)} 个片段，失败: {failed_count} 个片段")
            
            if failed_count > 0:
                warning_msg = f"注意：有 {failed_count} 个音频片段转录失败"
                return True, merged_text, warning_msg
            else:
                return True, merged_text, None
        
        except Exception as e:
            logger.exception("合并转录结果异常")
            return False, None, f"合并转录结果时发生错误: {str(e)}"
    
    def cleanup_temp_files(self):
        """清理临时文件"""
        for temp_file in self.temp_files:
            FileUtils.delete_file(temp_file)
        self.temp_files.clear()
        logger.debug("分段处理临时文件已清理")