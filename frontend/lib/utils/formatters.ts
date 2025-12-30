import { format, formatDistanceToNow } from 'date-fns'
import { zhCN } from 'date-fns/locale'

/**
 * 格式化日期时间
 */
export function formatDateTime(date: string | Date): string {
  if (!date) return 'N/A'
  try {
    const dateObj = typeof date === 'string' ? new Date(date) : date
    // 检查日期是否有效
    if (isNaN(dateObj.getTime())) {
      console.warn('Invalid date:', date)
      return 'Invalid Date'
    }
    return format(dateObj, 'yyyy-MM-dd HH:mm:ss', { locale: zhCN })
  } catch (error) {
    console.error('Error formatting date:', date, error)
    return 'Invalid Date'
  }
}

/**
 * 格式化日期
 */
export function formatDate(date: string | Date): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date
  return format(dateObj, 'yyyy-MM-dd', { locale: zhCN })
}

/**
 * 相对时间（如：3 小时前）
 */
export function formatRelativeTime(date: string | Date): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date
  return formatDistanceToNow(dateObj, { addSuffix: true, locale: zhCN })
}

/**
 * 格式化数字（添加千分位）
 */
export function formatNumber(num: number): string {
  return num.toLocaleString('zh-CN')
}

/**
 * 格式化百分比
 */
export function formatPercent(value: number, decimals: number = 1): string {
  return `${value.toFixed(decimals)}%`
}

/**
 * 格式化 GEO Score（带颜色标识）
 */
export function formatGeoScore(score: number | undefined | null): string {
  if (score === undefined || score === null) {
    return 'N/A'
  }
  return score.toFixed(1)
}

