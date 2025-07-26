"""
自定义提示词管理模块

支持用户自定义处理逻辑
"""

import json
import os
from typing import Dict, List, Any, Optional
from ..config import config
from ..utils.logger import get_logger
from ..utils.file_utils import FileUtils

logger = get_logger(__name__)

class CustomPrompts:
    """自定义提示词管理类"""
    
    def __init__(self):
        self.prompts_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'custom_prompts.json')
        self._prompts = self._load_prompts()
    
    def _load_prompts(self) -> Dict[str, Dict[str, Any]]:
        """加载自定义提示词"""
        try:
            if os.path.exists(self.prompts_file):
                with open(self.prompts_file, 'r', encoding='utf-8') as f:
                    prompts = json.load(f)
                logger.info(f"加载了 {len(prompts)} 个自定义提示词")
                return prompts
            else:
                logger.info("自定义提示词文件不存在，创建空集合")
                return {}
        except Exception as e:
            logger.error(f"加载自定义提示词失败: {e}")
            return {}
    
    def _save_prompts(self) -> bool:
        """保存自定义提示词到文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.prompts_file), exist_ok=True)
            
            with open(self.prompts_file, 'w', encoding='utf-8') as f:
                json.dump(self._prompts, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"自定义提示词已保存: {len(self._prompts)} 个")
            return True
        except Exception as e:
            logger.error(f"保存自定义提示词失败: {e}")
            return False
    
    def create_prompt(
        self, 
        prompt_id: str, 
        name: str, 
        user_prompt: str,
        system_prompt: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """
        创建自定义提示词
        
        Args:
            prompt_id: 提示词ID
            name: 提示词名称
            user_prompt: 用户提示词内容
            system_prompt: 系统提示词（可选）
            description: 描述（可选）
            tags: 标签列表（可选）
            
        Returns:
            bool: 创建是否成功
        """
        try:
            if not prompt_id or not name or not user_prompt:
                logger.error("创建提示词缺少必需参数")
                return False
            
            if prompt_id in self._prompts:
                logger.error(f"提示词ID已存在: {prompt_id}")
                return False
            
            prompt_data = {
                'name': name,
                'user_prompt': user_prompt,
                'system_prompt': system_prompt or '你是一个专业的文本处理助手。',
                'description': description or '',
                'tags': tags or [],
                'created_at': self._get_current_time(),
                'updated_at': self._get_current_time(),
                'usage_count': 0
            }
            
            self._prompts[prompt_id] = prompt_data
            
            if self._save_prompts():
                logger.info(f"创建自定义提示词成功: {prompt_id}")
                return True
            else:
                # 保存失败，回滚
                del self._prompts[prompt_id]
                return False
        
        except Exception as e:
            logger.exception(f"创建自定义提示词异常: {prompt_id}")
            return False
    
    def update_prompt(
        self, 
        prompt_id: str, 
        name: Optional[str] = None,
        user_prompt: Optional[str] = None,
        system_prompt: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """更新自定义提示词"""
        try:
            if prompt_id not in self._prompts:
                logger.error(f"要更新的提示词不存在: {prompt_id}")
                return False
            
            prompt_data = self._prompts[prompt_id]
            
            # 更新字段
            if name is not None:
                prompt_data['name'] = name
            if user_prompt is not None:
                prompt_data['user_prompt'] = user_prompt
            if system_prompt is not None:
                prompt_data['system_prompt'] = system_prompt
            if description is not None:
                prompt_data['description'] = description
            if tags is not None:
                prompt_data['tags'] = tags
            
            prompt_data['updated_at'] = self._get_current_time()
            
            if self._save_prompts():
                logger.info(f"更新自定义提示词成功: {prompt_id}")
                return True
            else:
                return False
        
        except Exception as e:
            logger.exception(f"更新自定义提示词异常: {prompt_id}")
            return False
    
    def delete_prompt(self, prompt_id: str) -> bool:
        """删除自定义提示词"""
        try:
            if prompt_id not in self._prompts:
                logger.warning(f"要删除的提示词不存在: {prompt_id}")
                return False
            
            del self._prompts[prompt_id]
            
            if self._save_prompts():
                logger.info(f"删除自定义提示词成功: {prompt_id}")
                return True
            else:
                return False
        
        except Exception as e:
            logger.exception(f"删除自定义提示词异常: {prompt_id}")
            return False
    
    def get_prompt(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """获取指定的自定义提示词"""
        return self._prompts.get(prompt_id)
    
    def get_all_prompts(self) -> Dict[str, Dict[str, Any]]:
        """获取所有自定义提示词"""
        return self._prompts.copy()
    
    def search_prompts(self, keyword: str) -> Dict[str, Dict[str, Any]]:
        """搜索自定义提示词"""
        keyword = keyword.lower()
        results = {}
        
        for prompt_id, prompt_data in self._prompts.items():
            # 在名称、描述和标签中搜索
            if (keyword in prompt_data.get('name', '').lower() or
                keyword in prompt_data.get('description', '').lower() or
                any(keyword in tag.lower() for tag in prompt_data.get('tags', []))):
                results[prompt_id] = prompt_data
        
        return results
    
    def get_prompts_by_tag(self, tag: str) -> Dict[str, Dict[str, Any]]:
        """按标签获取提示词"""
        results = {}
        
        for prompt_id, prompt_data in self._prompts.items():
            if tag in prompt_data.get('tags', []):
                results[prompt_id] = prompt_data
        
        return results
    
    def get_popular_prompts(self, limit: int = 10) -> Dict[str, Dict[str, Any]]:
        """获取最常用的提示词"""
        # 按使用次数排序
        sorted_prompts = sorted(
            self._prompts.items(),
            key=lambda x: x[1].get('usage_count', 0),
            reverse=True
        )
        
        return dict(sorted_prompts[:limit])
    
    def increment_usage(self, prompt_id: str) -> bool:
        """增加提示词使用次数"""
        try:
            if prompt_id in self._prompts:
                self._prompts[prompt_id]['usage_count'] = self._prompts[prompt_id].get('usage_count', 0) + 1
                self._prompts[prompt_id]['last_used'] = self._get_current_time()
                return self._save_prompts()
            return False
        except Exception as e:
            logger.error(f"更新使用次数失败: {e}")
            return False
    
    def duplicate_prompt(self, source_id: str, new_id: str, new_name: str) -> bool:
        """复制提示词"""
        try:
            if source_id not in self._prompts:
                logger.error(f"源提示词不存在: {source_id}")
                return False
            
            if new_id in self._prompts:
                logger.error(f"目标提示词ID已存在: {new_id}")
                return False
            
            # 复制数据
            source_data = self._prompts[source_id].copy()
            source_data['name'] = new_name
            source_data['created_at'] = self._get_current_time()
            source_data['updated_at'] = self._get_current_time()
            source_data['usage_count'] = 0
            
            self._prompts[new_id] = source_data
            
            if self._save_prompts():
                logger.info(f"复制提示词成功: {source_id} -> {new_id}")
                return True
            else:
                del self._prompts[new_id]
                return False
        
        except Exception as e:
            logger.exception(f"复制提示词异常: {source_id}")
            return False
    
    def export_prompts(self, prompt_ids: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
        """导出提示词"""
        try:
            if prompt_ids is None:
                return self._prompts.copy()
            else:
                return {pid: self._prompts[pid] for pid in prompt_ids if pid in self._prompts}
        except Exception as e:
            logger.error(f"导出提示词失败: {e}")
            return {}
    
    def import_prompts(self, prompts: Dict[str, Dict[str, Any]], overwrite: bool = False) -> int:
        """导入提示词"""
        try:
            imported_count = 0
            
            for prompt_id, prompt_data in prompts.items():
                # 检查是否已存在
                if prompt_id in self._prompts and not overwrite:
                    logger.warning(f"提示词已存在，跳过: {prompt_id}")
                    continue
                
                # 验证必需字段
                if 'name' not in prompt_data or 'user_prompt' not in prompt_data:
                    logger.warning(f"提示词数据无效，跳过: {prompt_id}")
                    continue
                
                # 添加默认字段
                prompt_data.setdefault('system_prompt', '你是一个专业的文本处理助手。')
                prompt_data.setdefault('description', '')
                prompt_data.setdefault('tags', [])
                prompt_data.setdefault('usage_count', 0)
                prompt_data['imported_at'] = self._get_current_time()
                
                self._prompts[prompt_id] = prompt_data
                imported_count += 1
                logger.debug(f"导入提示词: {prompt_id}")
            
            if imported_count > 0 and self._save_prompts():
                logger.info(f"成功导入 {imported_count} 个提示词")
                return imported_count
            else:
                return 0
        
        except Exception as e:
            logger.error(f"导入提示词失败: {e}")
            return 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取提示词统计信息"""
        try:
            if not self._prompts:
                return {
                    'total_count': 0,
                    'total_usage': 0,
                    'most_used': None,
                    'recently_created': [],
                    'all_tags': []
                }
            
            total_usage = sum(prompt.get('usage_count', 0) for prompt in self._prompts.values())
            
            # 最常用的提示词
            most_used = max(
                self._prompts.items(),
                key=lambda x: x[1].get('usage_count', 0)
            )
            
            # 最近创建的提示词
            recently_created = sorted(
                self._prompts.items(),
                key=lambda x: x[1].get('created_at', ''),
                reverse=True
            )[:5]
            
            # 所有标签
            all_tags = set()
            for prompt in self._prompts.values():
                all_tags.update(prompt.get('tags', []))
            
            return {
                'total_count': len(self._prompts),
                'total_usage': total_usage,
                'most_used': {
                    'id': most_used[0],
                    'name': most_used[1].get('name', ''),
                    'usage_count': most_used[1].get('usage_count', 0)
                } if most_used[1].get('usage_count', 0) > 0 else None,
                'recently_created': [
                    {
                        'id': pid,
                        'name': data.get('name', ''),
                        'created_at': data.get('created_at', '')
                    } for pid, data in recently_created
                ],
                'all_tags': sorted(list(all_tags))
            }
        
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}
    
    def _get_current_time(self) -> str:
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def validate_prompt(self, prompt_data: Dict[str, Any]) -> tuple:
        """验证提示词数据"""
        try:
            errors = []
            
            # 检查必需字段
            if not prompt_data.get('name'):
                errors.append("提示词名称不能为空")
            
            if not prompt_data.get('user_prompt'):
                errors.append("用户提示词内容不能为空")
            
            # 检查长度限制
            if len(prompt_data.get('name', '')) > 100:
                errors.append("提示词名称过长（最大100字符）")
            
            if len(prompt_data.get('user_prompt', '')) > 5000:
                errors.append("用户提示词内容过长（最大5000字符）")
            
            if prompt_data.get('system_prompt') and len(prompt_data['system_prompt']) > 1000:
                errors.append("系统提示词内容过长（最大1000字符）")
            
            # 检查标签
            tags = prompt_data.get('tags', [])
            if not isinstance(tags, list):
                errors.append("标签必须是列表格式")
            elif len(tags) > 10:
                errors.append("标签数量过多（最大10个）")
            
            return len(errors) == 0, errors
        
        except Exception as e:
            logger.error(f"验证提示词数据异常: {e}")
            return False, [f"验证过程发生错误: {str(e)}"]

# 全局自定义提示词实例
custom_prompts = CustomPrompts()