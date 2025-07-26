# AI音视频转文字处理工具

为iPadOS 18.5创建的完整AI音视频处理工具，支持通过iOS分享扩展和"打开方式"处理音频/视频文件，使用硅基流动API进行语音转文字，然后通过DeepSeek等大模型对文字内容进行智能整理。

## 功能特性

### ✨ 核心功能
- 🎤 **高精度语音转文字** - 基于硅基流动API，支持多种音频格式
- 🤖 **AI智能文本整理** - 使用DeepSeek等大模型进行文本处理
- 📱 **iOS原生集成** - 完美支持iPadOS分享扩展和文件关联
- 🎯 **多种处理模板** - 会议纪要、学习笔记、内容摘要等预设模板
- 📁 **批量处理** - 支持同时处理多个音视频文件

### 🎵 支持的格式
- **音频格式**: MP3, WAV, AAC, M4A, FLAC
- **视频格式**: MP4, MOV, AVI, MKV, WMV (自动提取音频)

### 🚀 AI处理模板
- **会议纪要** - 将会议录音整理成规范的会议纪要
- **学习笔记** - 将课程内容整理成结构化的学习笔记  
- **内容摘要** - 提取核心内容生成简洁摘要
- **访谈整理** - 将访谈录音整理成规范的访谈稿
- **讲座整理** - 将讲座录音转换成完整的讲座稿
- **客服记录** - 整理客服通话生成服务记录
- **自定义模板** - 支持用户自定义处理逻辑

## 安装使用

### 环境要求
- iOS/iPadOS 12.0+ 
- Pythonista 3 应用
- 有效的硅基流动API密钥
- 有效的DeepSeek API密钥

### 安装步骤

1. **下载代码**
   ```bash
   # 在Pythonista中克隆项目
   git clone https://github.com/B1INGO/Pythonista.git
   cd Pythonista/ai_transcribe
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置API密钥**
   - 启动应用后点击设置按钮⚙️
   - 分别配置硅基流动API和DeepSeek API密钥
   - 可在设置中测试API连接状态

4. **运行应用**
   ```python
   # 在Pythonista中运行
   python main.py
   ```

### 使用方法

#### 1. 基础使用流程
1. **添加文件** - 点击"添加文件"或通过分享扩展添加音视频文件
2. **选择模板** - 选择合适的AI处理模板
3. **开始处理** - 可选择"转录"、"AI整理"或"一键处理"
4. **查看结果** - 在结果界面查看、编辑、分享处理结果

#### 2. iOS集成功能

**分享扩展**
```
其他应用 → 分享按钮 → AI音视频转文字工具
```

**文件关联**
```
文件管理器 → 长按音视频文件 → 打开方式 → AI音视频转文字工具
```

**URL Scheme调用**
```javascript
// 转录文件
ai-transcribe://transcribe?file=/path/to/audio.mp3&language=zh

// AI处理文本  
ai-transcribe://process?text=文本内容&template=meeting_notes

// 打开设置
ai-transcribe://config?view=api
```

#### 3. API配置

**硅基流动API**
- 用途: 语音转文字
- 获取地址: https://siliconflow.cn
- 格式: sk-xxxxxxxxxxxx

**DeepSeek API** 
- 用途: AI文本处理
- 获取地址: https://platform.deepseek.com
- 格式: sk-xxxxxxxxxxxx

## 项目结构

```
ai_transcribe/
├── __init__.py                 # 包初始化
├── main.py                     # 主入口程序
├── config.py                   # 配置管理
├── requirements.txt            # 依赖列表
├── README.md                   # 使用说明
│
├── core/                       # 核心处理模块
│   ├── __init__.py
│   ├── media_processor.py      # 媒体文件处理
│   ├── audio_extractor.py      # 音频提取
│   └── format_converter.py     # 格式转换
│
├── transcribe/                 # 转录模块
│   ├── __init__.py
│   ├── siliconflow_client.py   # 硅基流动API客户端
│   ├── transcriber.py          # 转录核心逻辑
│   └── segment_processor.py    # 分段处理
│
├── ai_process/                 # AI处理模块
│   ├── __init__.py
│   ├── deepseek_client.py      # DeepSeek API客户端
│   ├── text_processor.py       # 文本处理核心
│   ├── prompt_templates.py     # 提示词模板
│   └── custom_prompts.py       # 自定义提示词管理
│
├── ios_integration/            # iOS集成
│   ├── __init__.py
│   ├── share_extension.py      # 分享扩展处理
│   ├── file_handler.py         # 文件处理器
│   └── url_scheme.py           # URL Scheme处理
│
├── ui/                         # 用户界面
│   ├── __init__.py
│   ├── main_view.py            # 主界面
│   ├── progress_view.py        # 进度界面
│   ├── result_view.py          # 结果预览界面
│   └── settings_view.py        # 设置界面
│
└── utils/                      # 工具模块
    ├── __init__.py
    ├── logger.py               # 日志系统
    ├── cache.py                # 缓存管理
    ├── file_utils.py           # 文件工具
    └── api_utils.py            # API工具
