#!/usr/bin/env python3
"""
GEO Agent API 启动脚本
"""

import os
import uvicorn
from src.api.main import app

# 从环境变量获取配置，默认为开发模式
IS_DEV = os.getenv("APP_ENV", "development") == "development"

if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app",  # 使用字符串形式的导入路径以支持 reload
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=IS_DEV,  # 仅开发模式启用自动重载
        workers=1 if IS_DEV else 4  # 生产环境使用多进程
    )

