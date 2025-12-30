/**
 * API 响应和错误类型定义
 * 用于类型安全和错误处理
 */

import type { AxiosError } from 'axios'
import type { ErrorResponse } from '@/types/api'

/**
 * API 错误类型
 */
export interface ApiError {
  message: string
  status?: number
  detail?: string
  code?: string
}

/**
 * 从 Axios 错误中提取 API 错误信息
 */
export function extractApiError(error: unknown): ApiError {
  if (typeof error === 'object' && error !== null && 'response' in error) {
    const axiosError = error as AxiosError<ErrorResponse>
    const response = axiosError.response

    if (response) {
      return {
        message: response.data?.error || '请求失败',
        status: response.status,
        detail: response.data?.detail,
      }
    }
  }

  // 网络错误或其他错误
  if (error instanceof Error) {
    return {
      message: error.message || '未知错误',
    }
  }

  return {
    message: '未知错误',
  }
}

/**
 * 检查错误是否为特定状态码
 */
export function isApiErrorStatus(error: unknown, status: number): boolean {
  if (typeof error === 'object' && error !== null && 'response' in error) {
    const axiosError = error as AxiosError
    return axiosError.response?.status === status
  }
  return false
}