```

## 技术特性

### 🔧 模块化架构
- 每个功能模块独立实现，便于维护和扩展
- 清晰的接口设计，支持插件式开发
- 完善的错误处理和日志记录

### ⚡ 性能优化
- 智能缓存系统，避免重复处理
- 异步处理和进度反馈
- 大文件分段处理，支持长音频

### 🔒 安全可靠
- API密钥安全存储在iOS Keychain
- 本地处理，保护隐私数据
- 完善的错误恢复机制

### 🎯 用户体验
- 直观的触摸界面设计
- 实时处理状态反馈
- 灵活的结果导出选项
- 完整的帮助和设置系统

## 开发说明

### 扩展新的AI服务
```python
# 1. 创建新的客户端类
class NewAIClient:
    def process_text(self, text, prompt):
        # 实现API调用逻辑
        pass

# 2. 在text_processor中集成
from .new_ai_client import NewAIClient
```

### 添加新的处理模板
```python
# 在prompt_templates.py中添加
'new_template': {
    'name': '新模板',
    'description': '模板描述',
    'user_prompt': '处理提示词...',
    'system_prompt': '系统提示词...',
    'category': '分类',
    'tags': ['标签1', '标签2']
}
```

### 自定义URL Scheme
```python
# 在url_scheme.py中扩展
def handle_custom_action(self, params):
    # 处理自定义URL Scheme
    pass
```

## 常见问题

### Q: 转录准确率如何提升？
A: 
- 确保音频质量清晰，减少背景噪音
- 使用合适的音频格式（推荐WAV或MP3）
- 对于方言内容，可在设置中调整语言选项

### Q: 处理大文件时间较长？
A: 
- 工具会自动分段处理大文件
- 可在缓存设置中查看处理进度
- 建议在WiFi环境下处理大文件

### Q: 如何添加自定义模板？
A: 
- 进入设置 → 提示词模板
- 点击"添加自定义模板"
- 输入模板名称和处理提示词

### Q: API调用出错怎么办？
A: 
- 检查网络连接状态
- 验证API密钥是否正确
- 在设置中进行API测试
- 查看日志获取详细错误信息

## 版本历史

### v1.0.0 (2024-12)
- ✨ 首个正式版本发布
- 🎤 支持硅基流动语音转文字API
- 🤖 集成DeepSeek AI文本处理
- 📱 完整的iOS集成功能
- 🎯 内置7种处理模板
- 📁 支持批量文件处理

## 贡献指南

欢迎提交Issue和Pull Request来改进这个项目！

### 提交Issue
- 详细描述问题现象
- 提供错误日志和复现步骤
- 说明使用环境和版本信息

### 提交代码
- Fork项目并创建功能分支
- 遵循现有的代码风格
- 添加必要的测试和文档
- 提交清晰的Commit信息

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 支持与反馈

如果您在使用过程中遇到任何问题，或有改进建议，欢迎通过以下方式联系：

- 📧 邮件反馈
- 🐛 GitHub Issues  
- 💬 应用内反馈

感谢您使用AI音视频转文字处理工具！