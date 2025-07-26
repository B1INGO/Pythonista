"""
进度界面模块

实时显示处理进度
"""

import ui
import threading
import time
from typing import Optional, Callable
from ..utils.logger import get_logger

logger = get_logger(__name__)

class ProgressView:
    """进度界面类"""
    
    def __init__(self):
        self.view = None
        self.progress_bar = None
        self.status_label = None
        self.detail_label = None
        self.cancel_button = None
        self.progress_value = 0.0
        self.is_cancelled = False
        self.cancel_callback = None
        
        self._create_ui()
    
    def _create_ui(self):
        """创建进度界面"""
        try:
            # 主视图
            self.view = ui.View(name='处理进度')
            self.view.background_color = '#f0f0f0'
            self.view.frame = (0, 0, 300, 200)
            
            # 标题
            title_label = ui.Label(name='title_label')
            title_label.text = '正在处理...'
            title_label.font = ('<system-bold>', 18)
            title_label.text_color = '#333333'
            title_label.alignment = ui.ALIGN_CENTER
            title_label.frame = (0, 20, self.view.width, 30)
            title_label.flex = 'W'
            self.view.add_subview(title_label)
            
            # 进度条
            self.progress_bar = ui.View(name='progress_container')
            self.progress_bar.background_color = '#e0e0e0'
            self.progress_bar.corner_radius = 5
            self.progress_bar.frame = (20, 70, self.view.width - 40, 10)
            self.progress_bar.flex = 'W'
            self.view.add_subview(self.progress_bar)
            
            # 进度填充
            self.progress_fill = ui.View(name='progress_fill')
            self.progress_fill.background_color = '#007AFF'
            self.progress_fill.corner_radius = 5
            self.progress_fill.frame = (0, 0, 0, 10)
            self.progress_bar.add_subview(self.progress_fill)
            
            # 状态标签
            self.status_label = ui.Label(name='status_label')
            self.status_label.text = '准备中...'
            self.status_label.font = ('<system>', 16)
            self.status_label.text_color = '#666666'
            self.status_label.alignment = ui.ALIGN_CENTER
            self.status_label.frame = (20, 100, self.view.width - 40, 25)
            self.status_label.flex = 'W'
            self.view.add_subview(self.status_label)
            
            # 详细信息标签
            self.detail_label = ui.Label(name='detail_label')
            self.detail_label.text = ''
            self.detail_label.font = ('<system>', 14)
            self.detail_label.text_color = '#999999'
            self.detail_label.alignment = ui.ALIGN_CENTER
            self.detail_label.number_of_lines = 2
            self.detail_label.frame = (20, 130, self.view.width - 40, 35)
            self.detail_label.flex = 'W'
            self.view.add_subview(self.detail_label)
            
            # 取消按钮
            self.cancel_button = ui.Button(name='cancel_button')
            self.cancel_button.title = '取消'
            self.cancel_button.font = ('<system>', 16)
            self.cancel_button.background_color = '#FF3B30'
            self.cancel_button.tint_color = 'white'
            self.cancel_button.corner_radius = 8
            self.cancel_button.frame = (self.view.width/2 - 40, 175, 80, 35)
            self.cancel_button.flex = 'LR'
            self.cancel_button.action = self._cancel_action
            self.view.add_subview(self.cancel_button)
            
            logger.info("进度界面创建完成")
        
        except Exception as e:
            logger.exception("创建进度界面异常")
            raise
    
    def update_progress(self, progress: float, status: str, detail: str = ''):
        """
        更新进度显示
        
        Args:
            progress: 进度值 (0.0 - 1.0)
            status: 状态文本
            detail: 详细信息
        """
        try:
            # 确保在主线程中更新UI
            def update_ui():
                try:
                    # 更新进度条
                    self.progress_value = max(0.0, min(1.0, progress))
                    progress_width = self.progress_bar.width * self.progress_value
                    self.progress_fill.frame = (0, 0, progress_width, 10)
                    
                    # 更新文本
                    self.status_label.text = status
                    if detail:
                        self.detail_label.text = detail
                    
                    # 更新进度百分比显示
                    percent = int(self.progress_value * 100)
                    if hasattr(self.view, 'superview') and self.view.superview:
                        self.view.name = f'处理进度 ({percent}%)'
                    
                    logger.debug(f"进度更新: {percent}% - {status}")
                
                except Exception as e:
                    logger.error(f"更新进度UI异常: {e}")
            
            # 在主线程中执行UI更新
            if threading.current_thread() == threading.main_thread():
                update_ui()
            else:
                # 如果在其他线程中，需要调度到主线程
                import dispatch
                dispatch.async_main(update_ui)
        
        except Exception as e:
            logger.error(f"更新进度异常: {e}")
    
    def set_indeterminate(self, indeterminate: bool = True):
        """设置为不确定进度模式"""
        try:
            if indeterminate:
                # 创建动画效果
                self._start_indeterminate_animation()
            else:
                self._stop_indeterminate_animation()
        
        except Exception as e:
            logger.error(f"设置不确定进度模式异常: {e}")
    
    def _start_indeterminate_animation(self):
        """开始不确定进度动画"""
        def animate():
            while not self.is_cancelled and hasattr(self, '_indeterminate_running'):
                try:
                    # 创建来回移动的动画效果
                    for i in range(20):
                        if self.is_cancelled or not hasattr(self, '_indeterminate_running'):
                            break
                        
                        progress = i / 20.0
                        self.update_progress(progress, self.status_label.text)
                        time.sleep(0.1)
                    
                    for i in range(20, 0, -1):
                        if self.is_cancelled or not hasattr(self, '_indeterminate_running'):
                            break
                        
                        progress = i / 20.0
                        self.update_progress(progress, self.status_label.text)
                        time.sleep(0.1)
                
                except Exception as e:
                    logger.error(f"不确定进度动画异常: {e}")
                    break
        
        try:
            self._indeterminate_running = True
            self._animation_thread = threading.Thread(target=animate, daemon=True)
            self._animation_thread.start()
        
        except Exception as e:
            logger.error(f"启动不确定进度动画异常: {e}")
    
    def _stop_indeterminate_animation(self):
        """停止不确定进度动画"""
        try:
            if hasattr(self, '_indeterminate_running'):
                delattr(self, '_indeterminate_running')
        except Exception as e:
            logger.error(f"停止不确定进度动画异常: {e}")
    
    def _cancel_action(self, sender):
        """取消操作"""
        try:
            self.is_cancelled = True
            
            # 更新UI显示
            self.status_label.text = '正在取消...'
            self.cancel_button.enabled = False
            self.cancel_button.title = '取消中'
            
            # 调用取消回调
            if self.cancel_callback:
                try:
                    self.cancel_callback()
                except Exception as e:
                    logger.error(f"执行取消回调异常: {e}")
            
            logger.info("用户取消了操作")
        
        except Exception as e:
            logger.exception("取消操作异常")
    
    def set_cancel_callback(self, callback: Callable[[], None]):
        """设置取消回调函数"""
        self.cancel_callback = callback
    
    def show_completion(self, success: bool, message: str):
        """显示完成状态"""
        try:
            if success:
                self.update_progress(1.0, '处理完成', message)
                self.progress_fill.background_color = '#34C759'  # 绿色
                self.cancel_button.title = '完成'
                self.cancel_button.background_color = '#34C759'
            else:
                self.progress_fill.background_color = '#FF3B30'  # 红色
                self.status_label.text = '处理失败'
                self.detail_label.text = message
                self.cancel_button.title = '关闭'
                self.cancel_button.background_color = '#FF3B30'
            
            self.cancel_button.enabled = True
            
            # 停止动画
            self._stop_indeterminate_animation()
            
        except Exception as e:
            logger.error(f"显示完成状态异常: {e}")
    
    def show_error(self, error_message: str):
        """显示错误状态"""
        self.show_completion(False, error_message)
    
    def reset(self):
        """重置进度界面"""
        try:
            self.progress_value = 0.0
            self.is_cancelled = False
            
            self.update_progress(0.0, '准备中...', '')
            self.progress_fill.background_color = '#007AFF'
            
            self.cancel_button.enabled = True
            self.cancel_button.title = '取消'
            self.cancel_button.background_color = '#FF3B30'
            
            self._stop_indeterminate_animation()
            
        except Exception as e:
            logger.error(f"重置进度界面异常: {e}")
    
    def show(self, parent_view: Optional[ui.View] = None):
        """显示进度界面"""
        try:
            if parent_view:
                # 作为子视图显示
                parent_view.add_subview(self.view)
                # 居中显示
                x = (parent_view.width - self.view.width) / 2
                y = (parent_view.height - self.view.height) / 2
                self.view.frame = (x, y, self.view.width, self.view.height)
            else:
                # 作为独立视图显示
                self.view.present('popover', hide_title_bar=False)
        
        except Exception as e:
            logger.exception("显示进度界面异常")
    
    def hide(self):
        """隐藏进度界面"""
        try:
            self._stop_indeterminate_animation()
            
            if self.view.superview:
                self.view.remove_from_superview()
            elif hasattr(self.view, 'close'):
                self.view.close()
        
        except Exception as e:
            logger.error(f"隐藏进度界面异常: {e}")
    
    def is_visible(self) -> bool:
        """检查进度界面是否可见"""
        try:
            return bool(self.view.superview) or bool(getattr(self.view, 'on_screen', False))
        except Exception as e:
            logger.error(f"检查进度界面可见性异常: {e}")
            return False

