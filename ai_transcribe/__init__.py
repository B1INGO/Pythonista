"""
AI音视频转文字处理工具

为iPadOS 18.5创建的完整AI音视频处理工具，支持通过iOS分享扩展和"打开方式"处理音频/视频文件，
使用硅基流动API进行语音转文字，然后通过DeepSeek等大模型对文字内容进行智能整理。

Author: AI Transcribe Team
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "AI Transcribe Team"

# 导入主要模块
from .main import main, AITranscribeApp

__all__ = ['main', 'AITranscribeApp']