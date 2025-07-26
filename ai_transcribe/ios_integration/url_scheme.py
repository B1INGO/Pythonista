"""
URL Scheme处理模块

支持从其他应用调用
"""

import urllib.parse
from typing import Tuple, Optional, Dict, Any, List
from ..utils.logger import get_logger

logger = get_logger(__name__)

class URLSchemeHandler:
    """URL Scheme处理器"""
    
    def __init__(self):
        self.supported_schemes = ['ai-transcribe', 'pythonista-ai-transcribe']
        self.supported_actions = ['transcribe', 'process', 'open', 'config']
    
    def handle_url_scheme(self, url: str) -> Tuple[bool, Dict[str, Any], Optional[str]]:
        """
        处理URL Scheme调用
        
        Args:
            url: URL scheme字符串
            
        Returns:
            (success, parsed_data, error_message)
        """
        try:
            if not url:
                return False, {}, "URL为空"
            
            logger.info(f"处理URL Scheme: {url}")
            
            # 解析URL
            parsed_url = urllib.parse.urlparse(url)
            
            # 验证scheme
            if parsed_url.scheme not in self.supported_schemes:
                return False, {}, f"不支持的URL scheme: {parsed_url.scheme}"
            
            # 解析action
            action = parsed_url.netloc or parsed_url.path.lstrip('/')
            if not action:
                return False, {}, "缺少action"
            
            # 解析参数
            query_params = urllib.parse.parse_qs(parsed_url.query)
            
            # 构建结果数据
            result_data = {
                'scheme': parsed_url.scheme,
                'action': action,
                'params': self._normalize_params(query_params),
                'fragment': parsed_url.fragment
            }
            
            # 验证action
            if action not in self.supported_actions:
                logger.warning(f"不支持的action: {action}")
                result_data['warning'] = f"不支持的action: {action}"
            
            logger.info(f"URL Scheme解析成功: action={action}")
            return True, result_data, None
        
        except Exception as e:
            logger.exception(f"处理URL Scheme异常: {url}")
            return False, {}, f"处理URL Scheme错误: {str(e)}"
    
    def _normalize_params(self, query_params: Dict[str, List[str]]) -> Dict[str, Any]:
        """标准化查询参数"""
        try:
            normalized = {}
            
            for key, values in query_params.items():
                if len(values) == 1:
                    # 单值参数
                    value = values[0]
                    
                    # 尝试转换类型
                    if value.lower() in ['true', 'false']:
                        normalized[key] = value.lower() == 'true'
                    elif value.isdigit():
                        normalized[key] = int(value)
                    elif self._is_float(value):
                        normalized[key] = float(value)
                    else:
                        normalized[key] = value
                else:
                    # 多值参数
                    normalized[key] = values
            
            return normalized
        
        except Exception as e:
            logger.error(f"标准化参数失败: {e}")
            return {}
    
    def _is_float(self, value: str) -> bool:
        """检查字符串是否为浮点数"""
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    def handle_transcribe_action(self, params: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], Optional[str]]:
        """
        处理转录action
        
        支持的参数:
        - file: 文件路径
        - url: 文件URL
        - text: 直接文本内容
        - language: 语言代码
        - callback: 回调URL
        """
        try:
            action_data = {
                'action_type': 'transcribe',
                'file_path': params.get('file'),
                'file_url': params.get('url'),
                'text_content': params.get('text'),
                'language': params.get('language', 'zh'),
                'callback_url': params.get('callback'),
                'auto_process': params.get('auto_process', False)
            }
            
            # 验证输入源
            if not any([action_data['file_path'], action_data['file_url'], action_data['text_content']]):
                return False, {}, "缺少输入源（file、url或text参数）"
            
            logger.info(f"转录action数据: {action_data}")
            return True, action_data, None
        
        except Exception as e:
            logger.error(f"处理转录action失败: {e}")
            return False, {}, f"处理转录action错误: {str(e)}"
    
    def handle_process_action(self, params: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], Optional[str]]:
        """
        处理文本处理action
        
        支持的参数:
        - text: 要处理的文本
        - template: 模板ID
        - prompt: 自定义提示词
        - system_prompt: 系统提示词
        - callback: 回调URL
        """
        try:
            action_data = {
                'action_type': 'process',
                'text_content': params.get('text'),
                'template_id': params.get('template'),
                'custom_prompt': params.get('prompt'),
                'system_prompt': params.get('system_prompt'),
                'callback_url': params.get('callback')
            }
            
            # 验证输入
            if not action_data['text_content']:
                return False, {}, "缺少要处理的文本（text参数）"
            
            if not action_data['template_id'] and not action_data['custom_prompt']:
                return False, {}, "缺少处理方式（template或prompt参数）"
            
            logger.info(f"处理action数据: {action_data}")
            return True, action_data, None
        
        except Exception as e:
            logger.error(f"处理文本处理action失败: {e}")
            return False, {}, f"处理文本处理action错误: {str(e)}"
    
    def handle_open_action(self, params: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], Optional[str]]:
        """
        处理打开文件action
        
        支持的参数:
        - file: 文件路径
        - url: 文件URL
        - view: 指定要打开的视图
        """
        try:
            action_data = {
                'action_type': 'open',
                'file_path': params.get('file'),
                'file_url': params.get('url'),
                'target_view': params.get('view', 'main')
            }
            
            # 验证输入源
            if not action_data['file_path'] and not action_data['file_url']:
                return False, {}, "缺少文件源（file或url参数）"
            
            logger.info(f"打开action数据: {action_data}")
            return True, action_data, None
        
        except Exception as e:
            logger.error(f"处理打开action失败: {e}")
            return False, {}, f"处理打开action错误: {str(e)}"
    
    def handle_config_action(self, params: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], Optional[str]]:
        """
        处理配置action
        
        支持的参数:
        - view: 配置视图类型（api, templates, settings）
        - api_service: API服务类型
        - api_key: API密钥
        """
        try:
            action_data = {
                'action_type': 'config',
                'config_view': params.get('view', 'settings'),
                'api_service': params.get('api_service'),
                'api_key': params.get('api_key')
            }
            
            logger.info(f"配置action数据: {action_data}")
            return True, action_data, None
        
        except Exception as e:
            logger.error(f"处理配置action失败: {e}")
            return False, {}, f"处理配置action错误: {str(e)}"
    
    def process_url_action(self, url: str) -> Tuple[bool, Dict[str, Any], Optional[str]]:
        """
        完整处理URL action
        
        Args:
            url: URL scheme字符串
            
        Returns:
            (success, action_data, error_message)
        """
        try:
            # 解析URL
            success, parsed_data, error = self.handle_url_scheme(url)
            if not success:
                return False, {}, error
            
            action = parsed_data['action']
            params = parsed_data['params']
            
            # 根据action类型处理
            if action == 'transcribe':
                return self.handle_transcribe_action(params)
            elif action == 'process':
                return self.handle_process_action(params)
            elif action == 'open':
                return self.handle_open_action(params)
            elif action == 'config':
                return self.handle_config_action(params)
            else:
                return False, {}, f"不支持的action: {action}"
        
        except Exception as e:
            logger.exception(f"处理URL action异常: {url}")
            return False, {}, f"处理URL action错误: {str(e)}"
    
    def generate_callback_url(self, callback_base: str, result_data: Dict[str, Any]) -> str:
        """
        生成回调URL
        
        Args:
            callback_base: 回调URL基础部分
            result_data: 结果数据
            
        Returns:
            str: 完整的回调URL
        """
        try:
            if not callback_base:
                return ""
            
            # 准备回调参数
            callback_params = {}
            
            if 'success' in result_data:
                callback_params['success'] = str(result_data['success']).lower()
            
            if 'result' in result_data:
                # 对结果进行URL编码
                callback_params['result'] = result_data['result']
            
            if 'error' in result_data:
                callback_params['error'] = result_data['error']
            
            if 'file_path' in result_data:
                callback_params['file'] = result_data['file_path']
            
            # 构建查询字符串
            query_string = urllib.parse.urlencode(callback_params, quote_via=urllib.parse.quote)
            
            # 组合完整URL
            if '?' in callback_base:
                callback_url = f"{callback_base}&{query_string}"
            else:
                callback_url = f"{callback_base}?{query_string}"
            
            logger.info(f"生成回调URL: {callback_url}")
            return callback_url
        
        except Exception as e:
            logger.error(f"生成回调URL失败: {e}")
            return callback_base
    
    def get_example_urls(self) -> Dict[str, List[str]]:
        """获取示例URL"""
        return {
            'transcribe': [
                'ai-transcribe://transcribe?file=/path/to/audio.mp3&language=zh',
                'ai-transcribe://transcribe?url=file:///path/to/video.mp4&auto_process=true',
                'ai-transcribe://transcribe?text=这是测试文本&callback=myapp://callback'
            ],
            'process': [
                'ai-transcribe://process?text=会议内容...&template=meeting_notes',
                'ai-transcribe://process?text=课程内容...&prompt=请整理成学习笔记',
                'ai-transcribe://process?text=内容...&template=custom_summary&callback=myapp://result'
            ],
            'open': [
                'ai-transcribe://open?file=/path/to/audio.wav',
                'ai-transcribe://open?url=file:///path/to/video.mp4&view=main',
                'ai-transcribe://open?view=settings'
            ],
            'config': [
                'ai-transcribe://config?view=api',
                'ai-transcribe://config?view=templates',
                'ai-transcribe://config?api_service=siliconflow&api_key=sk-xxx'
            ]
        }
    
    def validate_url_format(self, url: str) -> Tuple[bool, List[str]]:
        """验证URL格式"""
        try:
            issues = []
            
            if not url:
                issues.append("URL不能为空")
                return False, issues
            
            # 解析URL
            try:
                parsed_url = urllib.parse.urlparse(url)
            except Exception as e:
                issues.append(f"URL格式无效: {str(e)}")
                return False, issues
            
            # 检查scheme
            if not parsed_url.scheme:
                issues.append("缺少URL scheme")
            elif parsed_url.scheme not in self.supported_schemes:
                issues.append(f"不支持的URL scheme: {parsed_url.scheme}")
            
            # 检查action
            action = parsed_url.netloc or parsed_url.path.lstrip('/')
            if not action:
                issues.append("缺少action")
            elif action not in self.supported_actions:
                issues.append(f"不支持的action: {action}")
            
            # 检查必需参数（基于action类型）
            query_params = urllib.parse.parse_qs(parsed_url.query)
            
            if action == 'transcribe':
                if not any(param in query_params for param in ['file', 'url', 'text']):
                    issues.append("转录action缺少输入源参数（file、url或text）")
            
            elif action == 'process':
                if 'text' not in query_params:
                    issues.append("处理action缺少text参数")
                if not any(param in query_params for param in ['template', 'prompt']):
                    issues.append("处理action缺少处理方式参数（template或prompt）")
            
            elif action == 'open':
                if not any(param in query_params for param in ['file', 'url']):
                    issues.append("打开action缺少文件源参数（file或url）")
            
            success = len(issues) == 0
            return success, issues
        
        except Exception as e:
            logger.error(f"验证URL格式异常: {e}")
            return False, [f"验证过程发生错误: {str(e)}"]
    
    def get_scheme_info(self) -> Dict[str, Any]:
        """获取URL Scheme信息"""
        return {
            'supported_schemes': self.supported_schemes,
            'supported_actions': self.supported_actions,
            'examples': self.get_example_urls(),
            'documentation': {
                'transcribe': {
                    'description': '转录音视频文件或文本',
                    'required_params': ['file/url/text'],
                    'optional_params': ['language', 'callback', 'auto_process']
                },
                'process': {
                    'description': '使用AI处理文本',
                    'required_params': ['text', 'template/prompt'],
                    'optional_params': ['system_prompt', 'callback']
                },
                'open': {
                    'description': '打开文件或视图',
                    'required_params': ['file/url'],
                    'optional_params': ['view']
                },
                'config': {
                    'description': '打开配置界面',
                    'required_params': [],
                    'optional_params': ['view', 'api_service', 'api_key']
                }
            }
        }