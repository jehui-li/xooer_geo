# 环境变量配置说明

## 快速开始

1. **复制环境变量示例文件**
```bash
cd frontend
cp env.example .env.local
```

2. **编辑 `.env.local` 文件**
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_KEY=your-api-key-here
```

3. **重启开发服务器**
```bash
npm run dev
```

## 环境变量说明

### NEXT_PUBLIC_API_URL

**说明**：后端 API 的地址

**示例**：
- 开发环境：`http://localhost:8000`
- 生产环境：`https://api.geoagent.com`

**注意**：
- 必须以 `http://` 或 `https://` 开头
- 不要以斜杠 `/` 结尾

### NEXT_PUBLIC_API_KEY

**说明**：用于 API 认证的密钥

**示例**：`sk-1234567890abcdef`

**注意**：
- 如果后端不需要认证，可以留空
- 密钥会通过 `X-API-Key` Header 发送
- 不要在代码中硬编码 API Key

## 文件说明

- `env.example`：环境变量示例文件（可以提交到 Git）
- `.env.local`：本地环境变量文件（不会被提交到 Git）
- `.env`：默认环境变量文件（可选）

## 安全提示

⚠️ **重要**：
1. `.env.local` 文件不会被提交到 Git（已在 `.gitignore` 中）
2. 不要在代码中硬编码敏感信息
3. 生产环境应该使用服务器环境变量或密钥管理服务

## 验证配置

在浏览器控制台（开发模式下）会显示当前配置信息：

```
📋 环境配置：
  API_URL: http://localhost:8000
  API_KEY: ***abcd
  NODE_ENV: development
```

## 常见问题

### Q: 为什么环境变量不生效？

A: 检查以下几点：
1. 变量名必须以 `NEXT_PUBLIC_` 开头（Next.js 要求）
2. 文件名为 `.env.local`（不是 `.env.example`）
3. 重启了开发服务器（`npm run dev`）

### Q: 如何在生产环境配置？

A: 在生产环境（如 Vercel、Netlify）的设置页面配置环境变量，或者在服务器上设置系统环境变量。

### Q: API Key 在哪里获取？

A: 联系后端开发者或查看后端 API 文档。