class MultiStepProgressView(ProgressView):
    """多步骤进度界面"""
    
    def __init__(self, steps: list):
        self.steps = steps
        self.current_step = 0
        self.step_progress = 0.0
        
        super().__init__()
        
        # 添加步骤指示器
        self._create_step_indicator()
    
    def _create_step_indicator(self):
        """创建步骤指示器"""
        try:
            # 调整现有组件位置
            self.progress_bar.frame = (20, 90, self.view.width - 40, 10)
            self.status_label.frame = (20, 110, self.view.width - 40, 25)
            self.detail_label.frame = (20, 140, self.view.width - 40, 35)
            self.cancel_button.frame = (self.view.width/2 - 40, 185, 80, 35)
            
            # 扩展视图高度
            self.view.frame = (0, 0, self.view.width, 230)
            
            # 步骤指示器
            steps_label = ui.Label(name='steps_label')
            steps_label.text = f'步骤 1/{len(self.steps)}: {self.steps[0] if self.steps else ""}'
            steps_label.font = ('<system>', 14)
            steps_label.text_color = '#007AFF'
            steps_label.alignment = ui.ALIGN_CENTER
            steps_label.frame = (20, 55, self.view.width - 40, 20)
            steps_label.flex = 'W'
            self.view.add_subview(steps_label)
            
            self.steps_label = steps_label
            
        except Exception as e:
            logger.error(f"创建步骤指示器异常: {e}")
    
    def update_step(self, step_index: int, step_progress: float = 0.0, status: str = '', detail: str = ''):
        """更新步骤进度"""
        try:
            if 0 <= step_index < len(self.steps):
                self.current_step = step_index
                self.step_progress = step_progress
                
                # 计算总进度
                total_progress = (step_index + step_progress) / len(self.steps)
                
                # 更新步骤显示
                if hasattr(self, 'steps_label'):
                    self.steps_label.text = f'步骤 {step_index + 1}/{len(self.steps)}: {self.steps[step_index]}'
                
                # 更新状态
                if not status:
                    status = f'正在执行: {self.steps[step_index]}'
                
                self.update_progress(total_progress, status, detail)
        
        except Exception as e:
            logger.error(f"更新步骤进度异常: {e}")
    
    def next_step(self, status: str = '', detail: str = ''):
        """进入下一步骤"""
        if self.current_step < len(self.steps) - 1:
            self.update_step(self.current_step + 1, 0.0, status, detail)
    
    def complete_current_step(self, status: str = '', detail: str = ''):
        """完成当前步骤"""
        self.update_step(self.current_step, 1.0, status, detail)