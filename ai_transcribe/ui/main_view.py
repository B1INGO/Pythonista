"""
主界面模块

基于Pythonista UI的友好界面
"""

import ui
import os
from typing import Optional, List, Dict, Any
from ..utils.logger import get_logger
from ..config import config

logger = get_logger(__name__)

class MainView:
    """主界面类"""
    
    def __init__(self, app_controller):
        self.app_controller = app_controller
        self.view = None
        self.file_list = []
        self.selected_files = []
        
        # UI组件引用
        self.file_table = None
        self.status_label = None
        self.transcribe_button = None
        self.process_button = None
        self.settings_button = None
        self.template_selector = None
        
        self._create_ui()
    
    def _get_screen_size(self):
        """获取屏幕尺寸"""
        try:
            # 尝试获取实际屏幕尺寸
            import console
            if hasattr(console, 'get_window_size'):
                console_size = console.get_window_size()
                # console返回的是字符尺寸，需要估算像素尺寸
                width = max(375, console_size[0] * 10)  # 假设每字符10px宽
                height = max(667, console_size[1] * 20)  # 假设每字符20px高
            else:
                # 默认iPhone尺寸
                width, height = 375, 667
            
            # 如果可用，尝试从ui模块获取更准确的尺寸
            try:
                temp_view = ui.View()
                temp_view.present('fullscreen', hide_title_bar=True)
                if temp_view.width > 0 and temp_view.height > 0:
                    width, height = temp_view.width, temp_view.height
                temp_view.close()
            except:
                pass
                
            logger.debug(f"屏幕尺寸: {width}x{height}")
            return width, height
            
        except Exception as e:
            logger.warning(f"获取屏幕尺寸失败，使用默认值: {e}")
            # iPhone 6/7/8 尺寸作为默认值
            return 375, 667
    
    def _create_ui(self):
        """创建用户界面"""
        try:
            # 获取动态尺寸
            self.screen_width, self.screen_height = self._get_screen_size()
            
            # 主视图
            self.view = ui.View(name='AI音视频转文字工具')
            self.view.background_color = '#f0f0f0'
            # 让主视图使用全屏
            self.view.frame = (0, 0, self.screen_width, self.screen_height)
            
            # 标题栏
            self._create_title_bar()
            
            # 文件区域
            self._create_file_area()
            
            # 控制区域
            self._create_control_area()
            
            # 状态栏
            self._create_status_bar()
            
            logger.info("主界面创建完成")
        
        except Exception as e:
            logger.exception("创建主界面异常")
            raise
    
    def _create_title_bar(self):
        """创建标题栏"""
        margin = 20
        title_height = max(40, int(self.screen_height * 0.06))
        
        # 标题标签
        title_label = ui.Label(name='title_label')
        title_label.text = 'AI音视频转文字工具'
        title_label.font = ('<system-bold>', max(16, int(self.screen_width / 20)))
        title_label.text_color = '#333333'
        title_label.alignment = ui.ALIGN_CENTER
        title_label.frame = (0, margin, self.screen_width, title_height)
        title_label.flex = 'W'
        self.view.add_subview(title_label)
        
        # 设置按钮
        button_size = max(30, int(self.screen_width / 12))
        self.settings_button = ui.Button(name='settings_button')
        self.settings_button.title = '⚙️'
        self.settings_button.font = ('<system>', max(18, int(button_size * 0.7)))
        self.settings_button.frame = (self.screen_width - button_size - margin, 
                                    margin + (title_height - button_size) // 2, 
                                    button_size, button_size)
        self.settings_button.flex = 'L'
        self.settings_button.action = self._settings_action
        self.view.add_subview(self.settings_button)
    
    def _create_file_area(self):
        """创建文件区域"""
        margin = 20
        title_bar_height = max(40, int(self.screen_height * 0.06)) + 20  # title + margin
        current_y = title_bar_height + 20
        
        # 文件区域标题
        file_title = ui.Label(name='file_title')
        file_title.text = '选择音视频文件'
        file_title.font = ('<system-bold>', max(14, int(self.screen_width / 24)))
        file_title.text_color = '#666666'
        file_title.frame = (margin, current_y, self.screen_width - 2*margin, 30)
        file_title.flex = 'W'
        self.view.add_subview(file_title)
        
        current_y += 40
        button_height = max(35, int(self.screen_height * 0.05))
        button_width = int((self.screen_width - 4*margin) / 3)  # 3 buttons with margins
        
        # 添加文件按钮
        add_file_button = ui.Button(name='add_file_button')
        add_file_button.title = '+ 添加文件'
        add_file_button.font = ('<system>', max(14, int(self.screen_width / 26)))
        add_file_button.background_color = '#007AFF'
        add_file_button.tint_color = 'white'
        add_file_button.corner_radius = 8
        add_file_button.frame = (margin, current_y, button_width, button_height)
        add_file_button.action = self._add_file_action
        self.view.add_subview(add_file_button)
        
        # 清空列表按钮
        clear_button = ui.Button(name='clear_button')
        clear_button.title = '清空'
        clear_button.font = ('<system>', max(14, int(self.screen_width / 26)))
        clear_button.background_color = '#FF3B30'
        clear_button.tint_color = 'white'
        clear_button.corner_radius = 8
        clear_button.frame = (margin + button_width + margin, current_y, button_width*0.6, button_height)
        clear_button.action = self._clear_files_action
        self.view.add_subview(clear_button)
        
        # 从分享扩展添加按钮
        share_button = ui.Button(name='share_button')
        share_button.title = '📤 分享'
        share_button.font = ('<system>', max(14, int(self.screen_width / 26)))
        share_button.background_color = '#34C759'
        share_button.tint_color = 'white'
        share_button.corner_radius = 8
        share_button.frame = (self.screen_width - margin - button_width, current_y, button_width, button_height)
        share_button.action = self._handle_share_action
        self.view.add_subview(share_button)
        
        current_y += button_height + 20
        
        # 文件列表 - 使用更多空间
        table_height = int(self.screen_height * 0.3)  # 30% of screen height
        self.file_table = ui.TableView(name='file_table')
        self.file_table.frame = (margin, current_y, self.screen_width - 2*margin, table_height)
        self.file_table.flex = 'WH'
        self.file_table.data_source = FileTableDataSource(self)
        self.file_table.delegate = FileTableDelegate(self)
        self.view.add_subview(self.file_table)
        
        # 保存当前Y位置供后续组件使用
        self._file_area_bottom = current_y + table_height
    
    def _create_control_area(self):
        """创建控制区域"""
        margin = 20
        current_y = self._file_area_bottom + 20
        
        # 模板选择区域
        template_title = ui.Label(name='template_title')
        template_title.text = '处理模板'
        template_title.font = ('<system-bold>', max(14, int(self.screen_width / 24)))
        template_title.text_color = '#666666'
        template_title.frame = (margin, current_y, 150, 30)
        template_title.flex = 'WT'
        self.view.add_subview(template_title)
        
        current_y += 40
        
        # 模板选择器
        self.template_selector = ui.SegmentedControl(name='template_selector')
        self.template_selector.segments = ['会议纪要', '学习笔记', '内容摘要', '自定义']
        self.template_selector.selected_index = 0
        self.template_selector.frame = (margin, current_y, self.screen_width - 2*margin, 30)
        self.template_selector.flex = 'WT'
        self.template_selector.action = self._template_changed
        self.view.add_subview(self.template_selector)
        
        current_y += 50
        
        # 操作按钮区域
        button_height = max(45, int(self.screen_height * 0.06))
        button_width = int((self.screen_width - 3*margin) / 2)  # 2 buttons side by side
        
        # 转录按钮
        self.transcribe_button = ui.Button(name='transcribe_button')
        self.transcribe_button.title = '🎤 开始转录'
        self.transcribe_button.font = ('<system-bold>', max(14, int(self.screen_width / 26)))
        self.transcribe_button.background_color = '#007AFF'
        self.transcribe_button.tint_color = 'white'
        self.transcribe_button.corner_radius = 8
        self.transcribe_button.frame = (margin, current_y, button_width, button_height)
        self.transcribe_button.flex = 'WT'
        self.transcribe_button.action = self._transcribe_action
        self.view.add_subview(self.transcribe_button)
        
        # AI处理按钮
        self.process_button = ui.Button(name='process_button')
        self.process_button.title = '🤖 AI整理'
        self.process_button.font = ('<system-bold>', max(14, int(self.screen_width / 26)))
        self.process_button.background_color = '#34C759'
        self.process_button.tint_color = 'white'
        self.process_button.corner_radius = 8
        self.process_button.frame = (margin + button_width + margin, current_y, button_width, button_height)
        self.process_button.flex = 'WT'
        self.process_button.action = self._process_action
        self.view.add_subview(self.process_button)
        
        current_y += button_height + 15
        
        # 一键处理按钮
        one_click_button = ui.Button(name='one_click_button')
        one_click_button.title = '⚡ 一键处理'
        one_click_button.font = ('<system-bold>', max(14, int(self.screen_width / 26)))
        one_click_button.background_color = '#FF9500'
        one_click_button.tint_color = 'white'
        one_click_button.corner_radius = 8
        one_click_button.frame = (margin, current_y, self.screen_width - 2*margin, button_height)
        one_click_button.flex = 'WT'
        one_click_button.action = self._one_click_action
        self.view.add_subview(one_click_button)
        
        # 保存当前Y位置供状态栏使用
        self._control_area_bottom = current_y + button_height
    
    def _create_status_bar(self):
        """创建状态栏"""
        margin = 20
        current_y = self._control_area_bottom + 20
        
        self.status_label = ui.Label(name='status_label')
        self.status_label.text = '准备就绪'
        self.status_label.font = ('<system>', max(12, int(self.screen_width / 30)))
        self.status_label.text_color = '#666666'
        self.status_label.alignment = ui.ALIGN_CENTER
        self.status_label.frame = (margin, current_y, self.screen_width - 2*margin, 20)
        self.status_label.flex = 'WT'
        self.view.add_subview(self.status_label)
    
    def _add_file_action(self, sender):
        """添加文件操作"""
        try:
            # 在iOS中，通常通过文档选择器选择文件
            # 这里模拟文件选择过程
            console_msg = '''
请通过以下方式添加文件：
1. 使用"分享"按钮从其他应用分享文件
2. 通过URL Scheme调用: ai-transcribe://open?file=...
3. 将文件保存到Pythonista的Documents目录

支持的格式：
音频: .mp3, .wav, .aac, .m4a, .flac
视频: .mp4, .mov, .avi, .mkv, .wmv
            '''
            
            # 显示帮助信息
            self._show_alert('添加文件', console_msg)
            
            # 尝试检查Documents目录中的文件
            self._scan_documents_folder()
            
        except Exception as e:
            logger.exception("添加文件操作异常")
            self._show_alert('错误', f'添加文件失败: {str(e)}')
    
    def _scan_documents_folder(self):
        """扫描Documents文件夹中的音视频文件"""
        try:
            documents_path = os.path.expanduser('~/Documents')
            if not os.path.exists(documents_path):
                return
            
            supported_extensions = set()
            supported_extensions.update(config.get('supported_formats.audio', []))
            supported_extensions.update(config.get('supported_formats.video', []))
            
            found_files = []
            for filename in os.listdir(documents_path):
                file_path = os.path.join(documents_path, filename)
                if os.path.isfile(file_path):
                    _, ext = os.path.splitext(filename)
                    if ext.lower() in supported_extensions:
                        found_files.append(file_path)
            
            if found_files:
                # 自动添加找到的文件
                for file_path in found_files[:5]:  # 限制数量
                    if file_path not in [f['path'] for f in self.file_list]:
                        self.add_file(file_path)
                
                self.update_status(f'自动发现并添加了 {len(found_files)} 个文件')
        
        except Exception as e:
            logger.warning(f"扫描Documents文件夹失败: {e}")
    
    def _clear_files_action(self, sender):
        """清空文件列表操作"""
        self.file_list.clear()
        self.selected_files.clear()
        self.file_table.reload()
        self.update_status('文件列表已清空')
    
    def _handle_share_action(self, sender):
        """处理分享扩展操作"""
        try:
            from ..ios_integration.share_extension import ShareExtensionHandler
            
            share_handler = ShareExtensionHandler()
            
            # 检查是否在分享扩展环境中
            if share_handler.is_extension_available():
                success, files, error = share_handler.handle_appex_files()
                
                if success and files:
                    for file_path in files:
                        self.add_file(file_path)
                    self.update_status(f'从分享扩展添加了 {len(files)} 个文件')
                else:
                    self._show_alert('分享扩展', error or '没有找到分享的文件')
            else:
                self._show_alert('分享扩展', '分享扩展功能不可用\n请从其他应用使用"分享"功能调用本工具')
        
        except Exception as e:
            logger.exception("处理分享扩展异常")
            self._show_alert('错误', f'处理分享扩展失败: {str(e)}')
    
    def _template_changed(self, sender):
        """模板选择改变"""
        selected_index = sender.selected_index
        templates = ['meeting_notes', 'study_notes', 'content_summary', 'custom_cleanup']
        
        if selected_index < len(templates):
            template_id = templates[selected_index]
            self.update_status(f'已选择模板: {sender.segments[selected_index]}')
            logger.info(f"选择模板: {template_id}")
        else:
            self.update_status('已选择自定义模板')
    
    def _transcribe_action(self, sender):
        """转录操作"""
        try:
            if not self.file_list:
                self._show_alert('提示', '请先添加音视频文件')
                return
            
            # 获取选中的文件，如果没有选中则使用第一个
            files_to_process = self.selected_files if self.selected_files else [self.file_list[0]]
            
            # 启动转录流程
            self.app_controller.start_transcription(files_to_process)
            
        except Exception as e:
            logger.exception("转录操作异常")
            self._show_alert('错误', f'启动转录失败: {str(e)}')
    
    def _process_action(self, sender):
        """AI处理操作"""
        try:
            # 获取当前选择的模板
            template_index = self.template_selector.selected_index
            templates = ['meeting_notes', 'study_notes', 'content_summary', 'custom_cleanup']
            
            template_id = templates[template_index] if template_index < len(templates) else 'custom_cleanup'
            
            # 启动AI处理流程
            self.app_controller.start_ai_processing(template_id)
            
        except Exception as e:
            logger.exception("AI处理操作异常")
            self._show_alert('错误', f'启动AI处理失败: {str(e)}')
    
    def _one_click_action(self, sender):
        """一键处理操作"""
        try:
            if not self.file_list:
                self._show_alert('提示', '请先添加音视频文件')
                return
            
            # 获取选中的文件，如果没有选中则使用第一个
            files_to_process = self.selected_files if self.selected_files else [self.file_list[0]]
            
            # 获取当前选择的模板
            template_index = self.template_selector.selected_index
            templates = ['meeting_notes', 'study_notes', 'content_summary', 'custom_cleanup']
            template_id = templates[template_index] if template_index < len(templates) else 'custom_cleanup'
            
            # 启动完整处理流程
            self.app_controller.start_complete_processing(files_to_process, template_id)
            
        except Exception as e:
            logger.exception("一键处理操作异常")
            self._show_alert('错误', f'启动一键处理失败: {str(e)}')
    
    def _settings_action(self, sender):
        """设置操作"""
        try:
            self.app_controller.show_settings()
        except Exception as e:
            logger.exception("打开设置异常")
            self._show_alert('错误', f'打开设置失败: {str(e)}')
    
    def add_file(self, file_path: str) -> bool:
        """添加文件到列表"""
        try:
            from ..utils.file_utils import FileUtils
            
            # 验证文件
            is_valid, message = FileUtils.validate_file(file_path)
            if not is_valid:
                self._show_alert('文件无效', message)
                return False
            
            # 检查是否已存在
            if any(f['path'] == file_path for f in self.file_list):
                self.update_status('文件已存在于列表中')
                return False
            
            # 获取文件信息
            file_info = {
                'path': file_path,
                'name': os.path.basename(file_path),
                'size_mb': FileUtils.get_file_size_mb(file_path),
                'type': FileUtils.is_supported_format(file_path)[1]
            }
            
            self.file_list.append(file_info)
            self.file_table.reload()
            
            self.update_status(f'已添加文件: {file_info["name"]}')
            logger.info(f"添加文件成功: {file_path}")
            return True
        
        except Exception as e:
            logger.exception(f"添加文件异常: {file_path}")
            self._show_alert('错误', f'添加文件失败: {str(e)}')
            return False
    
    def remove_file(self, index: int):
        """移除文件"""
        try:
            if 0 <= index < len(self.file_list):
                removed_file = self.file_list.pop(index)
                self.file_table.reload()
                self.update_status(f'已移除文件: {removed_file["name"]}')
        except Exception as e:
            logger.exception(f"移除文件异常: {index}")
    
    def update_status(self, message: str):
        """更新状态显示"""
        try:
            self.status_label.text = message
            logger.info(f"状态更新: {message}")
        except Exception as e:
            logger.error(f"更新状态失败: {e}")
    
    def _show_alert(self, title: str, message: str):
        """显示警告对话框"""
        try:
            import console
            console.alert(title, message, 'OK', hide_cancel_button=True)
        except Exception as e:
            logger.error(f"显示警告对话框失败: {e}")
            print(f"{title}: {message}")
    
    def show(self):
        """显示主界面"""
        try:
            self.view.present('sheet', hide_title_bar=False)
        except Exception as e:
            logger.exception("显示主界面异常")
            raise

