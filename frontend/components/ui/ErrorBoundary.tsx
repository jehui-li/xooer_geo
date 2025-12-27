'use client'

import React, { Component, ErrorInfo, ReactNode } from 'react'
import { AlertTriangle, RefreshCw, Home } from 'lucide-react'
import Link from 'next/link'
import { cn } from '@/lib/utils/cn'

interface Props {
  children: ReactNode
  fallback?: ReactNode
  onError?: (error: Error, errorInfo: ErrorInfo) => void
}

interface State {
  hasError: boolean
  error: Error | null
}

/**
 * React 错误边界组件
 * 捕获子组件树中的 JavaScript 错误，并显示降级 UI
 */
export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
    }
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
    }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // 记录错误信息
    console.error('ErrorBoundary caught an error:', error, errorInfo)

    // 调用可选的回调函数
    if (this.props.onError) {
      this.props.onError(error, errorInfo)
    }
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
    })
  }

  render() {
    if (this.state.hasError) {
      // 如果提供了自定义 fallback，使用它
      if (this.props.fallback) {
        return this.props.fallback
      }

      // 默认错误 UI
      return (
        <div className="container mx-auto px-4 py-16">
          <div className="mx-auto max-w-2xl">
            <div className="rounded-lg border border-red-200 bg-red-50 p-8 text-center dark:border-red-800 dark:bg-red-950">
              <div className="mb-4 flex justify-center">
                <AlertTriangle className="h-16 w-16 text-red-600 dark:text-red-400" />
              </div>
              
              <h1 className="mb-2 text-2xl font-bold text-red-900 dark:text-red-100">
                出现了错误
              </h1>
              
              <p className="mb-6 text-red-800 dark:text-red-200">
                抱歉，页面渲染时出现了意外错误。请尝试刷新页面或返回首页。
              </p>

              {this.state.error && process.env.NODE_ENV === 'development' && (
                <details className="mb-6 rounded-md bg-red-100 p-4 text-left dark:bg-red-900">
                  <summary className="cursor-pointer font-medium text-red-900 dark:text-red-100">
                错误详情（开发模式）
              </summary>
                  <pre className="mt-2 overflow-auto text-xs text-red-800 dark:text-red-200">
                {this.state.error.toString()}
                {this.state.error.stack && `\n${this.state.error.stack}`}
              </pre>
                </details>
              )}

              <div className="flex justify-center gap-4">
                <button
                  onClick={this.handleReset}
                  className={cn(
                    'inline-flex items-center gap-2 rounded-md bg-red-600 px-4 py-2',
                    'text-sm font-medium text-white',
                    'transition-colors hover:bg-red-700',
                    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-500 focus-visible:ring-offset-2'
                  )}
                >
                  <RefreshCw className="h-4 w-4" />
                  重试
                </button>
                
                <Link
                  href="/"
                  className={cn(
                    'inline-flex items-center gap-2 rounded-md border border-red-600 bg-transparent px-4 py-2',
                    'text-sm font-medium text-red-600',
                    'transition-colors hover:bg-red-50 dark:hover:bg-red-900',
                    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-500 focus-visible:ring-offset-2'
                  )}
                >
                  <Home className="h-4 w-4" />
                  返回首页
                </Link>
              </div>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

