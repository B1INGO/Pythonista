"""
AI音视频转文字工具主程序

协调整个应用的运行流程
"""

import threading
import time
from typing import Optional, List, Dict, Any, Callable

# Handle relative imports for direct execution
try:
    from .config import config
    from .utils.logger import get_logger
    from .core.media_processor import MediaProcessor
    from .transcribe.transcriber import Transcriber
    from .ai_process.text_processor import TextProcessor
    from .ios_integration.share_extension import ShareExtensionHandler
    from .ios_integration.file_handler import FileHandler
    from .ios_integration.url_scheme import URLSchemeHandler
    from .ui.main_view import MainView
    from .ui.progress_view import ProgressView, MultiStepProgressView
    from .ui.result_view import ResultView
    from .ui.settings_view import SettingsView
except ImportError:
    # Direct execution fallback
    from config import config
    from utils.logger import get_logger
    from core.media_processor import MediaProcessor
    from transcribe.transcriber import Transcriber
    from ai_process.text_processor import TextProcessor
    from ios_integration.share_extension import ShareExtensionHandler
    from ios_integration.file_handler import FileHandler
    from ios_integration.url_scheme import URLSchemeHandler
    from ui.main_view import MainView
    from ui.progress_view import ProgressView, MultiStepProgressView
    from ui.result_view import ResultView
    from ui.settings_view import SettingsView

logger = get_logger(__name__)

