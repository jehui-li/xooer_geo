# 安装指南

## 关于虚拟环境

**不需要安装 Python 虚拟环境！**

前端项目使用 Node.js，通过 npm/yarn/pnpm 管理依赖。虚拟环境是 Python 项目的概念。

## 安装步骤

### 1. 安装 Node.js

确保已安装 Node.js 18+ 和 npm/yarn/pnpm。

检查版本：
```bash
node --version  # 应该 >= 18.0.0
npm --version   # 或 yarn --version / pnpm --version
```

### 2. 安装项目依赖

```bash
cd frontend
npm install
# 或
yarn install
# 或
pnpm install
```

### 3. 配置环境变量

创建 `.env.local` 文件（在 `frontend/` 目录下）：

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_KEY=your-api-key-here
```

### 4. 安装 shadcn/ui 组件（可选）

shadcn/ui 不是传统的 npm 包，而是通过 CLI 工具安装组件。

#### 方法 A：使用 shadcn/ui CLI（推荐）

```bash
# 安装 shadcn/ui CLI
npx shadcn-ui@latest init

# 安装常用组件（根据需要）
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add input
npx shadcn-ui@latest add label
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add table
npx shadcn-ui@latest add badge
npx shadcn-ui@latest add tabs
```

#### 方法 B：手动创建基础组件

如果需要，我可以帮你创建基础的 UI 组件（Button, Card 等）。

### 5. 启动开发服务器

```bash
npm run dev
# 或
yarn dev
# 或
pnpm dev
```

访问 http://localhost:3000

## 已安装的依赖

### 核心依赖
- ✅ Next.js 14.0.4
- ✅ React 18.2.0
- ✅ TypeScript 5.3.3
- ✅ Tailwind CSS 3.4.0

### 功能依赖
- ✅ axios - HTTP 客户端
- ✅ recharts - 图表库
- ✅ react-hook-form + zod - 表单处理
- ✅ zustand - 状态管理（可选）
- ✅ date-fns - 日期处理
- ✅ clsx + tailwind-merge - 样式工具

### shadcn/ui 相关依赖
- ✅ class-variance-authority - 样式变体
- ✅ lucide-react - 图标库
- ✅ @radix-ui/* - 无障碍 UI 组件
- ✅ tailwindcss-animate - 动画支持

## 验证安装

运行以下命令验证安装：

```bash
# 检查 TypeScript 编译
npm run build

# 检查代码规范
npm run lint
```

## 常见问题

### Q: 安装依赖时出错？
A: 尝试清除缓存后重新安装：
```bash
rm -rf node_modules package-lock.json
npm install
```

### Q: 需要使用 Python 虚拟环境吗？
A: 不需要。前端项目使用 Node.js，后端 Python 项目才需要虚拟环境。

### Q: shadcn/ui 组件在哪里？
A: shadcn/ui 组件需要单独安装。运行 `npx shadcn-ui@latest init` 初始化，然后使用 `add` 命令安装需要的组件。

