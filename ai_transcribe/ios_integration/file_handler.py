"""
文件处理器模块

支持"打开方式"直接调用和文件关联处理
"""

import os
import shutil
from typing import Tuple, Optional, List, Dict, Any
from ..utils.logger import get_logger
from ..utils.file_utils import FileUtils

logger = get_logger(__name__)

class FileHandler:
    """文件处理器类"""
    
    def __init__(self):
        self.supported_schemes = ['file', 'pythonista', 'ai-transcribe']
        self.temp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'temp_files')
        FileUtils.ensure_directory(self.temp_dir)
    
    def handle_file_open(self, file_path: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        处理通过"打开方式"调用的文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            (success, processed_file_path, error_message)
        """
        try:
            if not file_path:
                return False, None, "文件路径为空"
            
            logger.info(f"处理文件打开请求: {file_path}")
            
            # 验证文件
            is_valid, validation_msg = FileUtils.validate_file(file_path)
            if not is_valid:
                return False, None, validation_msg
            
            # 检查文件是否在应用的沙盒内
            processed_path = self._ensure_file_accessible(file_path)
            if not processed_path:
                return False, None, "无法访问文件"
            
            logger.info(f"文件处理成功: {os.path.basename(processed_path)}")
            return True, processed_path, None
        
        except Exception as e:
            logger.exception(f"处理文件打开异常: {file_path}")
            return False, None, f"处理文件时发生错误: {str(e)}"
    
    def handle_multiple_files(self, file_paths: List[str]) -> Tuple[bool, List[str], Optional[str]]:
        """
        处理多个文件
        
        Args:
            file_paths: 文件路径列表
            
        Returns:
            (success, processed_file_paths, error_message)
        """
        try:
            if not file_paths:
                return False, [], "文件路径列表为空"
            
            logger.info(f"处理多个文件: {len(file_paths)} 个")
            
            processed_files = []
            failed_files = []
            
            for file_path in file_paths:
                try:
                    success, processed_path, error = self.handle_file_open(file_path)
                    if success and processed_path:
                        processed_files.append(processed_path)
                    else:
                        failed_files.append(f"{os.path.basename(file_path)}: {error}")
                        logger.warning(f"处理文件失败 {file_path}: {error}")
                
                except Exception as e:
                    failed_files.append(f"{os.path.basename(file_path)}: {str(e)}")
                    logger.error(f"处理文件异常 {file_path}: {e}")
            
            if processed_files:
                error_msg = None
                if failed_files:
                    error_msg = f"部分文件处理失败: {'; '.join(failed_files)}"
                return True, processed_files, error_msg
            else:
                return False, [], f"所有文件处理都失败了: {'; '.join(failed_files)}"
        
        except Exception as e:
            logger.exception("处理多个文件异常")
            return False, [], f"处理多个文件时发生错误: {str(e)}"
    
    def _ensure_file_accessible(self, file_path: str) -> Optional[str]:
        """确保文件可访问"""
        try:
            # 检查文件是否存在且可读
            if not os.path.exists(file_path) or not os.access(file_path, os.R_OK):
                logger.warning(f"文件不存在或无法读取: {file_path}")
                return None
            
            # 检查是否在应用的沙盒内
            app_documents_dir = self._get_app_documents_dir()
            
            # 如果文件已经在应用目录内，直接返回
            if file_path.startswith(app_documents_dir):
                return file_path
            
            # 如果文件在外部，复制到应用目录
            return self._copy_to_app_directory(file_path)
        
        except Exception as e:
            logger.error(f"确保文件可访问失败: {e}")
            return None
    
    def _get_app_documents_dir(self) -> str:
        """获取应用的Documents目录"""
        try:
            # 在Pythonista中获取Documents目录
            import os
            
            # 尝试获取Pythonista的Documents目录
            pythonista_docs = os.path.expanduser('~/Documents')
            if os.path.exists(pythonista_docs):
                return pythonista_docs
            
            # 备用方案：当前工作目录
            return os.getcwd()
        
        except Exception as e:
            logger.error(f"获取应用目录失败: {e}")
            return os.getcwd()
    
    def _copy_to_app_directory(self, source_path: str) -> Optional[str]:
        """复制文件到应用目录"""
        try:
            filename = os.path.basename(source_path)
            safe_filename = FileUtils.get_safe_filename(f"imported_{filename}")
            
            # 目标路径
            dest_path = os.path.join(self.temp_dir, safe_filename)
            
            # 如果目标文件已存在，添加序号
            counter = 1
            base_dest_path = dest_path
            while os.path.exists(dest_path):
                name, ext = os.path.splitext(base_dest_path)
                dest_path = f"{name}_{counter}{ext}"
                counter += 1
            
            # 复制文件
            if FileUtils.copy_file(source_path, dest_path):
                logger.info(f"文件已复制到应用目录: {dest_path}")
                return dest_path
            else:
                return None
        
        except Exception as e:
            logger.error(f"复制文件到应用目录失败: {e}")
            return None
    
    def handle_url_file(self, url: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        处理文件URL
        
        Args:
            url: 文件URL
            
        Returns:
            (success, file_path, error_message)
        """
        try:
            if not url:
                return False, None, "URL为空"
            
            logger.info(f"处理文件URL: {url}")
            
            # 处理file://协议
            if url.startswith('file://'):
                local_path = url.replace('file://', '')
                # URL解码
                import urllib.parse
                local_path = urllib.parse.unquote(local_path)
                
                return self.handle_file_open(local_path)
            
            # 处理自定义协议
            if url.startswith('pythonista://') or url.startswith('ai-transcribe://'):
                file_path = self._extract_path_from_custom_url(url)
                if file_path:
                    return self.handle_file_open(file_path)
                else:
                    return False, None, "无法从自定义URL提取文件路径"
            
            # 处理网络URL（如果需要支持）
            if url.startswith(('http://', 'https://')):
                return False, None, "暂不支持网络文件URL"
            
            return False, None, f"不支持的URL格式: {url}"
        
        except Exception as e:
            logger.exception(f"处理文件URL异常: {url}")
            return False, None, f"处理文件URL错误: {str(e)}"
    
    def _extract_path_from_custom_url(self, url: str) -> Optional[str]:
        """从自定义URL提取文件路径"""
        try:
            import urllib.parse
            
            parsed_url = urllib.parse.urlparse(url)
            
            # 从查询参数中提取路径
            query_params = urllib.parse.parse_qs(parsed_url.query)
            
            if 'file' in query_params:
                file_path = query_params['file'][0]
                return urllib.parse.unquote(file_path)
            
            if 'path' in query_params:
                file_path = query_params['path'][0]
                return urllib.parse.unquote(file_path)
            
            # 从路径中提取
            if parsed_url.path:
                path = parsed_url.path.lstrip('/')
                if path:
                    return urllib.parse.unquote(path)
            
            return None
        
        except Exception as e:
            logger.error(f"从自定义URL提取路径失败: {e}")
            return None
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """获取文件详细信息"""
        try:
            if not os.path.exists(file_path):
                return {'exists': False}
            
            # 基本信息
            info = {
                'exists': True,
                'path': file_path,
                'name': os.path.basename(file_path),
                'size_mb': FileUtils.get_file_size_mb(file_path),
                'extension': FileUtils.get_file_extension(file_path),
                'is_readable': os.access(file_path, os.R_OK),
                'is_writable': os.access(file_path, os.W_OK),
            }
            
            # 验证信息
            is_supported, file_type = FileUtils.is_supported_format(file_path)
            info.update({
                'is_supported': is_supported,
                'file_type': file_type,
            })
            
            # 时间信息
            try:
                import time
                stat = os.stat(file_path)
                info.update({
                    'created_time': time.ctime(stat.st_ctime),
                    'modified_time': time.ctime(stat.st_mtime),
                    'accessed_time': time.ctime(stat.st_atime),
                })
            except Exception:
                pass
            
            # 媒体信息（如果是音视频文件）
            if is_supported and file_type in ['audio', 'video']:
                try:
                    from ..core.media_processor import MediaProcessor
                    processor = MediaProcessor()
                    media_info = processor.get_media_info(file_path)
                    if media_info:
                        info['media_info'] = media_info
                except Exception as e:
                    logger.debug(f"获取媒体信息失败: {e}")
            
            return info
        
        except Exception as e:
            logger.error(f"获取文件信息失败: {e}")
            return {'exists': False, 'error': str(e)}
    
    def create_file_association(self, file_types: List[str]) -> bool:
        """
        创建文件关联（在iOS环境中的实现）
        
        Args:
            file_types: 文件类型列表，如 ['.mp3', '.wav', '.mp4']
            
        Returns:
            bool: 是否成功
        """
        try:
            # 在iOS中，文件关联通常通过Info.plist配置
            # 这里提供一个概念性的实现
            
            logger.info(f"请求创建文件关联: {file_types}")
            
            # 在实际的iOS应用中，需要在Info.plist中配置：
            # CFBundleDocumentTypes数组，包含每种文件类型的配置
            
            # 这里只是记录请求，实际的文件关联需要在应用打包时配置
            supported_types = []
            for file_type in file_types:
                if file_type in ['.mp3', '.wav', '.aac', '.m4a', '.flac', '.mp4', '.mov', '.avi']:
                    supported_types.append(file_type)
            
            if supported_types:
                logger.info(f"支持的文件关联类型: {supported_types}")
                return True
            else:
                logger.warning("没有支持的文件类型用于关联")
                return False
        
        except Exception as e:
            logger.error(f"创建文件关联失败: {e}")
            return False
    
    def get_supported_file_types(self) -> Dict[str, List[str]]:
        """获取支持的文件类型"""
        try:
            from ..config import config
            
            return {
                'audio': config.get('supported_formats.audio', []),
                'video': config.get('supported_formats.video', []),
                'all': config.get('supported_formats.audio', []) + config.get('supported_formats.video', [])
            }
        
        except Exception as e:
            logger.error(f"获取支持的文件类型失败: {e}")
            return {'audio': [], 'video': [], 'all': []}
    
    def cleanup_temp_files(self):
        """清理临时文件"""
        try:
            if os.path.exists(self.temp_dir):
                for filename in os.listdir(self.temp_dir):
                    file_path = os.path.join(self.temp_dir, filename)
                    try:
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except Exception as e:
                        logger.warning(f"清理临时文件失败 {filename}: {e}")
                
                logger.info("文件处理器临时文件清理完成")
        
        except Exception as e:
            logger.error(f"清理文件处理器临时文件失败: {e}")
    
    def get_handler_stats(self) -> Dict[str, Any]:
        """获取文件处理器统计信息"""
        try:
            temp_files_count = 0
            temp_files_size = 0
            
            if os.path.exists(self.temp_dir):
                for filename in os.listdir(self.temp_dir):
                    file_path = os.path.join(self.temp_dir, filename)
                    if os.path.isfile(file_path):
                        temp_files_count += 1
                        temp_files_size += os.path.getsize(file_path)
            
            return {
                'temp_dir': self.temp_dir,
                'temp_files_count': temp_files_count,
                'temp_files_size_mb': temp_files_size / (1024 * 1024),
                'supported_schemes': self.supported_schemes,
                'supported_types': self.get_supported_file_types()
            }
        
        except Exception as e:
            logger.error(f"获取文件处理器统计信息失败: {e}")
            return {}
    
    def validate_file_permissions(self, file_path: str) -> Dict[str, bool]:
        """验证文件权限"""
        try:
            if not os.path.exists(file_path):
                return {'exists': False}
            
            return {
                'exists': True,
                'readable': os.access(file_path, os.R_OK),
                'writable': os.access(file_path, os.W_OK),
                'executable': os.access(file_path, os.X_OK),
            }
        
        except Exception as e:
            logger.error(f"验证文件权限失败: {e}")
            return {'exists': False, 'error': str(e)}