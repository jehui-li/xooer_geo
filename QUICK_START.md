# GEO Agent 快速启动指南

## 前置要求

- Python 3.10+
- Node.js 18+
- MongoDB（本地或远程）

## 快速启动（5 分钟）

### 1. 克隆项目（如果还没有）

```bash
cd /Users/zhihuili/Desktop/codes/geo_agent
```

### 2. 使用部署脚本（推荐）

```bash
./deploy.sh
```

脚本会自动：
- 检查环境
- 安装依赖
- 配置环境变量（需要手动填写）
- 启动服务

### 3. 手动启动

#### 后端

```bash
# 1. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # macOS/Linux

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
# 创建 .env 文件并填入 API 密钥（参考 config/settings.py）

# 4. 启动服务
python run_api.py
```

后端将在 `http://localhost:8000` 启动

#### 前端

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖
npm install

# 3. 配置环境变量
# 创建 .env.local 文件：
# NEXT_PUBLIC_API_URL=http://localhost:8000
# NEXT_PUBLIC_API_KEY=your-api-key

# 4. 启动开发服务器
npm run dev
```

前端将在 `http://localhost:3000` 启动

### 4. 验证部署

- 前端：http://localhost:3000
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

## 环境变量配置

### 后端 (.env)

必需的最小配置：

```bash
# API 认证（前端需要）
API_KEY=your-secret-api-key

# 数据库
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=geo_agent

# 至少配置一个 LLM API 密钥
OPENAI_API_KEY=your-key  # 或
GOOGLE_PROJECT_ID=your-project-id  # 或
PERPLEXITY_API_KEY=your-key  # 或
X_API_KEY=your-key
```

### 前端 (.env.local)

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_KEY=your-secret-api-key  # 与后端 API_KEY 一致
```

## 常见问题

### MongoDB 连接失败

如果使用本地 MongoDB：
```bash
# macOS
brew services start mongodb-community

# 或使用 Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

### 端口被占用

更改端口：
- 后端：修改 `run_api.py` 中的 `port=8000`
- 前端：修改 `frontend/package.json` 中的脚本或使用环境变量

### API 连接失败

1. 检查后端是否运行：`curl http://localhost:8000/health`
2. 检查 `NEXT_PUBLIC_API_URL` 是否正确
3. 检查 `API_KEY` 是否一致

## 下一步

- 查看 [DEPLOY.md](./DEPLOY.md) 了解详细部署说明
- 查看 [README.md](./README.md) 了解项目详情
- 访问 http://localhost:8000/docs 查看 API 文档

