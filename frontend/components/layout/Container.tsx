import { cn } from '@/lib/utils'
import type { ReactNode } from 'react'

interface ContainerProps {
  children: ReactNode
  className?: string
}

/**
 * 容器组件
 * 提供统一的页面容器样式
 */
export function Container({ children, className }: ContainerProps) {
  return (
    <div className={cn('container mx-auto px-4 py-8', className)}>
      {children}
    </div>
  )
}

