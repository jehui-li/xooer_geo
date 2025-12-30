import apiClient from './client'
import type { Strategy } from '@/types/api'

/**
 * 获取策略详情（如果后端有单独的策略接口）
 */
export async function getStrategy(strategyId: string): Promise<Strategy> {
  const response = await apiClient.get<Strategy>(`/strategies/${strategyId}`)
  return response.data
}

/**
 * 根据检测 ID 获取策略
 */
export async function getStrategyByAuditId(auditId: string): Promise<Strategy> {
  const response = await apiClient.get<Strategy>(`/audits/${auditId}/strategy`)
  return response.data
}

