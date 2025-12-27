'use client'

import { useEffect } from 'react'
import { X, CheckCircle2, AlertCircle, Info, XCircle } from 'lucide-react'
import { cn } from '@/lib/utils/cn'

export type ToastType = 'success' | 'error' | 'info' | 'warning'

export interface Toast {
  id: string
  message: string
  type: ToastType
  duration?: number
}

interface ToastProps {
  toast: Toast
  onClose: (id: string) => void
}

const toastConfig: Record<ToastType, { icon: typeof CheckCircle2; bgColor: string; textColor: string }> = {
  success: {
    icon: CheckCircle2,
    bgColor: 'bg-green-50 dark:bg-green-950',
    textColor: 'text-green-800 dark:text-green-200',
  },
  error: {
    icon: XCircle,
    bgColor: 'bg-red-50 dark:bg-red-950',
    textColor: 'text-red-800 dark:text-red-200',
  },
  info: {
    icon: Info,
    bgColor: 'bg-blue-50 dark:bg-blue-950',
    textColor: 'text-blue-800 dark:text-blue-200',
  },
  warning: {
    icon: AlertCircle,
    bgColor: 'bg-yellow-50 dark:bg-yellow-950',
    textColor: 'text-yellow-800 dark:text-yellow-200',
  },
}

export function ToastComponent({ toast, onClose }: ToastProps) {
  const config = toastConfig[toast.type]
  const Icon = config.icon
  const duration = toast.duration || 5000

  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        onClose(toast.id)
      }, duration)

      return () => clearTimeout(timer)
    }
  }, [duration, toast.id, onClose])

  return (
    <div
      className={cn(
        'flex items-start gap-3 rounded-lg border p-4 shadow-lg transition-all',
        config.bgColor,
        config.textColor,
        'animate-in slide-in-from-bottom-2 fade-in-0'
      )}
    >
      <Icon className="mt-0.5 h-5 w-5 flex-shrink-0" />
      <p className="flex-1 text-sm font-medium">{toast.message}</p>
      <button
        type="button"
        onClick={() => onClose(toast.id)}
        className="flex-shrink-0 rounded-md p-1 transition-colors hover:bg-black/10 dark:hover:bg-white/10"
        aria-label="关闭通知"
      >
        <X className="h-4 w-4" />
      </button>
    </div>
  )
}

interface ToastContainerProps {
  toasts: Toast[]
  onClose: (id: string) => void
}

export function ToastContainer({ toasts, onClose }: ToastContainerProps) {
  if (toasts.length === 0) return null

  return (
    <div className="pointer-events-none fixed bottom-4 right-4 z-50 flex max-w-md flex-col gap-2">
      {toasts.map((toast) => (
        <div key={toast.id} className="pointer-events-auto">
          <ToastComponent toast={toast} onClose={onClose} />
        </div>
      ))}
    </div>
  )
}

