"""
文件工具模块

提供文件操作的通用功能
"""

import os
import shutil
import hashlib
from typing import List, Optional, Tuple
from ..config import config
from .logger import get_logger

logger = get_logger(__name__)

class FileUtils:
    """文件工具类"""
    
    @staticmethod
    def get_file_extension(file_path: str) -> str:
        """获取文件扩展名"""
        return os.path.splitext(file_path)[1].lower()
    
    @staticmethod
    def get_file_size_mb(file_path: str) -> float:
        """获取文件大小（MB）"""
        try:
            return os.path.getsize(file_path) / (1024 * 1024)
        except Exception as e:
            logger.error(f"获取文件大小失败 {file_path}: {e}")
            return 0.0
    
    @staticmethod
    def is_supported_format(file_path: str) -> Tuple[bool, str]:
        """检查文件格式是否支持"""
        ext = FileUtils.get_file_extension(file_path)
        
        audio_formats = config.get('supported_formats.audio', [])
        video_formats = config.get('supported_formats.video', [])
        
        if ext in audio_formats:
            return True, 'audio'
        elif ext in video_formats:
            return True, 'video'
        else:
            return False, 'unknown'
    
    @staticmethod
    def validate_file(file_path: str) -> Tuple[bool, str]:
        """验证文件是否有效"""
        if not file_path:
            return False, "文件路径为空"
        
        if not os.path.exists(file_path):
            return False, "文件不存在"
        
        if not os.path.isfile(file_path):
            return False, "路径不是文件"
        
        # 检查文件格式
        is_supported, file_type = FileUtils.is_supported_format(file_path)
        if not is_supported:
            ext = FileUtils.get_file_extension(file_path)
            return False, f"不支持的文件格式: {ext}"
        
        # 检查文件大小
        file_size_mb = FileUtils.get_file_size_mb(file_path)
        max_size_mb = config.get('transcribe.max_file_size_mb', 100)
        if file_size_mb > max_size_mb:
            return False, f"文件太大: {file_size_mb:.1f}MB (最大: {max_size_mb}MB)"
        
        return True, f"有效的{file_type}文件"
    
    @staticmethod
    def get_file_hash(file_path: str) -> Optional[str]:
        """获取文件MD5哈希值"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"计算文件哈希失败 {file_path}: {e}")
            return None
    
    @staticmethod
    def ensure_directory(directory: str) -> bool:
        """确保目录存在"""
        try:
            os.makedirs(directory, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"创建目录失败 {directory}: {e}")
            return False
    
    @staticmethod
    def copy_file(src: str, dst: str, create_dirs: bool = True) -> bool:
        """复制文件"""
        try:
            if create_dirs:
                dst_dir = os.path.dirname(dst)
                if not FileUtils.ensure_directory(dst_dir):
                    return False
            
            shutil.copy2(src, dst)
            logger.debug(f"文件已复制: {src} -> {dst}")
            return True
        except Exception as e:
            logger.error(f"复制文件失败 {src} -> {dst}: {e}")
            return False
    
    @staticmethod
    def move_file(src: str, dst: str, create_dirs: bool = True) -> bool:
        """移动文件"""
        try:
            if create_dirs:
                dst_dir = os.path.dirname(dst)
                if not FileUtils.ensure_directory(dst_dir):
                    return False
            
            shutil.move(src, dst)
            logger.debug(f"文件已移动: {src} -> {dst}")
            return True
        except Exception as e:
            logger.error(f"移动文件失败 {src} -> {dst}: {e}")
            return False
    
    @staticmethod
    def delete_file(file_path: str) -> bool:
        """删除文件"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"文件已删除: {file_path}")
            return True
        except Exception as e:
            logger.error(f"删除文件失败 {file_path}: {e}")
            return False
    
    @staticmethod
    def get_temp_file_path(prefix: str = 'ai_transcribe', suffix: str = '') -> str:
        """获取临时文件路径"""
        import tempfile
        import uuid
        
        temp_dir = tempfile.gettempdir()
        filename = f"{prefix}_{uuid.uuid4().hex[:8]}{suffix}"
        return os.path.join(temp_dir, filename)
    
    @staticmethod
    def cleanup_temp_files(pattern: str = 'ai_transcribe*') -> int:
        """清理临时文件"""
        import tempfile
        import glob
        
        temp_dir = tempfile.gettempdir()
        pattern_path = os.path.join(temp_dir, pattern)
        temp_files = glob.glob(pattern_path)
        
        cleaned_count = 0
        for temp_file in temp_files:
            try:
                if os.path.isfile(temp_file):
                    os.remove(temp_file)
                    cleaned_count += 1
                elif os.path.isdir(temp_file):
                    shutil.rmtree(temp_file)
                    cleaned_count += 1
            except Exception as e:
                logger.warning(f"清理临时文件失败 {temp_file}: {e}")
        
        if cleaned_count > 0:
            logger.info(f"已清理 {cleaned_count} 个临时文件")
        
        return cleaned_count
    
    @staticmethod
    def get_safe_filename(filename: str) -> str:
        """获取安全的文件名（移除特殊字符）"""
        import re
        
        # 移除或替换不安全的字符
        safe_filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # 限制长度
        if len(safe_filename) > 200:
            name, ext = os.path.splitext(safe_filename)
            safe_filename = name[:200-len(ext)] + ext
        
        return safe_filename