class AITranscribeApp:
    """AI转录应用主控制器"""
    
    def __init__(self):
        # 核心组件
        self.media_processor = MediaProcessor()
        self.transcriber = Transcriber()
        self.text_processor = TextProcessor()
        
        # iOS集成组件
        self.share_handler = ShareExtensionHandler()
        self.file_handler = FileHandler()
        self.url_handler = URLSchemeHandler()
        
        # UI组件
        self.main_view = None
        self.progress_view = None
        self.result_view = None
        self.settings_view = None
        
        # 状态管理
        self.current_processing = None
        self.processing_cancelled = False
        
        logger.info("AI转录应用初始化完成")
    
    def start(self, launch_args: Optional[Dict[str, Any]] = None):
        """启动应用"""
        try:
            logger.info("启动AI转录应用")
            
            # 创建UI组件
            self._create_ui_components()
            
            # 处理启动参数
            if launch_args:
                self._handle_launch_args(launch_args)
            
            # 检查是否从分享扩展启动
            self._check_share_extension()
            
            # 显示主界面
            self.show_main_view()
            
        except Exception as e:
            logger.exception("启动应用异常")
            self._show_error("启动失败", f"应用启动时发生错误: {str(e)}")
    
    def _create_ui_components(self):
        """创建UI组件"""
        try:
            self.main_view = MainView(self)
            self.result_view = ResultView(self)
            self.settings_view = SettingsView(self)
            
            logger.info("UI组件创建完成")
        except Exception as e:
            logger.exception("创建UI组件异常")
            raise
    
    def _handle_launch_args(self, launch_args: Dict[str, Any]):
        """处理启动参数"""
        try:
            # 处理URL Scheme调用
            if 'url' in launch_args:
                url = launch_args['url']
                success, action_data, error = self.url_handler.process_url_action(url)
                
                if success:
                    self._handle_url_action(action_data)
                else:
                    logger.warning(f"处理URL Scheme失败: {error}")
            
            # 处理文件路径
            if 'file_path' in launch_args:
                file_path = launch_args['file_path']
                self._handle_file_input(file_path)
        
        except Exception as e:
            logger.exception("处理启动参数异常")
    
    def _check_share_extension(self):
        """检查分享扩展"""
        try:
            if self.share_handler.is_extension_available():
                share_info = self.share_handler.get_share_info()
                
                if share_info.get('is_extension') and (
                    share_info.get('has_file') or 
                    share_info.get('has_url') or 
                    share_info.get('has_text')
                ):
                    # 从分享扩展处理文件
                    success, files, error = self.share_handler.handle_appex_files()
                    
                    if success and files:
                        for file_path in files:
                            self.main_view.add_file(file_path)
                        
                        logger.info(f"从分享扩展添加了 {len(files)} 个文件")
                    elif error:
                        logger.warning(f"处理分享扩展失败: {error}")
        
        except Exception as e:
            logger.exception("检查分享扩展异常")
    
    def _handle_url_action(self, action_data: Dict[str, Any]):
        """处理URL Action"""
        try:
            action_type = action_data.get('action_type')
            
            if action_type == 'transcribe':
                self._handle_transcribe_url_action(action_data)
            elif action_type == 'process':
                self._handle_process_url_action(action_data)
            elif action_type == 'open':
                self._handle_open_url_action(action_data)
            elif action_type == 'config':
                self._handle_config_url_action(action_data)
        
        except Exception as e:
            logger.exception("处理URL Action异常")
    
    def _handle_transcribe_url_action(self, action_data: Dict[str, Any]):
        """处理转录URL Action"""
        try:
            # 获取文件
            file_path = action_data.get('file_path')
            file_url = action_data.get('file_url')
            
            if file_path:
                self.main_view.add_file(file_path)
            elif file_url:
                success, processed_path, error = self.file_handler.handle_url_file(file_url)
                if success:
                    self.main_view.add_file(processed_path)
                else:
                    logger.warning(f"处理文件URL失败: {error}")
            
            # 如果设置了自动处理，直接开始转录
            if action_data.get('auto_process'):
                language = action_data.get('language', 'zh')
                callback_url = action_data.get('callback_url')
                
                # 启动自动转录
                self._start_auto_transcription(language, callback_url)
        
        except Exception as e:
            logger.exception("处理转录URL Action异常")
    
    def _handle_file_input(self, file_path: str):
        """处理文件输入"""
        try:
            success, processed_path, error = self.file_handler.handle_file_open(file_path)
            if success:
                self.main_view.add_file(processed_path)
            else:
                logger.warning(f"处理文件输入失败: {error}")
        except Exception as e:
            logger.exception("处理文件输入异常")
    
    def show_main_view(self):
        """显示主界面"""
        try:
            if self.main_view:
                self.main_view.show()
        except Exception as e:
            logger.exception("显示主界面异常")
    
    def show_settings(self):
        """显示设置界面"""
        try:
            if self.settings_view:
                self.settings_view.show()
        except Exception as e:
            logger.exception("显示设置界面异常")
    
    def start_transcription(self, files: List[Dict[str, Any]]):
        """启动转录流程"""
        try:
            if not files:
                self._show_error("错误", "没有选择要转录的文件")
                return
            
            logger.info(f"开始转录 {len(files)} 个文件")
            
            # 创建进度界面
            steps = ['媒体处理', '音频转录', '结果整理']
            self.progress_view = MultiStepProgressView(steps)
            self.progress_view.set_cancel_callback(self._cancel_processing)
            self.progress_view.show()
            
            # 标记处理状态
            self.processing_cancelled = False
            
            # 在后台线程中执行转录
            def transcribe_worker():
                try:
                    self._transcribe_files(files)
                except Exception as e:
                    logger.exception("转录工作线程异常")
                    self._show_processing_error(f"转录过程发生错误: {str(e)}")
            
            self.current_processing = threading.Thread(target=transcribe_worker, daemon=True)
            self.current_processing.start()
        
        except Exception as e:
            logger.exception("启动转录异常")
            self._show_error("错误", f"启动转录失败: {str(e)}")
    
    def _transcribe_files(self, files: List[Dict[str, Any]]):
        """转录文件"""
        try:
            all_results = []
            
            for i, file_info in enumerate(files):
                if self.processing_cancelled:
                    break
                
                file_path = file_info['path']
                file_name = file_info['name']
                
                logger.info(f"处理文件 {i+1}/{len(files)}: {file_name}")
                
                # 步骤1: 媒体处理
                self.progress_view.update_step(0, 0.0, f"处理文件: {file_name}", "正在预处理媒体文件...")
                
                success, audio_path, error = self.media_processor.process_media_file(file_path)
                if not success:
                    logger.error(f"媒体处理失败: {error}")
                    continue
                
                self.progress_view.update_step(0, 1.0, f"媒体处理完成", f"已处理: {file_name}")
                
                if self.processing_cancelled:
                    break
                
                # 步骤2: 音频转录
                self.progress_view.update_step(1, 0.0, f"转录音频: {file_name}", "正在调用语音识别API...")
                
                def transcribe_progress(progress, message):
                    if not self.processing_cancelled:
                        self.progress_view.update_step(1, progress, f"转录音频: {file_name}", message)
                
                success, transcribed_text, error = self.transcriber.transcribe(
                    audio_path, 
                    language='zh',
                    progress_callback=transcribe_progress
                )
                
                if not success:
                    logger.error(f"音频转录失败: {error}")
                    self.progress_view.update_step(1, 0.0, f"转录失败: {file_name}", error or "转录过程出错")
                    continue
                
                self.progress_view.update_step(1, 1.0, f"转录完成: {file_name}", f"转录了 {len(transcribed_text)} 个字符")
                
                # 保存结果
                result = {
                    'file_name': file_name,
                    'file_path': file_path,
                    'transcription': transcribed_text,
                    'processing_time': time.time()
                }
                all_results.append(result)
            
            if not self.processing_cancelled and all_results:
                # 步骤3: 结果整理
                self.progress_view.update_step(2, 0.5, "整理结果", "正在合并转录结果...")
                
                # 合并所有转录结果
                combined_result = self._combine_transcription_results(all_results)
                
                self.progress_view.update_step(2, 1.0, "转录完成", f"成功转录 {len(all_results)} 个文件")
                
                # 显示结果
                self._show_transcription_result(combined_result)
            
            # 清理资源
            self.media_processor.cleanup_temp_files()
            self.transcriber.cleanup()
        
        except Exception as e:
            logger.exception("转录文件异常")
            self._show_processing_error(f"转录过程发生错误: {str(e)}")
    
    def start_ai_processing(self, template_id: str, text: Optional[str] = None):
        """启动AI处理流程"""
        try:
            if not text:
                # 从最近的转录结果获取文本
                # 这里应该有一个机制来获取最近的转录文本
                self._show_error("错误", "没有可处理的文本")
                return
            
            logger.info(f"开始AI处理，模板: {template_id}")
            
            # 创建进度界面
            self.progress_view = ProgressView()
            self.progress_view.set_cancel_callback(self._cancel_processing)
            self.progress_view.show()
            
            # 标记处理状态
            self.processing_cancelled = False
            
            # 在后台线程中执行AI处理
            def process_worker():
                try:
                    self._process_text_with_ai(text, template_id)
                except Exception as e:
                    logger.exception("AI处理工作线程异常")
                    self._show_processing_error(f"AI处理过程发生错误: {str(e)}")
            
            self.current_processing = threading.Thread(target=process_worker, daemon=True)
            self.current_processing.start()
        
        except Exception as e:
            logger.exception("启动AI处理异常")
            self._show_error("错误", f"启动AI处理失败: {str(e)}")
    
    def start_complete_processing(self, files: List[Dict[str, Any]], template_id: str):
        """启动完整处理流程（转录+AI处理）"""
        try:
            if not files:
                self._show_error("错误", "没有选择要处理的文件")
                return
            
            logger.info(f"开始完整处理 {len(files)} 个文件，模板: {template_id}")
            
            # 创建进度界面
            steps = ['媒体处理', '音频转录', 'AI文本处理', '结果整理']
            self.progress_view = MultiStepProgressView(steps)
            self.progress_view.set_cancel_callback(self._cancel_processing)
            self.progress_view.show()
            
            # 标记处理状态
            self.processing_cancelled = False
            
            # 在后台线程中执行完整处理
            def complete_worker():
                try:
                    self._complete_processing(files, template_id)
                except Exception as e:
                    logger.exception("完整处理工作线程异常")
                    self._show_processing_error(f"处理过程发生错误: {str(e)}")
            
            self.current_processing = threading.Thread(target=complete_worker, daemon=True)
            self.current_processing.start()
        
        except Exception as e:
            logger.exception("启动完整处理异常")
            self._show_error("错误", f"启动完整处理失败: {str(e)}")
    
    def _complete_processing(self, files: List[Dict[str, Any]], template_id: str):
        """执行完整处理流程"""
        try:
            # 首先进行转录
            transcription_results = []
            
            for i, file_info in enumerate(files):
                if self.processing_cancelled:
                    break
                
                file_path = file_info['path']
                file_name = file_info['name']
                
                # 媒体处理
                self.progress_view.update_step(0, i/len(files), f"处理文件: {file_name}", "正在预处理媒体文件...")
                
                success, audio_path, error = self.media_processor.process_media_file(file_path)
                if not success:
                    logger.error(f"媒体处理失败: {error}")
                    continue
                
                # 音频转录
                self.progress_view.update_step(1, i/len(files), f"转录音频: {file_name}", "正在调用语音识别API...")
                
                success, transcribed_text, error = self.transcriber.transcribe(audio_path, language='zh')
                if success:
                    transcription_results.append({
                        'file_name': file_name,
                        'transcription': transcribed_text
                    })
            
            if self.processing_cancelled or not transcription_results:
                return
            
            # 合并转录结果
            combined_text = '\n\n'.join([r['transcription'] for r in transcription_results])
            
            # AI文本处理
            self.progress_view.update_step(2, 0.0, "AI文本处理", f"使用模板: {template_id}")
            
            def ai_progress(progress, message):
                if not self.processing_cancelled:
                    self.progress_view.update_step(2, progress, "AI文本处理", message)
            
            success, processed_text, error = self.text_processor.process_with_template(
                combined_text,
                template_id,
                progress_callback=ai_progress
            )
            
            if not success:
                logger.error(f"AI文本处理失败: {error}")
                self._show_processing_error(f"AI处理失败: {error}")
                return
            
            # 结果整理
            self.progress_view.update_step(3, 0.5, "整理结果", "正在生成最终结果...")
            
            final_result = {
                'title': f'AI处理结果 - {template_id}',
                'content': {
                    'transcription': combined_text,
                    'ai_processed': processed_text
                },
                'metadata': {
                    'files_processed': len(transcription_results),
                    'template_used': template_id,
                    'processing_time': time.time(),
                    'word_count': len(processed_text)
                },
                'original_transcription': combined_text
            }
            
            self.progress_view.update_step(3, 1.0, "处理完成", f"成功处理 {len(files)} 个文件")
            
            # 显示结果
            self._show_final_result(final_result)
        
        except Exception as e:
            logger.exception("完整处理异常")
            self._show_processing_error(f"处理过程发生错误: {str(e)}")
    
    def _cancel_processing(self):
        """取消处理"""
        try:
            self.processing_cancelled = True
            logger.info("用户取消了处理")
            
            # 通知各组件取消处理
            if hasattr(self.transcriber, 'cancel'):
                self.transcriber.cancel()
            
            if hasattr(self.text_processor, 'cancel'):
                self.text_processor.cancel()
            
            # 清理资源
            self.media_processor.cleanup_temp_files()
            self.transcriber.cleanup()
        
        except Exception as e:
            logger.exception("取消处理异常")
    
    def _combine_transcription_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """合并转录结果"""
        try:
            combined_text = []
            total_files = len(results)
            
            for i, result in enumerate(results):
                file_name = result['file_name']
                transcription = result['transcription']
                
                combined_text.append(f"=== 文件 {i+1}: {file_name} ===")
                combined_text.append("")
                combined_text.append(transcription)
                combined_text.append("")
            
            return {
                'title': f'转录结果 - {total_files} 个文件',
                'content': '\n'.join(combined_text),
                'metadata': {
                    'files_processed': total_files,
                    'processing_time': time.time(),
                    'total_characters': sum(len(r['transcription']) for r in results)
                }
            }
        
        except Exception as e:
            logger.exception("合并转录结果异常")
            return {
                'title': '转录结果',
                'content': '合并结果时发生错误',
                'metadata': {}
            }
    
    def _show_transcription_result(self, result: Dict[str, Any]):
        """显示转录结果"""
        try:
            # 隐藏进度界面
            if self.progress_view:
                self.progress_view.hide()
            
            # 显示结果界面
            self.result_view.show_result(result)
            self.result_view.show()
        
        except Exception as e:
            logger.exception("显示转录结果异常")
    
    def _show_final_result(self, result: Dict[str, Any]):
        """显示最终结果"""
        try:
            # 隐藏进度界面
            if self.progress_view:
                self.progress_view.hide()
            
            # 显示结果界面
            self.result_view.show_result(result)
            self.result_view.show()
        
        except Exception as e:
            logger.exception("显示最终结果异常")
    
    def _show_processing_error(self, error_message: str):
        """显示处理错误"""
        try:
            if self.progress_view:
                self.progress_view.show_error(error_message)
        except Exception as e:
            logger.exception("显示处理错误异常")
    
    def _show_error(self, title: str, message: str):
        """显示错误对话框"""
        try:
            import console
            console.alert(title, message, 'OK', hide_cancel_button=True)
        except Exception as e:
            logger.error(f"显示错误对话框失败: {e}")
            print(f"{title}: {message}")
    
    def show_reprocess_options(self, original_text: str):
        """显示重新处理选项"""
        try:
            # 这里可以实现重新处理的界面
            # 暂时使用简单的模板选择
            import console
            
            templates = ['会议纪要', '学习笔记', '内容摘要', '自定义清理']
            template_ids = ['meeting_notes', 'study_notes', 'content_summary', 'custom_cleanup']
            
            result = console.alert('选择处理模板', '请选择要使用的AI处理模板：', *templates)
            
            if 1 <= result <= len(template_ids):
                template_id = template_ids[result - 1]
                self.start_ai_processing(template_id, original_text)
        
        except Exception as e:
            logger.exception("显示重新处理选项异常")
    
    def cleanup(self):
        """清理应用资源"""
        try:
            # 取消正在进行的处理
            if self.current_processing and self.current_processing.is_alive():
                self._cancel_processing()
                self.current_processing.join(timeout=5.0)
            
            # 清理各组件资源
            self.media_processor.cleanup_temp_files()
            self.transcriber.cleanup()
            self.share_handler.cleanup_temp_files()
            self.file_handler.cleanup_temp_files()
            
            logger.info("应用资源清理完成")
        
        except Exception as e:
            logger.exception("清理应用资源异常")

