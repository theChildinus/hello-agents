# Personal Information Signaling System - 个人信息信号系统

一个基于LLM的个人信息记录与分析系统，通过分析用户的日报/周报/月报，自动提取兴趣维度，智能匹配与搜索推荐，实现个性化的内容推荐和兴趣追踪。

## ✨ 核心功能

### 1. 智能YouTube视频搜索
- 基于用户定义的主题（themes）搜索相关视频
- 支持多主题并行搜索
- 自动评分和排序（基于频道白名单、关键词匹配等）
- 生成结构化日报和研究报告

### 2. 维度提取与分析
- **自动维度提取**：使用LLM从用户的自然语言报告（日报/周报/月报）中提取兴趣维度
- **主题智能修正**：分析提取的维度与现有搜索主题的匹配度，自动建议添加/删除主题
- **批量交互确认**：支持批量选择要添加/删除的主题，提升用户体验

### 3. 桌面提醒系统
- 每天定时弹出桌面提醒（可配置时间）
- 点击提醒窗口直接启动日报编写
- 支持自定义提醒图片和窗口样式

## 📁 项目结构

```
Personal_Information_Signaling_System/
├── README.md                      # 项目说明文档
├── requirements.txt               # Python依赖包
├── env.example                    # 环境变量配置模板
├── .gitignore                     # Git忽略文件配置
│
├── search_youtube_mcp_videos.py   # YouTube视频搜索主脚本
├── write_report.py                # 报告编写工具
├── extract_dimensions.py          # 维度提取模块
├── dimension_analysis.py          # 维度分析模块
├── analyze_dimensions.py          # 维度分析主脚本
├── manage_themes.py               # 主题管理工具
├── daily_reminder.py              # 桌面提醒脚本
│
├── themes.yaml                    # 搜索主题配置（用户自定义）
├── channels.yaml                  # 频道白名单配置
│
├── assets/                        # 资源文件目录
│   └── person.png                 # 提醒窗口图片
│
└── archive/                       # 数据归档目录（自动生成）
    ├── reports/                   # 用户报告
    │   ├── daily/                 # 日报
    │   ├── weekly/                # 周报
    │   └── monthly/               # 月报
    ├── dimensions/                # 维度提取结果
    ├── dimension_analysis/        # 分析报告
    └── youtube/                   # YouTube搜索结果
```

## 🚀 快速开始

### 1. 环境准备

#### 安装Python依赖

```bash
pip install -r requirements.txt
```

#### 安装LLM库（可选，用于维度提取和研究报告）

```bash
# 如果使用 hello_agents
# 请参考：https://github.com/datawhalechina/hello-agents
```

### 2. 配置环境变量

复制 `env.example` 为 `.env` 并填入你的配置：

```bash
cp env.example .env
```

编辑 `.env` 文件，填入以下必需配置：

```env
# YouTube API Key（必需）
YOUTUBE_API_KEY=your_youtube_api_key_here

# LLM配置（用于维度提取，必需）
LLM_API_KEY=your_llm_api_key_here
LLM_MODEL_ID=qwen-plus
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

**如何获取API Key：**
- **YouTube API Key**: [Google Cloud Console](https://console.cloud.google.com/) → 启用 YouTube Data API v3 → 创建凭据
- **LLM API Key**: 根据你使用的LLM服务提供商获取（如阿里云DashScope、OpenAI等）

### 3. 初始化配置文件

#### 设置搜索主题（themes.yaml）

```yaml
themes:
  - mcp
  - agent
  - rag
  - money
  - AI
```

#### 设置频道白名单（channels.yaml，可选）

```yaml
channels:
  - Anthropic
  - OpenAI
  - DeepMind
```

## 📖 使用指南

### 基础流程

#### 1. 编写日报/周报/月报

```bash
python write_report.py
```

选择报告类型（daily/weekly/monthly），输入你的自然语言报告内容。

#### 2. 搜索YouTube视频

```bash
# 普通模式（仅搜索和评分）
python search_youtube_mcp_videos.py

# 研究模式（搜索 + 生成研究报告）
python search_youtube_mcp_videos.py --research
```

#### 3. 提取维度并分析主题

```bash
# 提取维度（从报告中）
python analyze_dimensions.py --extract

# 提取维度 + 分析主题 + 交互式确认
python analyze_dimensions.py --extract --interactive
```

系统会：
- 从你的报告中提取维度
- 分析维度与现有主题的匹配度
- 建议添加/删除主题
- 支持批量选择确认

### 桌面提醒设置（Windows）

1. 准备提醒图片：将图片命名为 `person.png` 或 `person.jpg`，放入 `assets/` 目录
2. 设置Windows任务计划程序：
   - 打开"任务计划程序"
   - 创建基本任务
   - 触发器：每天 23:30（或你希望的时间）
   - 操作：启动程序
     - 程序：`python.exe` 的完整路径
     - 参数：`daily_reminder.py`
     - 起始于：项目目录路径

详细设置说明请参考：`桌面提醒设置说明.md`

## 🔧 高级功能

### 主题管理

```bash
# 查看当前主题
python manage_themes.py --list

# 添加主题
python manage_themes.py --add "新主题"

# 删除主题
python manage_themes.py --remove "旧主题"
```

### 维度分析配置

系统会自动生成以下配置文件（首次运行后）：
- `dimension_config.json`: 维度配置（活跃/候选/已删除）
- `dimension_history.json`: 维度历史记录

## 📝 详细文档

- **完整使用流程**: `完整使用流程说明.md`
- **维度分析系统**: `维度分析系统使用说明.md`
- **桌面提醒设置**: `桌面提醒设置说明.md`

## 🛠️ 技术栈

- **Python 3.8+**
- **LLM**: hello_agents / DashScope / OpenAI（可配置）
- **YouTube API**: YouTube Data API v3
- **GUI**: tkinter（桌面提醒）
- **数据处理**: PyYAML, JSON

## 📄 许可证

本项目为开源项目，遵循相应的开源许可证。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题或建议，请通过 GitHub Issues 联系。

---

**注意**：
- 首次使用前，请确保已配置 `.env` 文件中的 API Key
- `archive/` 目录包含用户个人数据，已配置在 `.gitignore` 中，不会被提交到仓库
- 配置文件请参考 `themes.yaml.example` 和 `channels.yaml.example`，复制为 `themes.yaml` 和 `channels.yaml` 后修改为你自己的配置

