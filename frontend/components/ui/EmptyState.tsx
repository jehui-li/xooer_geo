'use client'

import { ReactNode } from 'react'
import { LucideIcon } from 'lucide-react'
import { cn } from '@/lib/utils/cn'

interface EmptyStateProps {
  icon?: LucideIcon
  iconSize?: number
  title: string
  description?: string
  action?: ReactNode
  className?: string
}

/**
 * 空状态组件
 * 用于显示没有数据时的友好提示
 */
export function EmptyState({
  icon: Icon,
  iconSize = 48,
  title,
  description,
  action,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center rounded-lg border bg-card p-12 text-center',
        className
      )}
    >
      {Icon && (
        <div className="mb-4 text-muted-foreground">
          <Icon size={iconSize} strokeWidth={1.5} />
        </div>
      )}
      
      <h3 className="mb-2 text-lg font-semibold">{title}</h3>
      
      {description && (
        <p className="mb-6 max-w-md text-sm text-muted-foreground">{description}</p>
      )}
      
      {action && <div>{action}</div>}
    </div>
  )
}

/**
 * 预设的空状态组件
 */

export function EmptyAuditList() {
  return (
    <EmptyState
      title="暂无检测记录"
      description="创建您的第一个检测任务，开始分析品牌在生成式引擎中的表现"
    />
  )
}

export function EmptyAuditDetail() {
  return (
    <EmptyState
      title="检测不存在"
      description="请检查检测 ID 是否正确，或返回列表查看所有检测记录"
    />
  )
}

export function EmptyStrategyRecommendations() {
  return (
    <EmptyState
      title="暂无策略建议"
      description="策略建议将在此处显示，请等待检测完成后查看"
    />
  )
}

export function EmptyScoreData() {
  return (
    <EmptyState
      title="暂无评分数据"
      description="评分数据将在检测完成后显示，请稍候"
    />
  )
}

