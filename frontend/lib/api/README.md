# API 客户端使用指南

## 概述

API 客户端提供了统一、类型安全的方式来调用后端 API。所有 API 调用都通过封装的客户端进行，自动处理认证、错误处理和请求配置。

## 目录结构

```
lib/api/
├── client.ts       # Axios 实例和拦截器配置
├── audits.ts       # 检测相关的 API 方法
├── strategies.ts   # 策略相关的 API 方法
├── types.ts        # API 错误处理类型
└── index.ts        # 统一导出
```

## 快速开始

### 1. 导入 API 方法

```typescript
import { createAudit, getAudit, listAudits } from '@/lib/api'
// 或
import { createAudit } from '@/lib/api/audits'
```

### 2. 调用 API

```typescript
// 创建检测
const audit = await createAudit({
  brand_name: 'Asana',
  target_brand: 'Asana',
  keywords: ['project management software'],
})

// 获取检测详情
const auditDetail = await getAudit(audit.audit_id)

// 获取检测列表
const { audits, total } = await listAudits({ skip: 0, limit: 10 })
```

## API 方法

### 检测 API (`lib/api/audits.ts`)

#### `createAudit(data: AuditRequest): Promise<AuditResponse>`

创建新的检测任务。

```typescript
const audit = await createAudit({
  brand_name: 'Asana',
  target_brand: 'Asana',
  keywords: ['project management', 'task management'],
  target_website: 'https://asana.com',
})
```

#### `getAudit(auditId: string): Promise<AuditResponse>`

获取检测详情。

```typescript
const audit = await getAudit('audit_20240101_001')
```

#### `listAudits(params?): Promise<AuditListResponse>`

获取检测列表（支持分页）。

```typescript
const { audits, total } = await listAudits({
  skip: 0,
  limit: 20,
})
```

#### `deleteAudit(auditId: string): Promise<void>`

删除检测。

```typescript
await deleteAudit('audit_20240101_001')
```

### 策略 API (`lib/api/strategies.ts`)

#### `getStrategyByAuditId(auditId: string): Promise<Strategy>`

根据检测 ID 获取策略。

```typescript
const strategy = await getStrategyByAuditId('audit_20240101_001')
```

## 错误处理

### 使用 try-catch

```typescript
try {
  const audit = await createAudit(data)
} catch (error) {
  // 使用 extractApiError 提取错误信息
  import { extractApiError } from '@/lib/api'
  const apiError = extractApiError(error)
  console.error(apiError.message, apiError.status)
}
```

### 错误类型检查

```typescript
import { isApiErrorStatus } from '@/lib/api'

try {
  await deleteAudit(auditId)
} catch (error) {
  if (isApiErrorStatus(error, 404)) {
    // 处理 404 错误
    console.log('检测不存在')
  } else if (isApiErrorStatus(error, 401)) {
    // 处理 401 错误
    console.log('未授权，请检查 API Key')
  }
}
```

## 配置

### 环境变量

API 客户端从环境变量读取配置：

- `NEXT_PUBLIC_API_URL`: API 地址（默认：http://localhost:8000）
- `NEXT_PUBLIC_API_KEY`: API Key（可选）

详见 [README_ENV.md](../README_ENV.md)

### 请求配置

默认配置：
- 超时时间：30 秒
- Content-Type: application/json
- 自动添加 X-API-Key header（如果配置了 API Key）

## 类型安全

所有 API 方法都有完整的 TypeScript 类型定义：

```typescript
import type { AuditRequest, AuditResponse } from '@/types/api'

// TypeScript 会检查类型
const request: AuditRequest = {
  brand_name: 'Asana',
  target_brand: 'Asana',
  keywords: ['project management'],
}

// 返回类型自动推断为 AuditResponse
const response = await createAudit(request)
console.log(response.audit_id) // ✅ 有类型提示
```

## 开发调试

在开发环境下，API 客户端会自动记录请求和响应日志：

```
[API Request] POST /audits { ... }
[API Response] POST /audits { status: 200, data: {...} }
```

## 高级用法

### 直接使用 apiClient

如果需要直接使用 axios 实例：

```typescript
import { apiClient } from '@/lib/api'

const response = await apiClient.get('/custom-endpoint')
```

### 获取配置信息

```typescript
import { API_CONFIG } from '@/lib/api'

console.log(API_CONFIG.baseURL)
```

