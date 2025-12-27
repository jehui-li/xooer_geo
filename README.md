# GEO Agent

自动化审计品牌在生成式引擎（LLM）中表现的智能代理系统。

## 项目简介

GEO Agent 是一个能够自动化审计品牌在生成式引擎（如 ChatGPT、Gemini、Perplexity、Grok）中表现的系统。通过模拟人类对话、语义解析和数据量化，为品牌提供 GEO Score™ 评分和优化建议。

## 技术栈

- Python 3.10+
- LangGraph (Agent 框架)
- MongoDB (数据存储)
- OpenAI API, Google Vertex AI, Perplexity API, X API

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填入实际的 API 密钥：

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 API 密钥
```

### 3. 验证配置

```bash
python -c "from config.settings import settings; print(settings.validate_api_keys())"
```

## 项目结构

```
geo_agent/
├── src/                    # 源代码目录
│   ├── connectors/        # API 连接器
│   ├── analyzers/         # 数据分析模块
│   ├── scorers/           # 评分模块
│   ├── probes/            # 探针模块
│   └── strategists/        # 策略生成模块
├── config/                 # 配置模块
├── utils/                  # 工具模块
├── tests/                  # 测试目录
├── logs/                   # 日志目录
├── requirements.txt        # 依赖列表
└── .env.example           # 环境变量示例
```

## 开发状态

当前处于第一阶段：基础设施搭建

## 许可证

待定

