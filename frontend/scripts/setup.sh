#!/bin/bash

# GEO Agent Frontend 安装脚本

echo "🚀 开始安装 GEO Agent Frontend 依赖..."

# 检查 Node.js 版本
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
  echo "❌ 错误：需要 Node.js 18 或更高版本，当前版本：$(node -v)"
  exit 1
fi

echo "✅ Node.js 版本检查通过：$(node -v)"

# 安装依赖
echo "📦 正在安装 npm 依赖..."
npm install

if [ $? -ne 0 ]; then
  echo "❌ 依赖安装失败"
  exit 1
fi

echo "✅ 依赖安装完成"

# 检查 .env.local 文件
if [ ! -f ".env.local" ]; then
  echo "⚠️  未找到 .env.local 文件，正在创建..."
  cat > .env.local << EOF
# API 配置
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_KEY=your-api-key-here
EOF
  echo "✅ 已创建 .env.local 文件，请编辑并填入实际的 API 配置"
else
  echo "✅ .env.local 文件已存在"
fi

echo ""
echo "🎉 安装完成！"
echo ""
echo "下一步："
echo "1. 编辑 .env.local 文件，配置 API 地址和 API Key"
echo "2. 运行 'npm run dev' 启动开发服务器"
echo "3. 访问 http://localhost:3000"
echo ""
echo "提示："
echo "- 如需安装 shadcn/ui 组件，运行: npx shadcn-ui@latest init"
echo "- 然后使用: npx shadcn-ui@latest add [component-name] 安装组件"

