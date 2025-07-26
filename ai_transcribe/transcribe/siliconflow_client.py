"""
硅基流动API客户端

实现语音转文字功能
"""

import os
from typing import Tuple, Optional, Dict, Any
from ..config import config
from ..utils.logger import get_logger
from ..utils.api_utils import APIUtils

logger = get_logger(__name__)

class SiliconFlowClient:
    """硅基流动API客户端"""
    
    def __init__(self):
        self.api_key = config.get_api_key('siliconflow')
        self.base_url = config.get('transcribe.api_base_url', 'https://api.siliconflow.cn/v1')
        self.timeout = config.get('transcribe.api_timeout_seconds', 30)
        
        if not self.api_key:
            logger.warning("硅基流动API密钥未设置")
    
    def transcribe_audio(self, audio_path: str, language: str = 'zh') -> Tuple[bool, Optional[str], Optional[str]]:
        """
        转录音频文件
        
        Args:
            audio_path: 音频文件路径
            language: 语言代码，默认为中文
            
        Returns:
            (success, transcribed_text, error_message)
        """
        try:
            if not self.api_key:
                return False, None, "API密钥未设置，请在设置中配置硅基流动API密钥"
            
            if not os.path.exists(audio_path):
                return False, None, "音频文件不存在"
            
            logger.info(f"开始转录音频文件: {os.path.basename(audio_path)}")
            
            # 准备请求
            url = f"{self.base_url}/audio/transcriptions"
            headers = APIUtils.prepare_auth_headers(self.api_key, 'siliconflow')
            
            # 准备文件上传
            with open(audio_path, 'rb') as audio_file:
                files = {
                    'file': (os.path.basename(audio_path), audio_file, 'audio/wav'),
                }
                
                data = {
                    'model': 'FunAudioLLM/SenseVoiceSmall',  # 硅基流动的语音识别模型
                    'language': language,
                    'response_format': 'json'
                }
                
                # 发送请求
                success, response_data, error_msg = APIUtils.make_request(
                    method='POST',
                    url=url,
                    headers={k: v for k, v in headers.items() if k != 'Content-Type'},  # 移除Content-Type让requests自动设置
                    data=data,
                    files=files,
                    timeout=self.timeout
                )
            
            if success and response_data:
                # 提取转录文本
                text = self._extract_transcription_text(response_data)
                if text:
                    logger.info(f"音频转录成功，文本长度: {len(text)} 字符")
                    return True, text, None
                else:
                    logger.error(f"无法从响应中提取文本: {response_data}")
                    return False, None, "API响应格式异常"
            else:
                logger.error(f"硅基流动API调用失败: {error_msg}")
                return False, None, error_msg or "API调用失败"
        
        except Exception as e:
            logger.exception(f"音频转录异常: {audio_path}")
            return False, None, f"转录过程发生错误: {str(e)}"
    
    def _extract_transcription_text(self, response_data: Dict[str, Any]) -> Optional[str]:
        """从API响应中提取转录文本"""
        try:
            # 硅基流动API的响应格式
            if 'text' in response_data:
                return response_data['text'].strip()
            
            # 备用格式检查
            if 'data' in response_data and 'text' in response_data['data']:
                return response_data['data']['text'].strip()
            
            # OpenAI兼容格式
            if 'choices' in response_data and len(response_data['choices']) > 0:
                choice = response_data['choices'][0]
                if 'text' in choice:
                    return choice['text'].strip()
                elif 'message' in choice and 'content' in choice['message']:
                    return choice['message']['content'].strip()
            
            logger.error(f"未知的API响应格式: {response_data}")
            return None
        
        except Exception as e:
            logger.error(f"提取转录文本失败: {e}")
            return None
    
    def validate_api_key(self) -> Tuple[bool, Optional[str]]:
        """验证API密钥是否有效"""
        try:
            if not self.api_key:
                return False, "API密钥未设置"
            
            # 基本格式验证
            if not APIUtils.validate_api_key(self.api_key, 'siliconflow'):
                return False, "API密钥格式无效"
            
            # 尝试调用API验证
            url = f"{self.base_url}/models"
            headers = APIUtils.prepare_auth_headers(self.api_key, 'siliconflow')
            
            success, response_data, error_msg = APIUtils.make_request(
                method='GET',
                url=url,
                headers=headers,
                timeout=10
            )
            
            if success:
                logger.info("硅基流动API密钥验证成功")
                return True, "API密钥有效"
            else:
                logger.warning(f"硅基流动API密钥验证失败: {error_msg}")
                return False, error_msg or "API密钥验证失败"
        
        except Exception as e:
            logger.error(f"API密钥验证异常: {e}")
            return False, f"验证过程发生错误: {str(e)}"
    
    def get_supported_models(self) -> Tuple[bool, Optional[list], Optional[str]]:
        """获取支持的模型列表"""
        try:
            if not self.api_key:
                return False, None, "API密钥未设置"
            
            url = f"{self.base_url}/models"
            headers = APIUtils.prepare_auth_headers(self.api_key, 'siliconflow')
            
            success, response_data, error_msg = APIUtils.make_request(
                method='GET',
                url=url,
                headers=headers,
                timeout=10
            )
            
            if success and response_data:
                models = []
                if 'data' in response_data:
                    for model in response_data['data']:
                        if isinstance(model, dict) and 'id' in model:
                            models.append(model['id'])
                
                logger.info(f"获取到 {len(models)} 个可用模型")
                return True, models, None
            else:
                return False, None, error_msg or "获取模型列表失败"
        
        except Exception as e:
            logger.error(f"获取模型列表异常: {e}")
            return False, None, f"获取模型列表错误: {str(e)}"
    
    def get_transcription_status(self, task_id: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """获取转录任务状态（如果API支持异步处理）"""
        try:
            if not self.api_key:
                return False, None, "API密钥未设置"
            
            url = f"{self.base_url}/audio/transcriptions/{task_id}"
            headers = APIUtils.prepare_auth_headers(self.api_key, 'siliconflow')
            
            success, response_data, error_msg = APIUtils.make_request(
                method='GET',
                url=url,
                headers=headers,
                timeout=10
            )
            
            if success:
                return True, response_data, None
            else:
                return False, None, error_msg or "获取任务状态失败"
        
        except Exception as e:
            logger.error(f"获取转录状态异常: {e}")
            return False, None, f"获取状态错误: {str(e)}"
    
    def set_api_key(self, api_key: str) -> bool:
        """设置API密钥"""
        try:
            if not APIUtils.validate_api_key(api_key, 'siliconflow'):
                logger.error("硅基流动API密钥格式无效")
                return False
            
            # 保存到配置
            if config.set_api_key('siliconflow', api_key):
                self.api_key = api_key
                logger.info("硅基流动API密钥设置成功")
                return True
            else:
                logger.error("保存硅基流动API密钥失败")
                return False
        
        except Exception as e:
            logger.error(f"设置API密钥异常: {e}")
            return False