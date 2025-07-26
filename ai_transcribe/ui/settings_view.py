"""
设置界面模块

配置和管理应用设置
"""

import ui
from typing import Optional, Dict, Any, List
from ..utils.logger import get_logger
from ..config import config

logger = get_logger(__name__)

class SettingsView:
    """设置界面类"""
    
    def __init__(self, app_controller):
        self.app_controller = app_controller
        self.view = None
        self.section_table = None
        
        self._create_ui()
    
    def _get_screen_size(self):
        """获取屏幕尺寸"""
        try:
            # 尝试获取实际屏幕尺寸
            import console
            if hasattr(console, 'get_window_size'):
                console_size = console.get_window_size()
                width = max(375, console_size[0] * 10)
                height = max(667, console_size[1] * 20)
            else:
                width, height = 375, 667
                
            logger.debug(f"屏幕尺寸: {width}x{height}")
            return width, height
            
        except Exception as e:
            logger.warning(f"获取屏幕尺寸失败，使用默认值: {e}")
            return 375, 667
    
    def _create_ui(self):
        """创建设置界面"""
        try:
            # 获取动态尺寸
            self.screen_width, self.screen_height = self._get_screen_size()
            
            # 主视图
            self.view = ui.View(name='设置')
            self.view.background_color = '#f0f0f0'
            self.view.frame = (0, 0, self.screen_width, self.screen_height)
            
            # 标题栏
            self._create_title_bar()
            
            # 设置内容
            self._create_settings_content()
            
            logger.info("设置界面创建完成")
        
        except Exception as e:
            logger.exception("创建设置界面异常")
            raise
    
    def _create_title_bar(self):
        """创建标题栏"""
        title_height = max(60, int(self.screen_height * 0.08))
        
        # 标题栏背景
        title_bg = ui.View(name='title_bg')
        title_bg.background_color = '#ffffff'
        title_bg.frame = (0, 0, self.screen_width, title_height)
        title_bg.flex = 'W'
        self.view.add_subview(title_bg)
        
        # 标题
        title_label = ui.Label(name='title_label')
        title_label.text = '设置'
        title_label.font = ('<system-bold>', max(16, int(self.screen_width / 20)))
        title_label.text_color = '#333333'
        title_label.frame = (20, (title_height - 30) // 2, 200, 30)
        title_bg.add_subview(title_label)
        
        # 完成按钮
        button_width = max(50, int(self.screen_width / 7))
        done_button = ui.Button(name='done_button')
        done_button.title = '完成'
        done_button.font = ('<system>', max(14, int(self.screen_width / 26)))
        done_button.text_color = '#007AFF'
        done_button.frame = (self.screen_width - button_width - 10, 
                           (title_height - 30) // 2, 
                           button_width, 30)
        done_button.flex = 'L'
        done_button.action = self._done_action
        title_bg.add_subview(done_button)
        
        # 分隔线
        separator = ui.View(name='separator')
        separator.background_color = '#e0e0e0'
        separator.frame = (0, title_height - 1, self.screen_width, 1)
        separator.flex = 'W'
        self.view.add_subview(separator)
        
        # 保存标题栏高度
        self._title_height = title_height
    
    def _create_settings_content(self):
        """创建设置内容"""
        # 使用表格视图显示设置选项
        self.section_table = ui.TableView(name='section_table')
        self.section_table.frame = (0, self._title_height, 
                                  self.screen_width, 
                                  self.screen_height - self._title_height)
        self.section_table.flex = 'WH'
        self.section_table.data_source = SettingsDataSource(self)
        self.section_table.delegate = SettingsDelegate(self)
        self.view.add_subview(self.section_table)
    
    def _done_action(self, sender):
        """完成操作"""
        try:
            self.hide()
        except Exception as e:
            logger.exception("完成设置异常")
    
    def show_api_settings(self):
        """显示API设置"""
        try:
            api_view = APISettingsView(self.app_controller)
            api_view.show()
        except Exception as e:
            logger.exception("显示API设置异常")
    
    def show_template_settings(self):
        """显示模板设置"""
        try:
            template_view = TemplateSettingsView(self.app_controller)
            template_view.show()
        except Exception as e:
            logger.exception("显示模板设置异常")
    
    def show_general_settings(self):
        """显示通用设置"""
        try:
            general_view = GeneralSettingsView(self.app_controller)
            general_view.show()
        except Exception as e:
            logger.exception("显示通用设置异常")
    
    def show_about(self):
        """显示关于信息"""
        try:
            about_view = AboutView()
            about_view.show()
        except Exception as e:
            logger.exception("显示关于信息异常")
    
    def show(self):
        """显示设置界面"""
        try:
            self.view.present('sheet', hide_title_bar=True)
        except Exception as e:
            logger.exception("显示设置界面异常")
    
    def hide(self):
        """隐藏设置界面"""
        try:
            if hasattr(self.view, 'close'):
                self.view.close()
            elif self.view.superview:
                self.view.remove_from_superview()
        except Exception as e:
            logger.error(f"隐藏设置界面异常: {e}")

class SettingsDataSource:
    """设置数据源"""
    
    def __init__(self, settings_view):
        self.settings_view = settings_view
        self.sections = [
            {
                'title': 'API配置',
                'items': [
                    {'title': '硅基流动API', 'subtitle': '语音转文字服务', 'action': 'api_siliconflow'},
                    {'title': 'DeepSeek API', 'subtitle': 'AI文本处理服务', 'action': 'api_deepseek'},
                    {'title': 'API测试', 'subtitle': '测试API连接', 'action': 'api_test'}
                ]
            },
            {
                'title': '处理设置',
                'items': [
                    {'title': '提示词模板', 'subtitle': '管理AI处理模板', 'action': 'templates'},
                    {'title': '文件格式', 'subtitle': '支持的音视频格式', 'action': 'formats'},
                    {'title': '缓存设置', 'subtitle': '管理处理缓存', 'action': 'cache'}
                ]
            },
            {
                'title': '应用设置',
                'items': [
                    {'title': '通用设置', 'subtitle': '界面和行为设置', 'action': 'general'},
                    {'title': '日志设置', 'subtitle': '日志记录和调试', 'action': 'logs'},
                    {'title': '数据管理', 'subtitle': '清除数据和重置', 'action': 'data'}
                ]
            },
            {
                'title': '关于',
                'items': [
                    {'title': '应用信息', 'subtitle': '版本和开发信息', 'action': 'about'},
                    {'title': '使用帮助', 'subtitle': '使用说明和常见问题', 'action': 'help'},
                    {'title': '反馈建议', 'subtitle': '报告问题和建议', 'action': 'feedback'}
                ]
            }
        ]
    
    def tableview_number_of_sections(self, tableview):
        return len(self.sections)
    
    def tableview_number_of_rows(self, tableview, section):
        return len(self.sections[section]['items'])
    
    def tableview_title_for_header(self, tableview, section):
        return self.sections[section]['title']
    
    def tableview_cell_for_row(self, tableview, section, row):
        try:
            item = self.sections[section]['items'][row]
            
            cell = ui.TableViewCell('subtitle')
            cell.text_label.text = item['title']
            cell.detail_text_label.text = item['subtitle']
            cell.accessory_type = 'disclosure_indicator'
            
            # 添加状态指示
            if item['action'].startswith('api_'):
                status = self._get_api_status(item['action'])
                if status == 'configured':
                    cell.image_view.image = ui.Image.named('iob:checkmark_circled_32')
                elif status == 'error':
                    cell.image_view.image = ui.Image.named('iob:close_circled_32')
                else:
                    cell.image_view.image = ui.Image.named('iob:help_circled_32')
            
            return cell
        except Exception as e:
            logger.error(f"创建设置单元格异常: {e}")
            cell = ui.TableViewCell()
            cell.text_label.text = "错误"
            return cell
    
    def _get_api_status(self, action: str) -> str:
        """获取API配置状态"""
        try:
            if action == 'api_siliconflow':
                api_key = config.get_api_key('siliconflow')
                return 'configured' if api_key else 'not_configured'
            elif action == 'api_deepseek':
                api_key = config.get_api_key('deepseek')
                return 'configured' if api_key else 'not_configured'
            else:
                return 'unknown'
        except Exception as e:
            logger.error(f"获取API状态异常: {e}")
            return 'error'

class SettingsDelegate:
    """设置代理"""
    
    def __init__(self, settings_view):
        self.settings_view = settings_view
    
    def tableview_did_select(self, tableview, section, row):
        try:
            item = self.settings_view.section_table.data_source.sections[section]['items'][row]
            action = item['action']
            
            # 根据action执行相应操作
            if action == 'api_siliconflow':
                self._show_siliconflow_settings()
            elif action == 'api_deepseek':
                self._show_deepseek_settings()
            elif action == 'api_test':
                self._test_apis()
            elif action == 'templates':
                self.settings_view.show_template_settings()
            elif action == 'formats':
                self._show_format_settings()
            elif action == 'cache':
                self._show_cache_settings()
            elif action == 'general':
                self.settings_view.show_general_settings()
            elif action == 'logs':
                self._show_log_settings()
            elif action == 'data':
                self._show_data_management()
            elif action == 'about':
                self.settings_view.show_about()
            elif action == 'help':
                self._show_help()
            elif action == 'feedback':
                self._show_feedback()
            
            # 取消选中状态
            tableview.selected_row = (-1, -1)
        
        except Exception as e:
            logger.exception(f"处理设置选择异常: {action}")
    
    def _show_siliconflow_settings(self):
        """显示硅基流动API设置"""
        try:
            current_key = config.get_api_key('siliconflow') or ''
            
            # 创建输入对话框
            key_input = self._create_api_key_input(
                title='硅基流动API密钥',
                message='请输入您的硅基流动API密钥',
                current_value=current_key,
                service='siliconflow'
            )
        except Exception as e:
            logger.exception("显示硅基流动API设置异常")
    
    def _show_deepseek_settings(self):
        """显示DeepSeekAPI设置"""
        try:
            current_key = config.get_api_key('deepseek') or ''
            
            # 创建输入对话框
            key_input = self._create_api_key_input(
                title='DeepSeek API密钥',
                message='请输入您的DeepSeek API密钥',
                current_value=current_key,
                service='deepseek'
            )
        except Exception as e:
            logger.exception("显示DeepSeek API设置异常")
    
    def _create_api_key_input(self, title: str, message: str, current_value: str, service: str):
        """创建API密钥输入对话框"""
        try:
            import console
            
            # 显示当前值（部分隐藏）
            if current_value:
                masked_value = current_value[:8] + '*' * (len(current_value) - 8)
                message += f'\n\n当前值: {masked_value}'
            
            # 获取新的API密钥
            new_key = console.input_alert(title, message, current_value, 'Set')
            
            if new_key is not None and new_key.strip():
                # 验证并保存API密钥
                if self._validate_and_save_api_key(service, new_key.strip()):
                    console.hud_alert('API密钥设置成功', 'success', 2)
                    # 刷新表格显示
                    self.settings_view.section_table.reload()
                else:
                    console.hud_alert('API密钥设置失败', 'error', 2)
        
        except Exception as e:
            logger.exception("创建API密钥输入异常")
    
    def _validate_and_save_api_key(self, service: str, api_key: str) -> bool:
        """验证并保存API密钥"""
        try:
            from ..utils.api_utils import APIUtils
            
            # 基本格式验证
            if not APIUtils.validate_api_key(api_key, service):
                return False
            
            # 保存API密钥
            success = config.set_api_key(service, api_key)
            if success:
                logger.info(f"{service} API密钥设置成功")
            
            return success
        
        except Exception as e:
            logger.error(f"验证和保存API密钥异常: {e}")
            return False
    
    def _test_apis(self):
        """测试API连接"""
        try:
            import console
            
            results = []
            
            # 测试硅基流动API
            try:
                from ..transcribe.siliconflow_client import SiliconFlowClient
                client = SiliconFlowClient()
                is_valid, message = client.validate_api_key()
                
                status = "✅ 正常" if is_valid else "❌ 异常"
                results.append(f"硅基流动API: {status}")
                if not is_valid:
                    results.append(f"  错误: {message}")
            except Exception as e:
                results.append(f"硅基流动API: ❌ 测试失败 - {str(e)}")
            
            # 测试DeepSeek API
            try:
                from ..ai_process.deepseek_client import DeepSeekClient
                client = DeepSeekClient()
                is_valid, message = client.validate_api_key()
                
                status = "✅ 正常" if is_valid else "❌ 异常"
                results.append(f"DeepSeek API: {status}")
                if not is_valid:
                    results.append(f"  错误: {message}")
            except Exception as e:
                results.append(f"DeepSeek API: ❌ 测试失败 - {str(e)}")
            
            # 显示结果
            result_text = '\n'.join(results)
            console.alert('API测试结果', result_text, 'OK', hide_cancel_button=True)
        
        except Exception as e:
            logger.exception("测试API异常")
    
    def _show_format_settings(self):
        """显示格式设置"""
        try:
            import console
            
            supported_formats = config.get('supported_formats', {})
            audio_formats = supported_formats.get('audio', [])
            video_formats = supported_formats.get('video', [])
            
            format_info = f'''支持的文件格式：

音频格式:
{', '.join(audio_formats)}

视频格式:
{', '.join(video_formats)}

注意：视频文件会先提取音频轨道再进行转录处理。'''
            
            console.alert('支持的文件格式', format_info, 'OK', hide_cancel_button=True)
        
        except Exception as e:
            logger.exception("显示格式设置异常")
    
    def _show_cache_settings(self):
        """显示缓存设置"""
        try:
            import console
            
            from ..utils.cache import cache
            cache_info = cache.get_cache_size()
            
            cache_text = f'''缓存信息：

文件数量: {cache_info.get('file_count', 0)}
占用空间: {cache_info.get('total_size_mb', 0):.1f} MB
内存项目: {cache_info.get('memory_items', 0)}

缓存用于存储转录和AI处理结果，可以提高重复处理的速度。'''
            
            # 询问是否清理缓存
            result = console.alert('缓存设置', cache_text, '清理缓存', '取消')
            if result == 1:  # 清理缓存
                if cache.clear():
                    console.hud_alert('缓存已清理', 'success', 2)
                else:
                    console.hud_alert('清理缓存失败', 'error', 2)
        
        except Exception as e:
            logger.exception("显示缓存设置异常")
    
    def _show_log_settings(self):
        """显示日志设置"""
        try:
            import console
            import os
            
            log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
            log_count = 0
            log_size = 0
            
            if os.path.exists(log_dir):
                for filename in os.listdir(log_dir):
                    if filename.endswith('.log'):
                        log_count += 1
                        log_path = os.path.join(log_dir, filename)
                        log_size += os.path.getsize(log_path)
            
            log_text = f'''日志信息：

日志文件数: {log_count}
占用空间: {log_size / (1024 * 1024):.1f} MB
日志目录: {log_dir}

日志用于记录应用运行状态和错误信息，有助于问题诊断。'''
            
            console.alert('日志设置', log_text, 'OK', hide_cancel_button=True)
        
        except Exception as e:
            logger.exception("显示日志设置异常")
    
    def _show_data_management(self):
        """显示数据管理"""
        try:
            import console
            
            data_text = '''数据管理：

• 清理缓存：删除所有转录和处理缓存
• 清理日志：删除应用日志文件
• 清理临时文件：删除处理过程中的临时文件
• 重置设置：恢复应用默认设置

注意：这些操作不可撤销，请谨慎操作！'''
            
            options = ['清理缓存', '清理日志', '清理临时文件', '重置设置', '取消']
            result = console.alert('数据管理', data_text, *options)
            
            if result == 1:  # 清理缓存
                self._clear_cache()
            elif result == 2:  # 清理日志
                self._clear_logs()
            elif result == 3:  # 清理临时文件
                self._clear_temp_files()
            elif result == 4:  # 重置设置
                self._reset_settings()
        
        except Exception as e:
            logger.exception("显示数据管理异常")
    
    def _clear_cache(self):
        """清理缓存"""
        try:
            from ..utils.cache import cache
            if cache.clear():
                import console
                console.hud_alert('缓存已清理', 'success', 2)
            else:
                console.hud_alert('清理缓存失败', 'error', 2)
        except Exception as e:
            logger.exception("清理缓存异常")
    
    def _clear_logs(self):
        """清理日志"""
        try:
            import os
            import shutil
            
            log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
            if os.path.exists(log_dir):
                shutil.rmtree(log_dir)
                os.makedirs(log_dir, exist_ok=True)
            
            import console
            console.hud_alert('日志已清理', 'success', 2)
        except Exception as e:
            logger.exception("清理日志异常")
    
    def _clear_temp_files(self):
        """清理临时文件"""
        try:
            from ..utils.file_utils import FileUtils
            cleaned_count = FileUtils.cleanup_temp_files()
            
            import console
            console.hud_alert(f'已清理 {cleaned_count} 个临时文件', 'success', 2)
        except Exception as e:
            logger.exception("清理临时文件异常")
    
    def _reset_settings(self):
        """重置设置"""
        try:
            import console
            
            # 确认操作
            result = console.alert('重置设置', '确定要重置所有设置吗？这将删除所有API密钥和自定义配置。', '确定', '取消')
            if result == 1:
                # 删除API密钥
                config.delete_api_key('siliconflow')
                config.delete_api_key('deepseek')
                
                # 重新加载默认配置
                # 这里需要重新初始化配置对象
                console.hud_alert('设置已重置', 'success', 2)
                
                # 刷新表格显示
                self.settings_view.section_table.reload()
        except Exception as e:
            logger.exception("重置设置异常")
    
    def _show_help(self):
        """显示帮助信息"""
        try:
            import console
            
            help_text = '''使用说明：

1. 配置API密钥
   - 设置硅基流动API密钥用于语音转文字
   - 设置DeepSeek API密钥用于AI文本处理

2. 添加音视频文件
   - 点击"添加文件"按钮
   - 通过分享扩展从其他应用分享文件
   - 支持多种音视频格式

3. 选择处理模板
   - 会议纪要：整理会议内容
   - 学习笔记：整理学习材料
   - 内容摘要：生成内容摘要
   - 自定义：使用自定义模板

4. 开始处理
   - 单独转录：仅进行语音转文字
   - AI整理：对已有文本进行AI处理
   - 一键处理：转录+AI整理完整流程

常见问题请查看应用文档。'''
            
            console.alert('使用帮助', help_text, 'OK', hide_cancel_button=True)
        except Exception as e:
            logger.exception("显示帮助信息异常")
    
    def _show_feedback(self):
        """显示反馈信息"""
        try:
            import console
            
            feedback_text = '''反馈渠道：

如果您在使用过程中遇到问题或有改进建议，欢迎通过以下方式反馈：

• 应用内反馈
• GitHub Issues
• 邮件反馈

您的反馈对我们改进产品非常重要！'''
            
            console.alert('反馈建议', feedback_text, 'OK', hide_cancel_button=True)
        except Exception as e:
            logger.exception("显示反馈信息异常")

class APISettingsView:
    """API设置子界面"""
    
    def __init__(self, app_controller):
        self.app_controller = app_controller
        # 实现API设置详细界面
    
    def show(self):
        pass

class TemplateSettingsView:
    """模板设置子界面"""
    
    def __init__(self, app_controller):
        self.app_controller = app_controller
        # 实现模板设置详细界面
    
    def show(self):
        pass

class GeneralSettingsView:
    """通用设置子界面"""
    
    def __init__(self, app_controller):
        self.app_controller = app_controller
        # 实现通用设置详细界面
    
    def show(self):
        pass

class AboutView:
    """关于界面"""
    
    def __init__(self):
        pass
    
    def show(self):
        try:
            import console
            
            about_text = f'''AI音视频转文字工具

版本: {config.get('version', '1.0.0')}
作者: AI Transcribe Team

功能特性:
• 支持多种音视频格式
• 高精度语音识别
• AI智能文本整理
• 丰富的处理模板
• iOS原生集成

技术支持:
• 硅基流动API - 语音转文字
• DeepSeek API - AI文本处理
• Pythonista UI框架

感谢您的使用！'''
            
            console.alert('关于', about_text, 'OK', hide_cancel_button=True)
        except Exception as e:
            logger.exception("显示关于信息异常")