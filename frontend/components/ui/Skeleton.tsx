import { cn } from '@/lib/utils/cn'

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  className?: string
}

/**
 * 骨架屏组件
 * 用于加载状态的占位符
 */
export function Skeleton({ className, ...props }: SkeletonProps) {
  return (
    <div
      className={cn('animate-pulse rounded-md bg-muted', className)}
      {...props}
    />
  )
}

/**
 * 检测详情页骨架屏
 */
export function AuditDetailSkeleton() {
  return (
    <div className="container py-8 space-y-6">
      {/* 返回按钮骨架 */}
      <div className="flex items-center justify-between">
        <Skeleton className="h-6 w-24" />
        <Skeleton className="h-10 w-32" />
      </div>

      {/* 基本信息卡片骨架 */}
      <div className="rounded-lg border bg-card p-6 space-y-4">
        <Skeleton className="h-8 w-48" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-6 w-32" />
          </div>
          <div className="space-y-2">
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-6 w-32" />
          </div>
          <div className="space-y-2">
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-6 w-32" />
          </div>
          <div className="space-y-2">
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-6 w-32" />
          </div>
        </div>
      </div>

      {/* 关键词卡片骨架 */}
      <div className="rounded-lg border bg-card p-6 space-y-4">
        <Skeleton className="h-6 w-24" />
        <div className="flex flex-wrap gap-2">
          <Skeleton className="h-8 w-20 rounded-md" />
          <Skeleton className="h-8 w-24 rounded-md" />
          <Skeleton className="h-8 w-16 rounded-md" />
        </div>
      </div>

      {/* GEO Score 卡片骨架 */}
      <div className="rounded-lg border bg-card p-6 space-y-6">
        <Skeleton className="h-7 w-40" />
        <div className="flex justify-center">
          <Skeleton className="h-64 w-64 rounded-full" />
        </div>
      </div>

      {/* 评分明细卡片骨架 */}
      <div className="rounded-lg border bg-card p-6 space-y-6">
        <Skeleton className="h-7 w-32" />
        <Skeleton className="h-64 w-full" />
      </div>
    </div>
  )
}

