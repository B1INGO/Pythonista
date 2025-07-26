"""
分享扩展处理模块

通过iOS分享菜单接收文件
"""

import os
import shutil
from typing import Tuple, Optional, List, Dict, Any
from ..utils.logger import get_logger
from ..utils.file_utils import FileUtils

logger = get_logger(__name__)

class ShareExtensionHandler:
    """分享扩展处理器"""
    
    def __init__(self):
        self.temp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'temp_shares')
        FileUtils.ensure_directory(self.temp_dir)
    
    def handle_shared_files(self, shared_items: List[Any]) -> Tuple[bool, List[str], Optional[str]]:
        """
        处理通过分享扩展接收的文件
        
        Args:
            shared_items: 分享的项目列表
            
        Returns:
            (success, file_paths, error_message)
        """
        try:
            if not shared_items:
                return False, [], "没有接收到分享的文件"
            
            logger.info(f"收到 {len(shared_items)} 个分享项目")
            
            processed_files = []
            
            for i, item in enumerate(shared_items):
                try:
                    file_path = self._process_shared_item(item, i)
                    if file_path:
                        processed_files.append(file_path)
                        logger.info(f"处理分享文件成功: {os.path.basename(file_path)}")
                    else:
                        logger.warning(f"分享项目 {i} 处理失败")
                
                except Exception as e:
                    logger.error(f"处理分享项目 {i} 异常: {e}")
            
            if processed_files:
                return True, processed_files, None
            else:
                return False, [], "所有分享文件处理都失败了"
        
        except Exception as e:
            logger.exception("处理分享文件异常")
            return False, [], f"处理分享文件时发生错误: {str(e)}"
    
    def _process_shared_item(self, item: Any, index: int) -> Optional[str]:
        """处理单个分享项目"""
        try:
            # 尝试获取文件路径
            file_path = self._extract_file_path(item)
            if file_path and os.path.exists(file_path):
                # 验证文件格式
                is_valid, validation_msg = FileUtils.validate_file(file_path)
                if is_valid:
                    # 复制到临时目录
                    temp_file_path = self._copy_to_temp(file_path, index)
                    return temp_file_path
                else:
                    logger.warning(f"分享文件格式无效: {validation_msg}")
                    return None
            
            # 尝试从URL获取文件
            url = self._extract_url(item)
            if url:
                file_path = self._download_from_url(url, index)
                if file_path:
                    return file_path
            
            # 尝试处理文本内容（可能是文件内容）
            text_content = self._extract_text(item)
            if text_content:
                file_path = self._save_text_as_file(text_content, index)
                return file_path
            
            logger.warning(f"无法识别分享项目类型: {type(item)}")
            return None
        
        except Exception as e:
            logger.error(f"处理分享项目异常: {e}")
            return None
    
    def _extract_file_path(self, item: Any) -> Optional[str]:
        """从分享项目提取文件路径"""
        try:
            # 在Pythonista中，分享的文件通常通过appex模块传递
            try:
                import appex
                
                # 检查是否是文件
                if hasattr(item, 'file_path') or hasattr(item, 'path'):
                    return getattr(item, 'file_path', None) or getattr(item, 'path', None)
                
                # 检查appex的文件处理
                if appex.is_running_extension():
                    file_path = appex.get_file_path()
                    if file_path:
                        return file_path
                
                # 检查是否是字符串路径
                if isinstance(item, str) and os.path.exists(item):
                    return item
                
            except ImportError:
                logger.debug("appex模块不可用")
            
            # 检查常见的文件路径属性
            if hasattr(item, 'url') and hasattr(item.url, 'path'):
                return item.url.path
            
            if hasattr(item, 'fileURL') and item.fileURL:
                return str(item.fileURL.path) if hasattr(item.fileURL, 'path') else str(item.fileURL)
            
            return None
        
        except Exception as e:
            logger.debug(f"提取文件路径失败: {e}")
            return None
    
    def _extract_url(self, item: Any) -> Optional[str]:
        """从分享项目提取URL"""
        try:
            # 检查URL属性
            if hasattr(item, 'url') and item.url:
                url_str = str(item.url)
                if url_str.startswith(('http://', 'https://', 'file://')):
                    return url_str
            
            # 检查是否是字符串URL
            if isinstance(item, str) and item.startswith(('http://', 'https://', 'file://')):
                return item
            
            return None
        
        except Exception as e:
            logger.debug(f"提取URL失败: {e}")
            return None
    
    def _extract_text(self, item: Any) -> Optional[str]:
        """从分享项目提取文本内容"""
        try:
            # 检查文本属性
            if hasattr(item, 'text') and item.text:
                return item.text
            
            if hasattr(item, 'string') and item.string:
                return item.string
            
            # 检查是否是字符串
            if isinstance(item, str) and not item.startswith(('http://', 'https://', 'file://')):
                return item
            
            return None
        
        except Exception as e:
            logger.debug(f"提取文本失败: {e}")
            return None
    
    def _copy_to_temp(self, source_path: str, index: int) -> Optional[str]:
        """复制文件到临时目录"""
        try:
            filename = os.path.basename(source_path)
            safe_filename = FileUtils.get_safe_filename(f"shared_{index:03d}_{filename}")
            temp_path = os.path.join(self.temp_dir, safe_filename)
            
            if FileUtils.copy_file(source_path, temp_path):
                logger.debug(f"文件已复制到临时目录: {temp_path}")
                return temp_path
            else:
                return None
        
        except Exception as e:
            logger.error(f"复制文件到临时目录失败: {e}")
            return None
    
    def _download_from_url(self, url: str, index: int) -> Optional[str]:
        """从URL下载文件"""
        try:
            if url.startswith('file://'):
                # 本地文件URL
                local_path = url.replace('file://', '')
                if os.path.exists(local_path):
                    return self._copy_to_temp(local_path, index)
                return None
            
            if url.startswith(('http://', 'https://')):
                # 网络URL - 在实际应用中可以实现下载功能
                logger.info(f"收到网络URL: {url}")
                # 这里可以实现网络文件下载
                # 暂时不支持网络下载
                return None
            
            return None
        
        except Exception as e:
            logger.error(f"从URL下载文件失败: {e}")
            return None
    
    def _save_text_as_file(self, text: str, index: int) -> Optional[str]:
        """将文本保存为文件"""
        try:
            # 生成文件名
            filename = f"shared_text_{index:03d}.txt"
            temp_path = os.path.join(self.temp_dir, filename)
            
            # 保存文本
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(text)
            
            logger.debug(f"文本已保存为文件: {temp_path}")
            return temp_path
        
        except Exception as e:
            logger.error(f"保存文本为文件失败: {e}")
            return None
    
    def handle_appex_files(self) -> Tuple[bool, List[str], Optional[str]]:
        """
        处理通过Pythonista appex接收的文件
        """
        try:
            import appex
            
            if not appex.is_running_extension():
                return False, [], "不在分享扩展环境中"
            
            files = []
            
            # 处理文件
            file_path = appex.get_file_path()
            if file_path:
                is_valid, validation_msg = FileUtils.validate_file(file_path)
                if is_valid:
                    temp_path = self._copy_to_temp(file_path, 0)
                    if temp_path:
                        files.append(temp_path)
                        logger.info(f"处理appex文件成功: {os.path.basename(temp_path)}")
                else:
                    logger.warning(f"appex文件格式无效: {validation_msg}")
            
            # 处理URL
            url = appex.get_url()
            if url:
                file_path = self._download_from_url(str(url), len(files))
                if file_path:
                    files.append(file_path)
            
            # 处理文本
            text = appex.get_text()
            if text and not files:  # 只有在没有文件时才处理文本
                file_path = self._save_text_as_file(text, len(files))
                if file_path:
                    files.append(file_path)
            
            if files:
                return True, files, None
            else:
                return False, [], "没有找到有效的分享内容"
        
        except ImportError:
            return False, [], "appex模块不可用"
        except Exception as e:
            logger.exception("处理appex文件异常")
            return False, [], f"处理appex文件错误: {str(e)}"
    
    def get_share_info(self) -> Dict[str, Any]:
        """获取分享信息"""
        try:
            import appex
            
            if not appex.is_running_extension():
                return {'is_extension': False}
            
            info = {
                'is_extension': True,
                'has_file': bool(appex.get_file_path()),
                'has_url': bool(appex.get_url()),
                'has_text': bool(appex.get_text()),
                'has_image': bool(appex.get_image()),
            }
            
            # 获取附加信息
            if info['has_file']:
                file_path = appex.get_file_path()
                info['file_info'] = {
                    'path': file_path,
                    'name': os.path.basename(file_path) if file_path else None,
                    'size_mb': FileUtils.get_file_size_mb(file_path) if file_path else 0,
                    'extension': FileUtils.get_file_extension(file_path) if file_path else None
                }
            
            if info['has_url']:
                info['url'] = str(appex.get_url())
            
            if info['has_text']:
                text = appex.get_text()
                info['text_info'] = {
                    'length': len(text) if text else 0,
                    'preview': text[:100] + '...' if text and len(text) > 100 else text
                }
            
            return info
        
        except ImportError:
            return {'is_extension': False, 'error': 'appex模块不可用'}
        except Exception as e:
            logger.error(f"获取分享信息失败: {e}")
            return {'is_extension': False, 'error': str(e)}
    
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
                
                logger.info("分享扩展临时文件清理完成")
        
        except Exception as e:
            logger.error(f"清理分享扩展临时文件失败: {e}")
    
    def is_extension_available(self) -> bool:
        """检查分享扩展是否可用"""
        try:
            import appex
            return True
        except ImportError:
            return False