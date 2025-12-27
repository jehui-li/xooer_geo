'use client'

import { useState, useEffect, useMemo } from 'react'
import Link from 'next/link'
import { listAudits } from '@/lib/api'
import type { AuditResponse } from '@/types/api'
import { formatDateTime, formatRelativeTime } from '@/lib/utils/formatters'
import { Skeleton } from '@/components/ui/Skeleton'
import { EmptyAuditList } from '@/components/ui/EmptyState'
import { NetworkError } from '@/components/ui/FriendlyError'

type AuditStatus = 'pending' | 'running' | 'completed' | 'failed' | 'all'

/**
 * 检测列表页
 */
export default function AuditsPage() {
  const [audits, setAudits] = useState<AuditResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [total, setTotal] = useState(0)

  // 分页参数
  const [skip, setSkip] = useState(0)
  const [limit] = useState(20)

  // 筛选参数
  const [statusFilter, setStatusFilter] = useState<AuditStatus>('all')

  // 获取检测列表
  useEffect(() => {
    async function fetchAudits() {
      try {
        setLoading(true)
        setError(null)
        const response = await listAudits({ skip, limit })
        setAudits(response.audits)
        setTotal(response.total)
      } catch (err) {
        setError('获取检测列表失败，请稍后重试')
        console.error('Failed to fetch audits:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchAudits()
  }, [skip, limit])

  // 客户端筛选（按状态）
  const filteredAudits = useMemo(() => {
    if (statusFilter === 'all') {
      return audits
    }
    return audits.filter((audit) => audit.status === statusFilter)
  }, [audits, statusFilter])

  // 筛选后的总数
  const filteredTotal = useMemo(() => {
    if (statusFilter === 'all') {
      return total
    }
    return filteredAudits.length
  }, [total, filteredAudits.length, statusFilter])

  // 重置分页当筛选条件改变时
  useEffect(() => {
    setSkip(0)
  }, [statusFilter])

  // 状态标签样式
  const getStatusBadge = (status: string) => {
    const styles = {
      pending: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300',
      running: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
      completed: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
      failed: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
    }
    const labels = {
      pending: '等待中',
      running: '进行中',
      completed: '已完成',
      failed: '失败',
    }
    return (
      <span
        className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
          styles[status as keyof typeof styles] || styles.pending
        }`}
      >
        {labels[status as keyof typeof labels] || status}
      </span>
    )
  }

  return (
    <div className="container py-8">
      {/* 页面标题和操作 */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">检测列表</h1>
          <p className="text-muted-foreground mt-2">
            查看和管理所有检测任务
          </p>
        </div>
        <Link
          href="/audits/new"
          className="inline-flex h-10 items-center justify-center rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50"
        >
          创建新检测
        </Link>
      </div>

      {/* 加载状态 */}
      {loading && (
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="rounded-lg border bg-card p-6">
              <div className="flex items-center justify-between">
                <div className="space-y-2 flex-1">
                  <Skeleton className="h-6 w-48" />
                  <Skeleton className="h-4 w-32" />
                </div>
                <Skeleton className="h-8 w-24" />
              </div>
            </div>
          ))}
        </div>
      )}

      {/* 错误状态 */}
      {error && !loading && (
        <NetworkError onRetry={() => window.location.reload()} message={error} />
      )}

      {/* 筛选器 */}
      {!loading && !error && audits.length > 0 && (
        <div className="mb-4 flex items-center gap-2">
          <span className="text-sm font-medium text-muted-foreground">筛选：</span>
          <div className="flex gap-2">
            {(['all', 'pending', 'running', 'completed', 'failed'] as AuditStatus[]).map(
              (status) => (
                <button
                  key={status}
                  onClick={() => setStatusFilter(status)}
                  className={`inline-flex h-9 items-center justify-center rounded-md border px-3 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 ${
                    statusFilter === status
                      ? 'border-primary bg-primary text-primary-foreground shadow-sm'
                      : 'border-input bg-background hover:bg-accent hover:text-accent-foreground'
                  }`}
                >
                  {status === 'all'
                    ? '全部'
                    : status === 'pending'
                      ? '等待中'
                      : status === 'running'
                        ? '进行中'
                        : status === 'completed'
                          ? '已完成'
                          : '失败'}
                </button>
              )
            )}
          </div>
          {statusFilter !== 'all' && (
            <span className="ml-auto text-sm text-muted-foreground">
              已筛选 {filteredAudits.length} 条
            </span>
          )}
        </div>
      )}

      {/* 检测列表 */}
      {!loading && !error && (
        <>
          {filteredAudits.length === 0 ? (
            <div className="rounded-lg border bg-card p-12 text-center">
              <p className="mb-4 text-lg font-medium text-muted-foreground">
                暂无检测记录
              </p>
              <p className="mb-6 text-sm text-muted-foreground">
                创建第一个检测任务开始使用 GEO Agent
              </p>
              <Link
                href="/audits/new"
                className="inline-flex h-10 items-center justify-center rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90"
              >
                创建检测
              </Link>
            </div>
          ) : (
            <>
              {/* 统计信息 */}
              <div className="mb-4 text-sm text-muted-foreground">
                共 {filteredTotal} 个检测任务
                {statusFilter !== 'all' && `（已筛选 ${filteredAudits.length} 条）`}
              </div>

              {/* 列表表格 */}
              <div className="rounded-lg border bg-card">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b bg-muted/50">
                        <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">
                          品牌名称
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">
                          关键词
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">
                          状态
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">
                          GEO Score™
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">
                          创建时间
                        </th>
                        <th className="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-muted-foreground">
                          操作
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {filteredAudits.map((audit) => (
                        <tr
                          key={audit.audit_id}
                          className="hover:bg-muted/50 transition-colors"
                        >
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm font-medium">
                              {audit.brand_name}
                            </div>
                            {audit.target_brand !== audit.brand_name && (
                              <div className="text-xs text-muted-foreground">
                                {audit.target_brand}
                              </div>
                            )}
                          </td>
                          <td className="px-6 py-4">
                            <div className="flex flex-wrap gap-1">
                              {audit.keywords.slice(0, 2).map((keyword, idx) => (
                                <span
                                  key={idx}
                                  className="inline-flex items-center rounded-md bg-muted px-2 py-1 text-xs text-muted-foreground"
                                >
                                  {keyword}
                                </span>
                              ))}
                              {audit.keywords.length > 2 && (
                                <span className="inline-flex items-center rounded-md bg-muted px-2 py-1 text-xs text-muted-foreground">
                                  +{audit.keywords.length - 2}
                                </span>
                              )}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            {getStatusBadge(audit.status)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            {audit.geo_score !== undefined && audit.geo_score !== null ? (
                              <div className="flex items-center space-x-2">
                                <span className="text-sm font-semibold">
                                  {audit.geo_score.toFixed(1)}
                                </span>
                                <div className="h-2 w-16 rounded-full bg-muted">
                                  <div
                                    className="h-2 rounded-full bg-primary"
                                    style={{
                                      width: `${audit.geo_score}%`,
                                    }}
                                  />
                                </div>
                              </div>
                            ) : (
                              <span className="text-sm text-muted-foreground">-</span>
                            )}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">
                            <div>{formatDateTime(audit.started_at)}</div>
                            <div className="text-xs">
                              {formatRelativeTime(audit.started_at)}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <Link
                              href={`/audits/${audit.audit_id}`}
                              className="text-primary hover:text-primary/80 transition-colors"
                            >
                              查看详情 →
                            </Link>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* 分页 */}
              {filteredTotal > 0 && (
                <div className="mt-4 flex items-center justify-between">
                  <div className="text-sm text-muted-foreground">
                    显示 {skip + 1} - {Math.min(skip + limit, filteredAudits.length)} 条，共{' '}
                    {filteredTotal} 条
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setSkip(Math.max(0, skip - limit))}
                      disabled={skip === 0}
                      className="inline-flex h-10 items-center justify-center rounded-md border border-input bg-background px-4 text-sm font-medium shadow-sm transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50"
                    >
                      上一页
                    </button>
                    <button
                      onClick={() => setSkip(skip + limit)}
                      disabled={skip + limit >= filteredAudits.length}
                      className="inline-flex h-10 items-center justify-center rounded-md border border-input bg-background px-4 text-sm font-medium shadow-sm transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50"
                    >
                      下一页
                    </button>
                  </div>
                </div>
              )}
            </>
          )}
        </>
      )}
    </div>
  )
}

