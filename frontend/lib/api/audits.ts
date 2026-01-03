import apiClient from './client'
import type {
  AuditRequest,
  AuditResponse,
  AuditListResponse,
  StatsResponse,
} from '@/types/api'

/**
 * 创建检测
 */
export async function createAudit(data: AuditRequest): Promise<AuditResponse> {
  const response = await apiClient.post<AuditResponse>('/detect', data)
  return response.data
}

/**
 * 获取检测详情
 */
export async function getAudit(auditId: string): Promise<AuditResponse> {
  const response = await apiClient.get<AuditResponse>(`/audits/${auditId}`)
  return response.data
}

/**
 * 获取检测列表
 */
export async function listAudits(params?: {
  skip?: number
  limit?: number
}): Promise<AuditListResponse> {
  const response = await apiClient.get<AuditListResponse>('/audits', {
    params,
  })
  return response.data
}

/**
 * 删除检测
 */
export async function deleteAudit(auditId: string): Promise<void> {
  await apiClient.delete(`/audits/${auditId}`)
}

/**
 * 获取统计数据
 */
export async function getStats(): Promise<StatsResponse> {
  const response = await apiClient.get<StatsResponse>('/stats')
  return response.data
}

