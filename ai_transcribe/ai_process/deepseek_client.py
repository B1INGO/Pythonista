"""
DeepSeek API客户端

对转录文本进行智能整理
"""

from typing import Tuple, Optional, Dict, Any, List
from ..config import config
from ..utils.logger import get_logger
from ..utils.api_utils import APIUtils

logger = get_logger(__name__)

class DeepSeekClient:
    """DeepSeek API客户端"""
    
    def __init__(self):
        self.api_key = config.get_api_key('deepseek')
        self.base_url = config.get('ai_process.api_base_url', 'https://api.deepseek.com/v1')
        self.model = config.get('ai_process.model', 'deepseek-chat')
        self.max_tokens = config.get('ai_process.max_tokens', 4000)
        self.temperature = config.get('ai_process.temperature', 0.7)
        
        if not self.api_key:
            logger.warning("DeepSeek API密钥未设置")
    
    def process_text(
        self, 
        text: str, 
        prompt: str, 
        system_prompt: Optional[str] = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        使用AI处理文本
        
        Args:
            text: 要处理的文本
            prompt: 处理提示词
            system_prompt: 系统提示词
            
        Returns:
            (success, processed_text, error_message)
        """
        try:
            if not self.api_key:
                return False, None, "API密钥未设置，请在设置中配置DeepSeek API密钥"
            
            if not text or not text.strip():
                return False, None, "输入文本为空"
            
            if not prompt or not prompt.strip():
                return False, None, "处理提示词为空"
            
            logger.info(f"开始AI文本处理，文本长度: {len(text)} 字符")
            
            # 检查文本长度，如果太长则分块处理
            if APIUtils.estimate_tokens(text) > self.max_tokens // 2:
                logger.info("文本较长，使用分块处理")
                return self._process_text_chunks(text, prompt, system_prompt)
            else:
                return self._process_single_text(text, prompt, system_prompt)
        
        except Exception as e:
            logger.exception(f"AI文本处理异常")
            return False, None, f"处理文本时发生错误: {str(e)}"
    
    def _process_single_text(
        self, 
        text: str, 
        prompt: str, 
        system_prompt: Optional[str] = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """处理单个文本块"""
        try:
            # 准备消息
            messages = []
            
            if system_prompt:
                messages.append({
                    'role': 'system',
                    'content': system_prompt
                })
            
            # 构建用户消息
            user_content = f"{prompt}\n\n原文本：\n{text}"
            messages.append({
                'role': 'user',
                'content': user_content
            })
            
            # 准备请求数据
            request_data = {
                'model': self.model,
                'messages': messages,
                'max_tokens': self.max_tokens,
                'temperature': self.temperature,
                'stream': False
            }
            
            # 发送请求
            url = f"{self.base_url}/chat/completions"
            headers = APIUtils.prepare_auth_headers(self.api_key, 'deepseek')
            
            success, response_data, error_msg = APIUtils.make_request(
                method='POST',
                url=url,
                headers=headers,
                data=request_data,
                timeout=60  # AI处理可能需要更长时间
            )
            
            if success and response_data:
                # 提取处理结果
                processed_text = self._extract_response_text(response_data)
                if processed_text:
                    logger.info(f"AI文本处理成功，结果长度: {len(processed_text)} 字符")
                    return True, processed_text, None
                else:
                    logger.error(f"无法从响应中提取处理结果: {response_data}")
                    return False, None, "API响应格式异常"
            else:
                logger.error(f"DeepSeek API调用失败: {error_msg}")
                return False, None, error_msg or "API调用失败"
        
        except Exception as e:
            logger.exception("单个文本处理异常")
            return False, None, f"处理文本错误: {str(e)}"
    
    def _process_text_chunks(
        self, 
        text: str, 
        prompt: str, 
        system_prompt: Optional[str] = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """分块处理长文本"""
        try:
            # 将文本分块
            chunks = APIUtils.chunk_text(text, max_length=2000, overlap=200)
            logger.info(f"文本分为 {len(chunks)} 块处理")
            
            processed_chunks = []
            failed_chunks = 0
            
            for i, chunk in enumerate(chunks):
                logger.info(f"处理文本块 {i+1}/{len(chunks)}")
                
                # 为分块调整提示词
                chunk_prompt = f"{prompt}\n\n注意：这是文本的第 {i+1} 部分，共 {len(chunks)} 部分。请保持与其他部分的一致性。"
                
                success, processed_chunk, error = self._process_single_text(
                    chunk, chunk_prompt, system_prompt
                )
                
                if success and processed_chunk:
                    processed_chunks.append(processed_chunk)
                else:
                    failed_chunks += 1
                    logger.warning(f"文本块 {i+1} 处理失败: {error}")
                    # 如果处理失败，使用原文本
                    processed_chunks.append(f"[处理失败，原文本] {chunk}")
            
            if not processed_chunks:
                return False, None, "所有文本块处理都失败了"
            
            # 合并结果
            merged_text = '\n\n'.join(processed_chunks)
            
            if failed_chunks > 0:
                warning_msg = f"注意：有 {failed_chunks} 个文本块处理失败"
                logger.warning(warning_msg)
                return True, merged_text, warning_msg
            else:
                logger.info("所有文本块处理成功")
                return True, merged_text, None
        
        except Exception as e:
            logger.exception("分块文本处理异常")
            return False, None, f"分块处理错误: {str(e)}"
    
    def _extract_response_text(self, response_data: Dict[str, Any]) -> Optional[str]:
        """从API响应中提取处理结果"""
        try:
            # DeepSeek API响应格式
            if 'choices' in response_data and len(response_data['choices']) > 0:
                choice = response_data['choices'][0]
                if 'message' in choice and 'content' in choice['message']:
                    return choice['message']['content'].strip()
            
            # 备用格式检查
            if 'text' in response_data:
                return response_data['text'].strip()
            
            logger.error(f"未知的API响应格式: {response_data}")
            return None
        
        except Exception as e:
            logger.error(f"提取响应文本失败: {e}")
            return None
    
    def validate_api_key(self) -> Tuple[bool, Optional[str]]:
        """验证API密钥是否有效"""
        try:
            if not self.api_key:
                return False, "API密钥未设置"
            
            # 基本格式验证
            if not APIUtils.validate_api_key(self.api_key, 'deepseek'):
                return False, "API密钥格式无效"
            
            # 尝试调用API验证
            url = f"{self.base_url}/models"
            headers = APIUtils.prepare_auth_headers(self.api_key, 'deepseek')
            
            success, response_data, error_msg = APIUtils.make_request(
                method='GET',
                url=url,
                headers=headers,
                timeout=10
            )
            
            if success:
                logger.info("DeepSeek API密钥验证成功")
                return True, "API密钥有效"
            else:
                logger.warning(f"DeepSeek API密钥验证失败: {error_msg}")
                return False, error_msg or "API密钥验证失败"
        
        except Exception as e:
            logger.error(f"API密钥验证异常: {e}")
            return False, f"验证过程发生错误: {str(e)}"
    
    def get_supported_models(self) -> Tuple[bool, Optional[List[str]], Optional[str]]:
        """获取支持的模型列表"""
        try:
            if not self.api_key:
                return False, None, "API密钥未设置"
            
            url = f"{self.base_url}/models"
            headers = APIUtils.prepare_auth_headers(self.api_key, 'deepseek')
            
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
    
    def test_processing(self, test_text: str = "这是一段测试文本。") -> Tuple[bool, Optional[str], Optional[str]]:
        """测试文本处理功能"""
        try:
            test_prompt = "请将以下文本重新整理，使其更加清晰易读："
            return self.process_text(test_text, test_prompt)
        except Exception as e:
            logger.error(f"测试文本处理异常: {e}")
            return False, None, f"测试处理错误: {str(e)}"
    
    def set_api_key(self, api_key: str) -> bool:
        """设置API密钥"""
        try:
            if not APIUtils.validate_api_key(api_key, 'deepseek'):
                logger.error("DeepSeek API密钥格式无效")
                return False
            
            # 保存到配置
            if config.set_api_key('deepseek', api_key):
                self.api_key = api_key
                logger.info("DeepSeek API密钥设置成功")
                return True
            else:
                logger.error("保存DeepSeek API密钥失败")
                return False
        
        except Exception as e:
            logger.error(f"设置API密钥异常: {e}")
            return False
    
    def update_model_config(self, model: Optional[str] = None, max_tokens: Optional[int] = None, temperature: Optional[float] = None):
        """更新模型配置"""
        try:
            if model is not None:
                self.model = model
                config.set('ai_process.model', model)
            
            if max_tokens is not None:
                self.max_tokens = max_tokens
                config.set('ai_process.max_tokens', max_tokens)
            
            if temperature is not None:
                self.temperature = temperature
                config.set('ai_process.temperature', temperature)
            
            logger.info(f"模型配置已更新: model={self.model}, max_tokens={self.max_tokens}, temperature={self.temperature}")
        
        except Exception as e:
            logger.error(f"更新模型配置失败: {e}")
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """获取使用统计信息（如果API支持）"""
        try:
            # DeepSeek API可能不提供使用统计，这里返回基本信息
            stats = {
                'model': self.model,
                'max_tokens': self.max_tokens,
                'temperature': self.temperature,
                'api_configured': bool(self.api_key)
            }
            
            return stats
        except Exception as e:
            logger.error(f"获取使用统计失败: {e}")
            return {}