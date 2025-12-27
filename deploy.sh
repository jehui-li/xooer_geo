#!/bin/bash

# GEO Agent 部署脚本
# 用于快速部署前后端服务

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo -e "${GREEN}=== GEO Agent 部署脚本 ===${NC}\n"

# 检查 Python
check_python() {
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}错误: 未找到 Python3${NC}"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✓ Python 版本: $PYTHON_VERSION${NC}"
}

# 检查 Node.js
check_node() {
    if ! command -v node &> /dev/null; then
        echo -e "${RED}错误: 未找到 Node.js${NC}"
        exit 1
    fi
    
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓ Node.js 版本: $NODE_VERSION${NC}"
}

# 检查 MongoDB
check_mongodb() {
    if command -v mongod &> /dev/null; then
        echo -e "${GREEN}✓ MongoDB 已安装${NC}"
    else
        echo -e "${YELLOW}⚠ MongoDB 未安装（如果使用远程 MongoDB，可以忽略）${NC}"
    fi
}

# 部署后端
deploy_backend() {
    echo -e "\n${GREEN}=== 部署后端 ===${NC}"
    
    cd "$BACKEND_DIR"
    
    # 检查虚拟环境
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}创建 Python 虚拟环境...${NC}"
        python3 -m venv venv
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 安装依赖
    echo -e "${YELLOW}安装 Python 依赖...${NC}"
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # 检查 .env 文件
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}⚠ .env 文件不存在，请创建并配置环境变量${NC}"
        echo -e "${YELLOW}参考 config/settings.py 查看需要的环境变量${NC}"
    else
        echo -e "${GREEN}✓ .env 文件存在${NC}"
    fi
    
    echo -e "${GREEN}后端部署完成！${NC}"
    echo -e "${YELLOW}启动命令: python run_api.py${NC}"
}

# 部署前端
deploy_frontend() {
    echo -e "\n${GREEN}=== 部署前端 ===${NC}"
    
    cd "$FRONTEND_DIR"
    
    # 检查 node_modules
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}安装 Node.js 依赖...${NC}"
        npm install
    else
        echo -e "${GREEN}✓ 依赖已安装${NC}"
    fi
    
    # 检查 .env.local 文件
    if [ ! -f ".env.local" ]; then
        echo -e "${YELLOW}⚠ .env.local 文件不存在，请创建并配置环境变量${NC}"
        echo -e "${YELLOW}必需变量: NEXT_PUBLIC_API_URL, NEXT_PUBLIC_API_KEY${NC}"
        if [ -f "env.example" ]; then
            echo -e "${YELLOW}参考 env.example 文件${NC}"
        fi
    else
        echo -e "${GREEN}✓ .env.local 文件存在${NC}"
    fi
    
    echo -e "${GREEN}前端部署完成！${NC}"
    echo -e "${YELLOW}开发模式: npm run dev${NC}"
    echo -e "${YELLOW}生产模式: npm run build && npm start${NC}"
}

# 启动服务
start_services() {
    echo -e "\n${GREEN}=== 启动服务 ===${NC}"
    echo -e "${YELLOW}选择启动模式:${NC}"
    echo "1) 开发模式（后端 + 前端）"
    echo "2) 仅后端"
    echo "3) 仅前端"
    echo "4) 跳过"
    read -p "请选择 (1-4): " choice
    
    case $choice in
        1)
            start_backend_dev &
            BACKEND_PID=$!
            sleep 3
            start_frontend_dev
            ;;
        2)
            start_backend_dev
            ;;
        3)
            start_frontend_dev
            ;;
        4)
            echo -e "${GREEN}跳过启动${NC}"
            ;;
        *)
            echo -e "${RED}无效选择${NC}"
            ;;
    esac
}

# 启动后端（开发模式）
start_backend_dev() {
    echo -e "\n${GREEN}启动后端服务...${NC}"
    cd "$BACKEND_DIR"
    source venv/bin/activate
    python run_api.py
}

# 启动前端（开发模式）
start_frontend_dev() {
    echo -e "\n${GREEN}启动前端服务...${NC}"
    cd "$FRONTEND_DIR"
    npm run dev
}

# 主函数
main() {
    check_python
    check_node
    check_mongodb
    
    echo -e "\n${YELLOW}开始部署...${NC}"
    
    deploy_backend
    deploy_frontend
    
    echo -e "\n${GREEN}=== 部署完成 ===${NC}\n"
    
    start_services
}

# 运行主函数
main

