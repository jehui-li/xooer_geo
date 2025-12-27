'use client'

import { ReactNode } from 'react'
import { AlertCircle, RefreshCw, Home, ArrowLeft } from 'lucide-react'
import Link from 'next/link'
import { cn } from '@/lib/utils/cn'

interface FriendlyErrorProps {
  title?: string
  message: string
  description?: string
  icon?: ReactNode
  actions?: ReactNode
  className?: string
  variant?: 'error' | 'warning' | 'info'
}

const variantStyles = {
  error: {
    border: 'border-red-200 dark:border-red-800',
    bg: 'bg-red-50 dark:bg-red-950',
    text: 'text-red-800 dark:text-red-200',
    titleText: 'text-red-900 dark:text-red-100',
    icon: 'text-red-600 dark:text-red-400',
  },
  warning: {
    border: 'border-yellow-200 dark:border-yellow-800',
    bg: 'bg-yellow-50 dark:bg-yellow-950',
    text: 'text-yellow-800 dark:text-yellow-200',
    titleText: 'text-yellow-900 dark:text-yellow-100',
    icon: 'text-yellow-600 dark:text-yellow-400',
  },
  info: {
    border: 'border-blue-200 dark:border-blue-800',
    bg: 'bg-blue-50 dark:bg-blue-950',
    text: 'text-blue-800 dark:text-blue-200',
    titleText: 'text-blue-900 dark:text-blue-100',
    icon: 'text-blue-600 dark:text-blue-400',
  },
}

/**
 * 友好错误提示组件
 */
export function FriendlyError({
  title = '出现了错误',
  message,
  description,
  icon,
  actions,
  className,
  variant = 'error',
}: FriendlyErrorProps) {
  const styles = variantStyles[variant]
  const defaultIcon = <AlertCircle className={cn('h-6 w-6', styles.icon)} />

  return (
    <div
      className={cn(
        'rounded-lg border p-6',
        styles.border,
        styles.bg,
        className
      )}
    >
      <div className="flex items-start gap-4">
        <div className="flex-shrink-0">{icon || defaultIcon}</div>
        
        <div className="flex-1">
          <h3 className={cn('mb-2 text-lg font-semibold', styles.titleText)}>
            {title}
          </h3>
          
          <p className={cn('mb-2', styles.text)}>{message}</p>
          
          {description && (
            <p className={cn('text-sm', styles.text)}>{description}</p>
          )}
          
          {actions && <div className="mt-4 flex flex-wrap gap-3">{actions}</div>}
        </div>
      </div>
    </div>
  )
}

/**
 * 预设的错误组件
 */

interface AuditNotFoundErrorProps {
  auditId?: string
  onRetry?: () => void
  showBackButton?: boolean
}

export function AuditNotFoundError({
  auditId,
  onRetry,
  showBackButton = true,
}: AuditNotFoundErrorProps) {
  return (
    <FriendlyError
      title="检测不存在"
      message={auditId ? `未找到 ID 为 ${auditId} 的检测记录` : '检测记录不存在'}
      description="请检查检测 ID 是否正确，或返回列表查看所有检测记录"
      actions={
        <>
          {showBackButton && (
            <Link
              href="/audits"
              className={cn(
                'inline-flex items-center gap-2 rounded-md border border-input bg-background px-4 py-2',
                'text-sm font-medium shadow-sm',
                'transition-colors hover:bg-accent hover:text-accent-foreground',
                'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2'
              )}
            >
              <ArrowLeft className="h-4 w-4" />
              返回列表
            </Link>
          )}
          {onRetry && (
            <button
              onClick={onRetry}
              className={cn(
                'inline-flex items-center gap-2 rounded-md bg-primary px-4 py-2',
                'text-sm font-medium text-primary-foreground shadow',
                'transition-colors hover:bg-primary/90',
                'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2'
              )}
            >
              <RefreshCw className="h-4 w-4" />
              重新加载
            </button>
          )}
        </>
      }
    />
  )
}

interface NetworkErrorProps {
  onRetry?: () => void
  message?: string
}

export function NetworkError({ onRetry, message }: NetworkErrorProps) {
  return (
    <FriendlyError
      title="网络错误"
      message={message || '无法连接到服务器，请检查网络连接'}
      description="如果问题持续存在，请联系技术支持"
      actions={
        onRetry && (
          <button
            onClick={onRetry}
            className={cn(
              'inline-flex items-center gap-2 rounded-md bg-primary px-4 py-2',
              'text-sm font-medium text-primary-foreground shadow',
              'transition-colors hover:bg-primary/90',
              'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2'
            )}
          >
            <RefreshCw className="h-4 w-4" />
            重试
          </button>
        )
      }
    />
  )
}

