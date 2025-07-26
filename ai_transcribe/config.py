"""
配置管理模块

管理API密钥、应用设置和用户配置
"""

import json
import os
import keychain
from typing import Dict, Any, Optional

class Config:
    """配置管理类"""
    
    def __init__(self):
        self.config_file = os.path.join(os.path.dirname(__file__), 'config.json')
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        default_config = {
            'app_name': 'AI音视频转文字工具',
            'version': '1.0.0',
            'supported_formats': {
                'audio': ['.mp3', '.wav', '.aac', '.m4a', '.flac'],
                'video': ['.mp4', '.mov', '.avi', '.mkv', '.wmv']
            },
            'transcribe': {
                'max_file_size_mb': 100,
                'chunk_duration_seconds': 60,
                'api_timeout_seconds': 30,
                'api_base_url': 'https://api.siliconflow.cn/v1'
            },
            'ai_process': {
                'api_base_url': 'https://api.deepseek.com/v1',
                'model': 'deepseek-chat',
                'max_tokens': 4000,
                'temperature': 0.7
            },
            'ui': {
                'theme': 'light',
                'font_size': 16,
                'progress_update_interval': 0.5
            },
            'cache': {
                'enabled': True,
                'max_size_mb': 500,
                'ttl_hours': 24
            },
            'prompts': {
                'builtin': self._get_default_prompts(),
                'custom': {}
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                # 合并默认配置和用户配置
                default_config.update(user_config)
            except Exception as e:
                print(f"警告：无法加载配置文件: {e}")
        
        return default_config
    
    def save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"警告：无法保存配置文件: {e}")
    
    def get(self, key: str, default=None):
        """获取配置值"""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        keys = key.split('.')
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save_config()
    
    def get_api_key(self, service: str) -> Optional[str]:
        """从keychain获取API密钥"""
        try:
            return keychain.get_password(f'ai_transcribe_{service}', 'api_key')
        except Exception as e:
            print(f"警告：无法获取{service}的API密钥: {e}")
            return None
    
    def set_api_key(self, service: str, api_key: str) -> bool:
        """设置API密钥到keychain"""
        try:
            keychain.set_password(f'ai_transcribe_{service}', 'api_key', api_key)
            return True
        except Exception as e:
            print(f"错误：无法设置{service}的API密钥: {e}")
            return False
    
    def delete_api_key(self, service: str) -> bool:
        """删除API密钥"""
        try:
            keychain.delete_password(f'ai_transcribe_{service}', 'api_key')
            return True
        except Exception as e:
            print(f"警告：无法删除{service}的API密钥: {e}")
            return False
    
    def _get_default_prompts(self):
        """获取所有内置提示词模板"""
        return {
            'meeting_notes': {
                'name': '会议纪要',
                'description': '将会议录音转录的文本整理成规范的会议纪要',
                'system_prompt': '你是一个专业的会议记录员，擅长将会议录音转录的文本整理成清晰、结构化的会议纪要。',
                'user_prompt': '''请将以下会议录音转录的文本整理成规范的会议纪要，要求：

1. **会议基本信息**（如果文本中有提及）
   - 会议时间、地点、参会人员
   - 会议主题和目的

2. **会议内容整理**
   - 按讨论主题分类整理
   - 突出重要决策和结论
   - 记录具体的行动计划

3. **任务分配**
   - 明确责任人和截止时间
   - 列出待办事项

4. **格式要求**
   - 使用标准的会议纪要格式
   - 语言简洁明了，去除口语化表达
   - 重点内容用粗体标注

请确保内容准确、完整、条理清晰。''',
                'category': '商务办公',
                'tags': ['会议', '纪要', '商务']
            },
            
            'study_notes': {
                'name': '学习笔记',
                'description': '将课程录音或学习材料整理成结构化的学习笔记',
                'system_prompt': '你是一个优秀的学习助手，能够将课程内容整理成清晰易懂的学习笔记。',
                'user_prompt': '''请将以下学习内容整理成结构化的学习笔记，要求：

1. **内容梳理**
   - 提取核心概念和要点
   - 建立知识框架和逻辑关系
   - 突出重难点内容

2. **格式优化**
   - 使用清晰的标题层级
   - 适当使用列表和编号
   - 重要概念用粗体标注

3. **补充完善**
   - 添加适当的总结和小结
   - 提供记忆要点
   - 如有可能，提出相关思考问题

4. **语言优化**
   - 去除重复和冗余内容
   - 使用准确的学术表达
   - 确保逻辑清晰

请确保笔记内容准确、全面、便于复习。''',
                'category': '教育学习',
                'tags': ['学习', '笔记', '教育']
            },
            
            'content_summary': {
                'name': '内容摘要',
                'description': '提取文本的核心内容，生成简洁的摘要',
                'system_prompt': '你是一个专业的内容编辑，擅长提取文本的核心信息并生成简洁明了的摘要。',
                'user_prompt': '''请为以下内容生成摘要，要求：

1. **摘要内容**
   - 提取核心观点和主要信息
   - 保留重要细节和数据
   - 去除冗余和次要信息

2. **结构安排**
   - 按重要性排序
   - 使用简洁的段落结构
   - 突出关键信息

3. **长度控制**
   - 摘要长度控制在原文的20-30%
   - 确保信息完整性
   - 语言简洁明了

4. **质量要求**
   - 保持原文的准确性
   - 逻辑清晰连贯
   - 可读性强

请生成一个高质量的内容摘要。''',
                'category': '内容处理',
                'tags': ['摘要', '提取', '总结']
            },
            
            'interview_transcript': {
                'name': '访谈整理',
                'description': '将访谈录音整理成规范的访谈稿',
                'system_prompt': '你是一个专业的访谈编辑，能够将访谈录音整理成结构清晰的访谈稿。',
                'user_prompt': '''请将以下访谈录音转录文本整理成规范的访谈稿，要求：

1. **对话整理**
   - 区分访谈者和受访者的发言
   - 保持对话的自然流畅
   - 适当标注语气和情感

2. **内容优化**
   - 去除口语化的填充词（如"那个"、"然后"等）
   - 修正语法错误，但保持原意
   - 整理断句和语序

3. **结构规范**
   - 添加合适的段落分割
   - 突出重要观点
   - 保持访谈的逻辑顺序

4. **格式标准**
   - 使用标准的访谈稿格式
   - 清晰标识说话人
   - 适当添加场景描述

请确保访谈稿准确反映原始对话内容。''',
                'category': '媒体制作',
                'tags': ['访谈', '对话', '媒体']
            },
            
            'lecture_notes': {
                'name': '讲座整理',
                'description': '将讲座录音整理成完整的讲座稿',
                'system_prompt': '你是一个专业的讲座整理员，能够将讲座录音转录成结构完整的讲座稿。',
                'user_prompt': '''请将以下讲座录音转录文本整理成完整的讲座稿，要求：

1. **内容结构**
   - 提取讲座的主题和核心观点
   - 建立清晰的逻辑框架
   - 突出重点和亮点

2. **语言优化**
   - 将口语表达转换为书面语
   - 完善句子结构和语法
   - 保持讲者的表达风格

3. **格式规范**
   - 使用标准的讲座稿格式
   - 合理设置标题和段落
   - 标注重要观点和金句

4. **补充完善**
   - 适当添加过渡句
   - 补充逻辑连接
   - 确保内容完整

请生成一个高质量的讲座稿。''',
                'category': '教育学习',
                'tags': ['讲座', '演讲', '教育']
            },
            
            'customer_service': {
                'name': '客服记录',
                'description': '整理客服通话录音，生成客服记录',
                'system_prompt': '你是一个专业的客服记录整理员，能够将客服通话内容整理成规范的服务记录。',
                'user_prompt': '''请将以下客服通话录音转录文本整理成客服记录，要求：

1. **基本信息**
   - 客户基本情况
   - 咨询或投诉的主要内容
   - 服务人员的回应

2. **问题分析**
   - 客户的具体需求或问题
   - 问题的性质和紧急程度
   - 相关背景信息

3. **处理过程**
   - 服务人员的处理方案
   - 客户的反馈和态度
   - 最终解决方案

4. **记录规范**
   - 使用客观、专业的语言
   - 重点记录关键信息
   - 便于后续跟进

请生成规范的客服记录。''',
                'category': '商务服务',
                'tags': ['客服', '记录', '服务']
            },
            
            'custom_cleanup': {
                'name': '文本清理',
                'description': '基本的文本清理和格式优化',
                'system_prompt': '你是一个专业的文本编辑器，能够清理和优化各种文本内容。',
                'user_prompt': '''请对以下文本进行清理和优化，要求：

1. **基础清理**
   - 去除重复内容和冗余表达
   - 修正明显的语法错误
   - 统一标点符号的使用

2. **格式优化**
   - 合理分段，提高可读性
   - 统一格式风格
   - 适当使用标题和列表

3. **语言润色**
   - 优化句子结构
   - 提高表达的准确性
   - 保持原意不变

4. **质量提升**
   - 确保逻辑清晰
   - 语言流畅自然
   - 信息完整准确

请生成清理优化后的文本。''',
                'category': '文本处理',
                'tags': ['清理', '优化', '格式']
            }
        }
    
    # 提示词管理方法
    def get_prompt(self, prompt_id: str):
        """获取提示词（内置或自定义）"""
        # 先检查内置提示词
        builtin_prompts = self.get('prompts.builtin', {})
        if prompt_id in builtin_prompts:
            return builtin_prompts[prompt_id]
        
        # 检查自定义提示词
        custom_prompts = self.get('prompts.custom', {})
        return custom_prompts.get(prompt_id)
    
    def get_all_prompts(self):
        """获取所有提示词"""
        builtin_prompts = self.get('prompts.builtin', {})
        custom_prompts = self.get('prompts.custom', {})
        
        # 合并，自定义提示词优先
        all_prompts = builtin_prompts.copy()
        all_prompts.update(custom_prompts)
        return all_prompts
    
    def get_prompt_categories(self):
        """获取所有提示词分类"""
        categories = set()
        all_prompts = self.get_all_prompts()
        for prompt in all_prompts.values():
            if 'category' in prompt:
                categories.add(prompt['category'])
        return sorted(list(categories))
    
    def get_prompts_by_category(self, category: str):
        """按分类获取提示词"""
        all_prompts = self.get_all_prompts()
        return {
            pid: prompt for pid, prompt in all_prompts.items()
            if prompt.get('category') == category
        }
    
    def search_prompts(self, keyword: str):
        """搜索提示词"""
        keyword = keyword.lower()
        results = {}
        all_prompts = self.get_all_prompts()
        
        for pid, prompt in all_prompts.items():
            if (keyword in prompt.get('name', '').lower() or
                keyword in prompt.get('description', '').lower() or
                any(keyword in tag.lower() for tag in prompt.get('tags', []))):
                results[pid] = prompt
        
        return results
    
    def add_custom_prompt(self, prompt_id: str, prompt_data: dict):
        """添加自定义提示词"""
        custom_prompts = self.get('prompts.custom', {})
        custom_prompts[prompt_id] = prompt_data
        self.set('prompts.custom', custom_prompts)
        return True
    
    def update_custom_prompt(self, prompt_id: str, prompt_data: dict):
        """更新自定义提示词"""
        custom_prompts = self.get('prompts.custom', {})
        if prompt_id in custom_prompts:
            custom_prompts[prompt_id].update(prompt_data)
            self.set('prompts.custom', custom_prompts)
            return True
        return False
    
    def delete_custom_prompt(self, prompt_id: str):
        """删除自定义提示词"""
        custom_prompts = self.get('prompts.custom', {})
        if prompt_id in custom_prompts:
            del custom_prompts[prompt_id]
            self.set('prompts.custom', custom_prompts)
            return True
        return False

# 全局配置实例
config = Config()