def main():
    """主函数"""
    try:
        # 创建应用实例
        app = AITranscribeApp()
        
        # 检查系统要求
        issues = _check_system_requirements()
        if issues:
            logger.warning(f"系统检查发现问题: {issues}")
        
        # 启动应用
        app.start()
        
        return app
    
    except Exception as e:
        logger.exception("主函数异常")
        print(f"启动应用失败: {str(e)}")
        return None

def _check_system_requirements() -> List[str]:
    """检查系统要求"""
    issues = []
    
    try:
        # 检查Python版本
        import sys
        if sys.version_info < (3, 6):
            issues.append("需要Python 3.6或更高版本")
        
        # 检查必需模块
        required_modules = ['ui', 'requests']
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                issues.append(f"缺少必需模块: {module}")
        
        # 检查iOS环境
        try:
            import objc_util
            logger.info("检测到iOS环境")
        except ImportError:
            logger.warning("未检测到iOS环境，部分功能可能不可用")
        
        # 检查Pythonista UI
        try:
            import ui
            logger.info("Pythonista UI可用")
        except ImportError:
            issues.append("Pythonista UI不可用")
    
    except Exception as e:
        logger.error(f"系统检查异常: {e}")
        issues.append(f"系统检查失败: {str(e)}")
    
    return issues

# 如果作为脚本直接运行
if __name__ == '__main__':
    app = main()
    
    # 保持应用运行
    if app:
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("收到退出信号")
            app.cleanup()
        except Exception as e:
            logger.exception("应用运行异常")
            if app:
                app.cleanup()