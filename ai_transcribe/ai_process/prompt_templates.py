"""
提示词模板模块

预设多种处理场景的提示词模板
"""

from typing import Dict, List, Any
from ..utils.logger import get_logger

logger = get_logger(__name__)

class PromptTemplates:
    """提示词模板管理类"""
    
    def __init__(self):
        self._templates = self._load_default_templates()
    
    def _load_default_templates(self) -> Dict[str, Dict[str, Any]]:
        """加载默认模板"""
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
    
    def get_template(self, template_id: str) -> Dict[str, Any]:
        """获取指定模板"""
        return self._templates.get(template_id, {})
    
    def get_all_templates(self) -> Dict[str, Dict[str, Any]]:
        """获取所有模板"""
        return self._templates.copy()
    
    def get_templates_by_category(self, category: str) -> Dict[str, Dict[str, Any]]:
        """按分类获取模板"""
        return {
            tid: template for tid, template in self._templates.items()
            if template.get('category') == category
        }
    
    def get_categories(self) -> List[str]:
        """获取所有分类"""
        categories = set()
        for template in self._templates.values():
            if 'category' in template:
                categories.add(template['category'])
        return sorted(list(categories))
    
    def search_templates(self, keyword: str) -> Dict[str, Dict[str, Any]]:
        """搜索模板"""
        keyword = keyword.lower()
        results = {}
        
        for tid, template in self._templates.items():
            # 在名称、描述和标签中搜索
            if (keyword in template.get('name', '').lower() or
                keyword in template.get('description', '').lower() or
                any(keyword in tag.lower() for tag in template.get('tags', []))):
                results[tid] = template
        
        return results
    
    def add_template(self, template_id: str, template_data: Dict[str, Any]) -> bool:
        """添加自定义模板"""
        try:
            # 验证必需字段
            required_fields = ['name', 'user_prompt']
            for field in required_fields:
                if field not in template_data:
                    logger.error(f"模板缺少必需字段: {field}")
                    return False
            
            # 添加默认值
            template_data.setdefault('description', '')
            template_data.setdefault('system_prompt', '你是一个专业的文本处理助手。')
            template_data.setdefault('category', '自定义')
            template_data.setdefault('tags', [])
            
            self._templates[template_id] = template_data
            logger.info(f"添加自定义模板: {template_id}")
            return True
        
        except Exception as e:
            logger.error(f"添加模板失败: {e}")
            return False
    
    def update_template(self, template_id: str, template_data: Dict[str, Any]) -> bool:
        """更新模板"""
        try:
            if template_id not in self._templates:
                logger.error(f"模板不存在: {template_id}")
                return False
            
            self._templates[template_id].update(template_data)
            logger.info(f"更新模板: {template_id}")
            return True
        
        except Exception as e:
            logger.error(f"更新模板失败: {e}")
            return False
    
    def delete_template(self, template_id: str) -> bool:
        """删除模板"""
        try:
            if template_id not in self._templates:
                logger.warning(f"要删除的模板不存在: {template_id}")
                return False
            
            del self._templates[template_id]
            logger.info(f"删除模板: {template_id}")
            return True
        
        except Exception as e:
            logger.error(f"删除模板失败: {e}")
            return False
    
    def export_templates(self) -> Dict[str, Dict[str, Any]]:
        """导出所有模板"""
        return self._templates.copy()
    
    def import_templates(self, templates: Dict[str, Dict[str, Any]], overwrite: bool = False) -> int:
        """导入模板"""
        try:
            imported_count = 0
            
            for template_id, template_data in templates.items():
                # 检查是否已存在
                if template_id in self._templates and not overwrite:
                    logger.warning(f"模板已存在，跳过: {template_id}")
                    continue
                
                # 验证模板数据
                if 'name' not in template_data or 'user_prompt' not in template_data:
                    logger.warning(f"模板数据无效，跳过: {template_id}")
                    continue
                
                self._templates[template_id] = template_data
                imported_count += 1
                logger.debug(f"导入模板: {template_id}")
            
            logger.info(f"成功导入 {imported_count} 个模板")
            return imported_count
        
        except Exception as e:
            logger.error(f"导入模板失败: {e}")
            return 0
    
    def get_template_info(self, template_id: str) -> Dict[str, Any]:
        """获取模板详细信息"""
        template = self.get_template(template_id)
        if not template:
            return {}
        
        return {
            'id': template_id,
            'name': template.get('name', ''),
            'description': template.get('description', ''),
            'category': template.get('category', ''),
            'tags': template.get('tags', []),
            'has_system_prompt': bool(template.get('system_prompt')),
            'prompt_length': len(template.get('user_prompt', ''))
        }

# 全局模板实例
templates = PromptTemplates()