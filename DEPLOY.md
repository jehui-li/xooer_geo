# GEO Agent 部署指南

本文档说明如何部署 GEO Agent 前后端服务。

## 目录

- [环境要求](#环境要求)
- [后端部署](#后端部署)
- [前端部署](#前端部署)
- [完整部署流程](#完整部署流程)
- [生产环境配置](#生产环境配置)

## 环境要求

### 后端
- Python 3.10+
- MongoDB (本地或远程)
- 各种 API 密钥（OpenAI, Google Vertex AI, Perplexity, X API）

### 前端
- Node.js 18+
- npm/yarn/pnpm

## 后端部署

### 1. 安装 Python 依赖

```bash
# 确保在项目根目录
cd /Users/zhihuili/Desktop/codes/geo_agent

# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件（在项目根目录）：

```bash
# API 密钥
OPENAI_API_KEY=your-openai-api-key
GOOGLE_PROJECT_ID=your-google-project-id
GOOGLE_LOCATION=us-central1
PERPLEXITY_API_KEY=your-perplexity-api-key
X_API_KEY=your-x-api-key
X_API_SECRET_KEY=your-x-api-secret-key
X_ACCESS_TOKEN=your-x-access-token
X_ACCESS_TOKEN_SECRET=your-x-access-token-secret
X_BEARER_TOKEN=your-x-bearer-token

# 数据库配置
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=geo_agent

# API 配置
API_KEY=your-api-key-for-frontend  # 用于前端认证
LOG_LEVEL=INFO
APP_ENV=production
```

### 3. 启动 MongoDB（如果使用本地）

```bash
# macOS (使用 Homebrew)
brew services start mongodb-community

# Linux
sudo systemctl start mongod

# 或使用 Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

### 4. 启动后端服务

#### 开发模式

```bash
python run_api.py
```

服务将在 `http://0.0.0.0:8000` 启动。

#### 生产模式

```bash
# 使用 uvicorn 直接启动（推荐）
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4

# 或使用 gunicorn（需要安装 gunicorn）
pip install gunicorn
gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 5. 验证后端服务

```bash
# 健康检查
curl http://localhost:8000/health

# 根路径
curl http://localhost:8000/
```

## 前端部署

### 1. 安装 Node.js 依赖

```bash
cd frontend
npm install
```

### 2. 配置环境变量

创建 `frontend/.env.local` 文件：

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_KEY=your-api-key-here  # 与后端 API_KEY 保持一致
```

### 3. 构建前端

```bash
# 构建生产版本
npm run build

# 启动生产服务器
npm start
```

服务将在 `http://localhost:3000` 启动。

### 4. 开发模式

```bash
npm run dev
```

## 完整部署流程

### 本地开发环境

1. **启动 MongoDB**
   ```bash
   # 如果使用本地 MongoDB
   brew services start mongodb-community
   # 或使用 Docker
   docker run -d -p 27017:27017 --name mongodb mongo:latest
   ```

2. **启动后端**
   ```bash
   cd /Users/zhihuili/Desktop/codes/geo_agent
   source venv/bin/activate  # 如果使用虚拟环境
   python run_api.py
   ```

3. **启动前端**
   ```bash
   cd frontend
   npm run dev
   ```

4. **访问应用**
   - 前端：http://localhost:3000
   - 后端 API：http://localhost:8000
   - API 文档：http://localhost:8000/docs

### 生产环境部署

#### 使用 systemd（Linux）

1. **创建后端服务文件** `/etc/systemd/system/geo-agent-api.service`:

```ini
[Unit]
Description=GEO Agent API Service
After=network.target mongodb.service

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/geo_agent
Environment="PATH=/path/to/geo_agent/venv/bin"
ExecStart=/path/to/geo_agent/venv/bin/uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

2. **创建前端服务文件** `/etc/systemd/system/geo-agent-frontend.service`:

```ini
[Unit]
Description=GEO Agent Frontend Service
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/geo_agent/frontend
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. **启动服务**

```bash
sudo systemctl daemon-reload
sudo systemctl enable geo-agent-api
sudo systemctl enable geo-agent-frontend
sudo systemctl start geo-agent-api
sudo systemctl start geo-agent-frontend
```

#### 使用 Docker Compose

创建 `docker-compose.yml`:

```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:latest
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    environment:
      MONGO_INITDB_DATABASE: geo_agent

  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URI=mongodb://mongodb:27017
    depends_on:
      - mongodb
    volumes:
      - ./.env:/app/.env

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend

volumes:
  mongodb_data:
```

#### 使用 PM2（Node.js 进程管理）

```bash
# 安装 PM2
npm install -g pm2

# 启动后端（需要创建 ecosystem.config.js）
pm2 start ecosystem.config.js

# 启动前端
cd frontend
pm2 start npm --name "geo-agent-frontend" -- start
```

## 生产环境配置

### 后端配置建议

1. **禁用自动重载**
   - `run_api.py` 中的 `reload=True` 应改为 `reload=False`

2. **配置 CORS**
   - 在 `src/api/main.py` 中限制允许的源：
   ```python
   allow_origins=["http://localhost:3000", "https://yourdomain.com"]
   ```

3. **使用 HTTPS**
   - 使用 Nginx 作为反向代理
   - 配置 SSL 证书

4. **日志管理**
   - 配置日志轮转
   - 使用结构化日志

### 前端配置建议

1. **环境变量**
   - 生产环境使用 `.env.production`
   - `NEXT_PUBLIC_API_URL` 应指向生产后端地址

2. **静态资源优化**
   - Next.js 会自动优化
   - 考虑使用 CDN

3. **反向代理**
   - 使用 Nginx 代理前端和后端

### Nginx 配置示例

```nginx
# 后端 API
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# 前端
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 验证部署

### 后端验证

```bash
# 健康检查
curl http://localhost:8000/health

# API 文档
open http://localhost:8000/docs
```

### 前端验证

```bash
# 访问前端
open http://localhost:3000

# 检查 API 连接
curl http://localhost:3000/api/health  # 如果配置了 API 路由
```

## 故障排查

### 后端问题

1. **MongoDB 连接失败**
   - 检查 MongoDB 是否运行
   - 检查 `MONGODB_URI` 配置

2. **API 密钥错误**
   - 检查 `.env` 文件
   - 验证 API 密钥有效性

3. **端口被占用**
   - 更改 `run_api.py` 中的端口
   - 或杀死占用端口的进程

### 前端问题

1. **API 连接失败**
   - 检查 `NEXT_PUBLIC_API_URL` 配置
   - 检查后端服务是否运行
   - 检查 CORS 配置

2. **构建失败**
   - 检查 Node.js 版本（需要 18+）
   - 清除缓存：`rm -rf .next node_modules && npm install`

## 安全建议

1. **API 密钥安全**
   - 不要将 `.env` 文件提交到 Git
   - 使用环境变量或密钥管理服务

2. **API 认证**
   - 生产环境必须使用 API Key 认证
   - 考虑使用 JWT 或其他认证方式

3. **HTTPS**
   - 生产环境必须使用 HTTPS
   - 配置 SSL 证书

4. **防火墙**
   - 只开放必要端口
   - 限制数据库访问

## 监控和维护

1. **日志监控**
   - 定期检查日志文件
   - 设置日志报警

2. **性能监控**
   - 监控 API 响应时间
   - 监控数据库性能

3. **备份**
   - 定期备份 MongoDB 数据
   - 备份配置文件