class FileTableDataSource:
    """文件列表数据源"""
    
    def __init__(self, main_view):
        self.main_view = main_view
    
    def tableview_number_of_sections(self, tableview):
        return 1
    
    def tableview_number_of_rows(self, tableview, section):
        return len(self.main_view.file_list)
    
    def tableview_cell_for_row(self, tableview, section, row):
        try:
            file_info = self.main_view.file_list[row]
            
            cell = ui.TableViewCell('subtitle')
            cell.text_label.text = file_info['name']
            cell.detail_text_label.text = f"{file_info['size_mb']:.1f}MB • {file_info['type']}"
            
            # 添加文件类型图标
            if file_info['type'] == 'audio':
                cell.image_view.image = ui.Image.named('iob:ios7_musical_notes_32')
            elif file_info['type'] == 'video':
                cell.image_view.image = ui.Image.named('iob:ios7_videocam_32')
            
            return cell
        except Exception as e:
            logger.error(f"创建表格单元格异常: {e}")
            cell = ui.TableViewCell()
            cell.text_label.text = "错误"
            return cell

class FileTableDelegate:
    """文件列表代理"""
    
    def __init__(self, main_view):
        self.main_view = main_view
    
    def tableview_did_select(self, tableview, section, row):
        try:
            file_info = self.main_view.file_list[row]
            
            # 切换选中状态
            if file_info in self.main_view.selected_files:
                self.main_view.selected_files.remove(file_info)
            else:
                self.main_view.selected_files.append(file_info)
            
            # 更新显示
            cell = tableview.cell_for_row(ui.Path((section, row)))
            if cell:
                if file_info in self.main_view.selected_files:
                    cell.accessory_type = 'checkmark'
                else:
                    cell.accessory_type = 'none'
        
        except Exception as e:
            logger.error(f"选择表格行异常: {e}")
    
    def tableview_can_delete(self, tableview, section, row):
        return True
    
    def tableview_delete(self, tableview, section, row):
        try:
            self.main_view.remove_file(row)
        except Exception as e:
            logger.error(f"删除表格行异常: {e}")