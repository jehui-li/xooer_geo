# GEO Agent Frontend

GEO Agent 前端应用，使用 Next.js 14 + TypeScript + Tailwind CSS 构建。

## 项目结构

```
frontend/
├── app/                    # Next.js App Router
│   ├── layout.tsx         # 根布局
│   ├── page.tsx           # 首页
│   ├── globals.css        # 全局样式
│   └── ...
├── components/            # React 组件
│   ├── ui/               # 基础 UI 组件
│   ├── audits/           # 检测相关组件
│   ├── charts/           # 图表组件
│   ├── scoring/          # 评分相关组件
│   └── strategy/         # 策略相关组件
├── lib/                  # 工具库
│   ├── api/             # API 客户端
│   │   ├── client.ts    # Axios 实例
│   │   └── audits.ts    # 检测 API
│   └── utils.ts         # 工具函数
├── types/                # TypeScript 类型定义
│   └── api.ts           # API 类型
└── public/              # 静态资源
```

## 开发

### 快速开始

**方式一：使用安装脚本（推荐）**

```bash
./scripts/setup.sh
```

**方式二：手动安装**

#### 1. 安装依赖

```bash
npm install
# 或
yarn install
# 或
pnpm install
```

#### 2. 配置环境变量

创建 `.env.local` 文件（在 `frontend/` 目录下）：

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_KEY=your-api-key-here
```

#### 3. 安装 shadcn/ui 组件（可选）

```bash
# 初始化 shadcn/ui
npx shadcn-ui@latest init

# 安装常用组件
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add input
npx shadcn-ui@latest add label
```

### 启动开发服务器

```bash
npm run dev
# 或
yarn dev
# 或
pnpm dev
```

打开 [http://localhost:3000](http://localhost:3000) 查看应用。

## 重要提示

### ⚠️ 关于虚拟环境

**前端项目不需要 Python 虚拟环境！**

- 前端使用 Node.js，通过 npm/yarn/pnpm 管理依赖
- 虚拟环境是 Python 项目的概念
- 只需要安装 Node.js 18+ 即可

详细安装说明请参考 [INSTALL.md](./INSTALL.md)

## 构建

```bash
npm run build
npm run start
```

## 技术栈

- **框架**: Next.js 14 (App Router)
- **语言**: TypeScript
- **样式**: Tailwind CSS
- **HTTP 客户端**: Axios
- **图表**: Recharts
- **表单**: React Hook Form + Zod
- **状态管理**: Zustand

