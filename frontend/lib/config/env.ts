/**
 * 环境变量配置
 * 统一管理和验证环境变量
 */

/**
 * API 配置
 */
export const API_CONFIG = {
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  apiKey: process.env.NEXT_PUBLIC_API_KEY || '',
} as const

/**
 * 应用配置
 */
export const APP_CONFIG = {
  name: process.env.NEXT_PUBLIC_APP_NAME || 'GEO Agent',
  debug: process.env.NEXT_PUBLIC_DEBUG === 'true',
  isDevelopment: process.env.NODE_ENV === 'development',
  isProduction: process.env.NODE_ENV === 'production',
} as const

/**
 * 验证环境变量配置
 */
export function validateEnvConfig(): { valid: boolean; errors: string[] } {
  const errors: string[] = []

  // 验证 API URL
  if (!API_CONFIG.baseURL) {
    errors.push('NEXT_PUBLIC_API_URL 未配置')
  } else {
    try {
      new URL(API_CONFIG.baseURL)
    } catch {
      errors.push('NEXT_PUBLIC_API_URL 格式无效（必须是有效的 URL）')
    }
  }

  // API Key 是可选的，但如果有值应该检查格式
  if (API_CONFIG.apiKey && API_CONFIG.apiKey.length < 10) {
    console.warn('⚠️ API Key 看起来太短，请确认是否正确')
  }

  return {
    valid: errors.length === 0,
    errors,
  }
}

/**
 * 在开发环境下打印配置信息
 */
export function logConfig() {
  if (APP_CONFIG.isDevelopment) {
    console.log('📋 环境配置：', {
      API_URL: API_CONFIG.baseURL,
      API_KEY: API_CONFIG.apiKey ? '***' + API_CONFIG.apiKey.slice(-4) : '未配置',
      NODE_ENV: process.env.NODE_ENV,
    })
  }
}

