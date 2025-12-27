# GEO Agent 服务状态

## 当前运行的服务

### 后端 API
- **状态**: 运行中
- **URL**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health
- **PID 文件**: /tmp/geo_agent_backend.pid
- **日志文件**: /tmp/geo_agent_backend.log

### 前端应用
- **状态**: 运行中
- **URL**: http://localhost:3000
- **PID 文件**: /tmp/geo_agent_frontend.pid
- **日志文件**: /tmp/geo_agent_frontend.log

## 常用命令

### 查看服务状态

```bash
# 检查后端
curl http://localhost:8000/health

# 检查前端
curl -I http://localhost:3000

# 查看进程
ps aux | grep -E "(python|node)" | grep -E "(run_api|next)"
```

### 查看日志

```bash
# 后端日志
tail -f /tmp/geo_agent_backend.log

# 前端日志
tail -f /tmp/geo_agent_frontend.log
```

### 停止服务

```bash
# 使用停止脚本（推荐）
./stop_services.sh

# 或手动停止
kill $(cat /tmp/geo_agent_backend.pid)
kill $(cat /tmp/geo_agent_frontend.pid)
```

### 重启服务

```bash
# 停止服务
./stop_services.sh

# 重新启动（使用 deploy.sh 或手动启动）
```

## 注意事项

1. **环境变量**: 确保 `.env` 和 `frontend/.env.local` 文件已正确配置
2. **MongoDB**: 确保 MongoDB 服务正在运行
3. **API 密钥**: 确保至少配置了一个 LLM API 密钥
4. **端口占用**: 如果端口 8000 或 3000 被占用，需要先释放端口

## 故障排查

### 后端无法启动
1. 检查 Python 虚拟环境是否激活
2. 检查依赖是否安装完整
3. 查看日志文件: `cat /tmp/geo_agent_backend.log`
4. 检查 MongoDB 连接

### 前端无法启动
1. 检查 Node.js 版本（需要 18+）
2. 检查依赖是否安装: `cd frontend && npm install`
3. 查看日志文件: `cat /tmp/geo_agent_frontend.log`
4. 检查 `.env.local` 配置

### API 连接失败
1. 检查后端是否运行: `curl http://localhost:8000/health`
2. 检查 `NEXT_PUBLIC_API_URL` 配置
3. 检查 `API_KEY` 是否前后端一致
4. 检查 CORS 配置

