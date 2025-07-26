"""
结果预览界面模块

支持文本结果的预览和编辑
"""

import ui
import os
from typing import Optional, Dict, Any
from ..utils.logger import get_logger

logger = get_logger(__name__)

class ResultView:
    """结果预览界面类"""
    
    def __init__(self, app_controller):
        self.app_controller = app_controller
        self.view = None
        self.text_view = None
        self.toolbar = None
        self.result_data = {}
        
        self._create_ui()
    
    def _create_ui(self):
        """创建结果界面"""
        try:
            # 主视图
            self.view = ui.View(name='处理结果')
            self.view.background_color = '#f0f0f0'
            
            # 工具栏
            self._create_toolbar()
            
            # 文本显示区域
            self._create_text_area()
            
            # 底部操作栏
            self._create_action_bar()
            
            logger.info("结果界面创建完成")
        
        except Exception as e:
            logger.exception("创建结果界面异常")
            raise
    
    def _create_toolbar(self):
        """创建工具栏"""
        # 工具栏背景
        toolbar_bg = ui.View(name='toolbar_bg')
        toolbar_bg.background_color = '#ffffff'
        toolbar_bg.frame = (0, 0, self.view.width, 50)
        toolbar_bg.flex = 'W'
        self.view.add_subview(toolbar_bg)
        
        # 标题
        title_label = ui.Label(name='title_label')
        title_label.text = '处理结果'
        title_label.font = ('<system-bold>', 18)
        title_label.text_color = '#333333'
        title_label.frame = (20, 10, 200, 30)
        toolbar_bg.add_subview(title_label)
        
        # 关闭按钮
        close_button = ui.Button(name='close_button')
        close_button.title = '✕'
        close_button.font = ('<system>', 20)
        close_button.text_color = '#666666'
        close_button.frame = (self.view.width - 40, 10, 30, 30)
        close_button.flex = 'L'
        close_button.action = self._close_action
        toolbar_bg.add_subview(close_button)
        
        # 分隔线
        separator = ui.View(name='separator')
        separator.background_color = '#e0e0e0'
        separator.frame = (0, 49, self.view.width, 1)
        separator.flex = 'W'
        toolbar_bg.add_subview(separator)
    
    def _create_text_area(self):
        """创建文本显示区域"""
        # 文本视图
        self.text_view = ui.TextView(name='text_view')
        self.text_view.font = ('<system>', 16)
        self.text_view.editable = True
        self.text_view.text_color = '#333333'
        self.text_view.background_color = '#ffffff'
        self.text_view.frame = (10, 60, self.view.width - 20, self.view.height - 130)
        self.text_view.flex = 'WH'
        self.view.add_subview(self.text_view)
    
    def _create_action_bar(self):
        """创建操作栏"""
        # 操作栏背景
        action_bg = ui.View(name='action_bg')
        action_bg.background_color = '#ffffff'
        action_bg.frame = (0, self.view.height - 60, self.view.width, 60)
        action_bg.flex = 'WT'
        self.view.add_subview(action_bg)
        
        # 分隔线
        separator = ui.View(name='separator')
        separator.background_color = '#e0e0e0'
        separator.frame = (0, 0, self.view.width, 1)
        separator.flex = 'W'
        action_bg.add_subview(separator)
        
        # 按钮容器
        button_container = ui.View(name='button_container')
        button_container.frame = (0, 10, self.view.width, 40)
        button_container.flex = 'W'
        action_bg.add_subview(button_container)
        
        # 复制按钮
        copy_button = ui.Button(name='copy_button')
        copy_button.title = '📋 复制'
        copy_button.font = ('<system>', 14)
        copy_button.background_color = '#007AFF'
        copy_button.tint_color = 'white'
        copy_button.corner_radius = 6
        copy_button.frame = (10, 5, 80, 30)
        copy_button.action = self._copy_action
        button_container.add_subview(copy_button)
        
        # 分享按钮
        share_button = ui.Button(name='share_button')
        share_button.title = '📤 分享'
        share_button.font = ('<system>', 14)
        share_button.background_color = '#34C759'
        share_button.tint_color = 'white'
        share_button.corner_radius = 6
        share_button.frame = (100, 5, 80, 30)
        share_button.action = self._share_action
        button_container.add_subview(share_button)
        
        # 保存按钮
        save_button = ui.Button(name='save_button')
        save_button.title = '💾 保存'
        save_button.font = ('<system>', 14)
        save_button.background_color = '#FF9500'
        save_button.tint_color = 'white'
        save_button.corner_radius = 6
        save_button.frame = (190, 5, 80, 30)
        save_button.action = self._save_action
        button_container.add_subview(save_button)
        
        # 重新处理按钮
        reprocess_button = ui.Button(name='reprocess_button')
        reprocess_button.title = '🔄 重新处理'
        reprocess_button.font = ('<system>', 14)
        reprocess_button.background_color = '#8E8E93'
        reprocess_button.tint_color = 'white'
        reprocess_button.corner_radius = 6
        reprocess_button.frame = (280, 5, 100, 30)
        reprocess_button.flex = 'L'
        reprocess_button.action = self._reprocess_action
        button_container.add_subview(reprocess_button)
    
    def show_result(self, result_data: Dict[str, Any]):
        """显示处理结果"""
        try:
            self.result_data = result_data
            
            # 更新标题
            title = result_data.get('title', '处理结果')
            title_label = self.view['toolbar_bg']['title_label']
            title_label.text = title
            
            # 显示文本内容
            content = result_data.get('content', '')
            if isinstance(content, dict):
                # 如果内容是字典，格式化显示
                formatted_content = self._format_dict_content(content)
                self.text_view.text = formatted_content
            else:
                self.text_view.text = str(content)
            
            # 更新按钮状态
            self._update_button_states()
            
            logger.info(f"显示结果: {len(str(content))} 字符")
        
        except Exception as e:
            logger.exception("显示结果异常")
            self.text_view.text = f"显示结果时发生错误: {str(e)}"
    
    def _format_dict_content(self, content: Dict[str, Any]) -> str:
        """格式化字典内容为可读文本"""
        try:
            formatted_lines = []
            
            # 处理转录结果
            if 'transcription' in content:
                formatted_lines.append("=== 转录结果 ===")
                formatted_lines.append("")
                formatted_lines.append(content['transcription'])
                formatted_lines.append("")
            
            # 处理AI处理结果
            if 'ai_processed' in content:
                formatted_lines.append("=== AI处理结果 ===")
                formatted_lines.append("")
                formatted_lines.append(content['ai_processed'])
                formatted_lines.append("")
            
            # 处理元数据
            if 'metadata' in content:
                metadata = content['metadata']
                formatted_lines.append("=== 处理信息 ===")
                
                if 'file_name' in metadata:
                    formatted_lines.append(f"文件名: {metadata['file_name']}")
                
                if 'processing_time' in metadata:
                    formatted_lines.append(f"处理时间: {metadata['processing_time']:.1f}秒")
                
                if 'template_used' in metadata:
                    formatted_lines.append(f"使用模板: {metadata['template_used']}")
                
                if 'word_count' in metadata:
                    formatted_lines.append(f"字数统计: {metadata['word_count']}")
                
                formatted_lines.append("")
            
            # 如果没有特殊格式，直接转换为文本
            if not formatted_lines:
                import json
                formatted_lines.append(json.dumps(content, ensure_ascii=False, indent=2))
            
            return '\n'.join(formatted_lines)
        
        except Exception as e:
            logger.error(f"格式化内容异常: {e}")
            return str(content)
    
    def _update_button_states(self):
        """更新按钮状态"""
        try:
            has_content = bool(self.text_view.text.strip())
            
            # 根据内容是否存在启用/禁用按钮
            button_container = self.view['action_bg']['button_container']
            
            for button_name in ['copy_button', 'share_button', 'save_button']:
                if button_name in button_container.subviews:
                    button = button_container[button_name]
                    button.enabled = has_content
                    button.alpha = 1.0 if has_content else 0.5
        
        except Exception as e:
            logger.error(f"更新按钮状态异常: {e}")
    
    def _copy_action(self, sender):
        """复制文本操作"""
        try:
            import clipboard
            
            text_to_copy = self.text_view.text
            if text_to_copy.strip():
                clipboard.set(text_to_copy)
                self._show_toast('文本已复制到剪贴板')
                logger.info("文本已复制到剪贴板")
            else:
                self._show_toast('没有可复制的内容')
        
        except Exception as e:
            logger.exception("复制文本异常")
            self._show_toast(f'复制失败: {str(e)}')
    
    def _share_action(self, sender):
        """分享文本操作"""
        try:
            text_to_share = self.text_view.text
            if not text_to_share.strip():
                self._show_toast('没有可分享的内容')
                return
            
            # 在iOS中分享文本
            try:
                import appex
                
                # 创建临时文件
                temp_file = self._create_temp_file(text_to_share)
                if temp_file:
                    # 使用iOS分享功能
                    import console
                    console.open_in(temp_file)
                    self._show_toast('已打开分享菜单')
                else:
                    # 备用方案：复制到剪贴板
                    import clipboard
                    clipboard.set(text_to_share)
                    self._show_toast('文本已复制到剪贴板，可手动分享')
            
            except ImportError:
                # 不在iOS环境中
                import clipboard
                clipboard.set(text_to_share)
                self._show_toast('文本已复制到剪贴板')
        
        except Exception as e:
            logger.exception("分享文本异常")
            self._show_toast(f'分享失败: {str(e)}')
    
    def _save_action(self, sender):
        """保存文本操作"""
        try:
            text_to_save = self.text_view.text
            if not text_to_save.strip():
                self._show_toast('没有可保存的内容')
                return
            
            # 生成文件名
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 根据结果类型确定文件名前缀
            file_prefix = "AI转录结果"
            if 'metadata' in self.result_data:
                metadata = self.result_data['metadata']
                if 'template_used' in metadata:
                    template_name = metadata['template_used']
                    if template_name == 'meeting_notes':
                        file_prefix = "会议纪要"
                    elif template_name == 'study_notes':
                        file_prefix = "学习笔记"
                    elif template_name == 'content_summary':
                        file_prefix = "内容摘要"
            
            filename = f"{file_prefix}_{timestamp}.txt"
            
            # 保存到Documents目录
            documents_path = os.path.expanduser('~/Documents')
            file_path = os.path.join(documents_path, filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(text_to_save)
            
            self._show_toast(f'已保存到: {filename}')
            logger.info(f"文件已保存: {file_path}")
        
        except Exception as e:
            logger.exception("保存文本异常")
            self._show_toast(f'保存失败: {str(e)}')
    
    def _reprocess_action(self, sender):
        """重新处理操作"""
        try:
            # 获取原始数据
            original_text = ""
            if 'original_transcription' in self.result_data:
                original_text = self.result_data['original_transcription']
            elif 'transcription' in self.result_data.get('content', {}):
                original_text = self.result_data['content']['transcription']
            
            if not original_text:
                self._show_toast('没有找到原始转录文本')
                return
            
            # 调用重新处理
            self.app_controller.show_reprocess_options(original_text)
            
        except Exception as e:
            logger.exception("重新处理异常")
            self._show_toast(f'重新处理失败: {str(e)}')
    
    def _close_action(self, sender):
        """关闭界面操作"""
        try:
            self.hide()
        except Exception as e:
            logger.exception("关闭界面异常")
    
    def _create_temp_file(self, content: str) -> Optional[str]:
        """创建临时文件"""
        try:
            import tempfile
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"AI转录结果_{timestamp}.txt"
            
            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, filename)
            
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return temp_file
        
        except Exception as e:
            logger.error(f"创建临时文件失败: {e}")
            return None
    
    def _show_toast(self, message: str):
        """显示提示消息"""
        try:
            # 创建提示视图
            toast = ui.View()
            toast.background_color = '#333333'
            toast.corner_radius = 10
            toast.alpha = 0.9
            
            # 提示文本
            label = ui.Label()
            label.text = message
            label.font = ('<system>', 14)
            label.text_color = 'white'
            label.alignment = ui.ALIGN_CENTER
            label.number_of_lines = 0
            
            # 计算大小
            text_size = ui.measure_string(message, font=label.font, max_width=300)
            toast.frame = (0, 0, text_size.width + 20, text_size.height + 20)
            label.frame = (10, 10, text_size.width, text_size.height)
            
            toast.add_subview(label)
            
            # 添加到主视图并居中
            self.view.add_subview(toast)
            toast.center = (self.view.width / 2, self.view.height - 100)
            
            # 自动消失
            import threading
            def hide_toast():
                import time
                time.sleep(2)
                if toast.superview:
                    toast.remove_from_superview()
            
            threading.Thread(target=hide_toast, daemon=True).start()
        
        except Exception as e:
            logger.error(f"显示提示消息失败: {e}")
            # 备用方案：使用console.hud
            try:
                import console
                console.hud_alert(message, duration=2)
            except:
                print(f"提示: {message}")
    
    def get_current_text(self) -> str:
        """获取当前显示的文本"""
        try:
            return self.text_view.text
        except Exception as e:
            logger.error(f"获取当前文本失败: {e}")
            return ""
    
    def set_text(self, text: str):
        """设置显示文本"""
        try:
            self.text_view.text = text
            self._update_button_states()
        except Exception as e:
            logger.error(f"设置文本失败: {e}")
    
    def append_text(self, text: str):
        """追加文本"""
        try:
            current_text = self.text_view.text
            self.text_view.text = current_text + text
            self._update_button_states()
            
            # 滚动到底部
            self.text_view.selected_range = (len(self.text_view.text), 0)
        except Exception as e:
            logger.error(f"追加文本失败: {e}")
    
    def clear_text(self):
        """清空文本"""
        try:
            self.text_view.text = ""
            self._update_button_states()
        except Exception as e:
            logger.error(f"清空文本失败: {e}")
    
    def show(self):
        """显示结果界面"""
        try:
            self.view.present('sheet', hide_title_bar=True)
        except Exception as e:
            logger.exception("显示结果界面异常")
    
    def hide(self):
        """隐藏结果界面"""
        try:
            if hasattr(self.view, 'close'):
                self.view.close()
            elif self.view.superview:
                self.view.remove_from_superview()
        except Exception as e:
            logger.error(f"隐藏结果界面异常: {e}")
    
    def is_visible(self) -> bool:
        """检查界面是否可见"""
        try:
            return bool(self.view.superview) or bool(getattr(self.view, 'on_screen', False))
        except Exception as e:
            logger.error(f"检查界面可见性异常: {e}")
            return False