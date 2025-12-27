'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { getAudit } from '@/lib/api'
import type { AuditResponse } from '@/types/api'
import { formatDateTime, formatRelativeTime } from '@/lib/utils/formatters'
import { GeoScoreOverview, ScoreBreakdown } from '@/components/scoring'
import { StrategyRecommendationsList, StrategySummary } from '@/components/strategy'
import { useToast } from '@/hooks/useToast'
import { ToastContainer } from '@/components/ui/Toast'
import { AuditDetailSkeleton } from '@/components/ui/Skeleton'
import { AuditNotFoundError, NetworkError } from '@/components/ui/FriendlyError'
import { EmptyScoreData } from '@/components/ui/EmptyState'
import { ErrorBoundary } from '@/components/ui/ErrorBoundary'

/**
 * 检测详情页
 */
function AuditDetailPageContent() {
  const params = useParams()
  const router = useRouter()
  const auditId = params.id as string

  const [audit, setAudit] = useState<AuditResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [polling, setPolling] = useState(false)

  const previousStatusRef = useRef<string | null>(null)
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null)

  const { toasts, removeToast, success, info } = useToast()

  // 获取检测详情
  const fetchAudit = useCallback(
    async (silent = false) => {
      if (!auditId) return

      try {
        if (!silent) {
          setLoading(true)
        }
        setError(null)
        const data = await getAudit(auditId)
        
        // 调试：打印获取到的数据
        if (process.env.NODE_ENV === 'development') {
          console.log('Fetched audit data:', {
            audit_id: data.audit_id,
            started_at: data.started_at,
            status: data.status
          })
        }

        // 检测状态变更
        if (previousStatusRef.current && previousStatusRef.current !== data.status) {
          const statusMessages: Record<string, string> = {
            pending: '检测任务已开始',
            running: '检测正在执行中',
            completed: '检测已完成！',
            failed: '检测执行失败',
          }
          const message = statusMessages[data.status] || `状态已变更为：${data.status}`

          if (data.status === 'completed') {
            success(message, 6000)
          } else if (data.status === 'failed') {
            info(message, 6000)
          } else {
            info(message, 4000)
          }
        }

        previousStatusRef.current = data.status
        setAudit(data)

        // 如果状态为 running 或 pending，继续轮询
        if (data.status === 'running' || data.status === 'pending') {
          setPolling(true)
        } else {
          setPolling(false)
        }
      } catch (err) {
        if (!silent) {
          setError('获取检测详情失败，请稍后重试')
          console.error('Failed to fetch audit:', err)
        }
      } finally {
        if (!silent) {
          setLoading(false)
        }
      }
    },
    [auditId, success, info]
  )

  // 初始加载
  useEffect(() => {
    if (auditId) {
      // 重置状态，确保获取最新数据
      setAudit(null)
      fetchAudit()
    }
  }, [auditId, fetchAudit])

  // 轮询机制
  useEffect(() => {
    if (!polling || !auditId) {
      // 停止轮询
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current)
        pollingIntervalRef.current = null
      }
      return
    }

    // 每 7 秒轮询一次（在 5-10 秒之间）
    pollingIntervalRef.current = setInterval(() => {
      fetchAudit(true) // silent mode，不显示 loading
    }, 7000)

    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current)
        pollingIntervalRef.current = null
      }
    }
  }, [polling, auditId, fetchAudit])

  // 状态标签
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
        className={`inline-flex items-center rounded-full px-3 py-1 text-sm font-medium ${
          styles[status as keyof typeof styles] || styles.pending
        }`}
      >
        {labels[status as keyof typeof labels] || status}
      </span>
    )
  }

  // 加载状态
  if (loading) {
    return (
      <>
        <AuditDetailSkeleton />
        <ToastContainer toasts={toasts} onClose={removeToast} />
      </>
    )
  }

  // 错误状态
  if (error || !audit) {
    const handleRetry = () => {
      setError(null)
      if (auditId) {
        fetchAudit()
      }
    }

    return (
      <>
        <div className="container py-8">
          <div className="mb-6">
            <Link
              href="/audits"
              className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              ← 返回列表
            </Link>
          </div>
          
          {error && error.includes('网络') ? (
            <NetworkError onRetry={handleRetry} message={error} />
          ) : (
            <AuditNotFoundError auditId={auditId} onRetry={handleRetry} />
          )}
        </div>
        <ToastContainer toasts={toasts} onClose={removeToast} />
      </>
    )
  }

  return (
    <div className="container py-8">
      {/* 返回按钮和操作 */}
      <div className="mb-6 flex items-center justify-between">
        <Link
          href="/audits"
          className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          ← 返回列表
        </Link>
        <div className="flex gap-2">
          {/* 可以添加更多操作按钮 */}
        </div>
      </div>

      {/* 页面标题 */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">{audit.brand_name}</h1>
            {audit.target_brand !== audit.brand_name && (
              <p className="mt-1 text-lg text-muted-foreground">
                目标品牌：{audit.target_brand}
              </p>
            )}
          </div>
          <div>{getStatusBadge(audit.status)}</div>
        </div>
        <p className="mt-2 text-sm text-muted-foreground">
          检测 ID: {audit.audit_id}
        </p>
      </div>

      {/* 基本信息卡片 */}
      <div className="mb-6 rounded-lg border bg-card">
        <div className="border-b p-6">
          <h2 className="text-xl font-semibold">基本信息</h2>
        </div>
        <div className="grid gap-6 p-6 sm:grid-cols-2">
          {/* 品牌信息 */}
          <div>
            <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-muted-foreground">
              品牌信息
            </h3>
            <dl className="space-y-2">
              <div>
                <dt className="text-xs font-medium text-muted-foreground">品牌名称</dt>
                <dd className="mt-1 text-base font-medium">{audit.brand_name}</dd>
              </div>
              {audit.target_brand !== audit.brand_name && (
                <div>
                  <dt className="text-xs font-medium text-muted-foreground">目标品牌</dt>
                  <dd className="mt-1 text-base font-medium">{audit.target_brand}</dd>
                </div>
              )}
              <div>
                <dt className="text-xs font-medium text-muted-foreground">检测 ID</dt>
                <dd className="mt-1 font-mono text-sm text-muted-foreground">{audit.audit_id}</dd>
              </div>
            </dl>
          </div>

          {/* 状态和时间 */}
          <div>
            <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-muted-foreground">
              状态与时间
            </h3>
            <dl className="space-y-2">
              <div>
                <dt className="text-xs font-medium text-muted-foreground">状态</dt>
                <dd className="mt-1">{getStatusBadge(audit.status)}</dd>
              </div>
              <div>
                <dt className="text-xs font-medium text-muted-foreground">开始时间</dt>
                <dd className="mt-1 text-sm">
                  <div>{formatDateTime(audit.started_at)}</div>
                  <div className="text-xs text-muted-foreground">
                    {formatRelativeTime(audit.started_at)}
                  </div>
                </dd>
              </div>
              {audit.completed_at && (
                <div>
                  <dt className="text-xs font-medium text-muted-foreground">完成时间</dt>
                  <dd className="mt-1 text-sm">
                    <div>{formatDateTime(audit.completed_at)}</div>
                    <div className="text-xs text-muted-foreground">
                      {formatRelativeTime(audit.completed_at)}
                    </div>
                  </dd>
                </div>
              )}
            </dl>
          </div>
        </div>
      </div>

      {/* 关键词卡片 */}
      <div className="mb-6 rounded-lg border bg-card p-6">
        <h3 className="mb-4 text-sm font-semibold uppercase tracking-wide text-muted-foreground">
          关键词
        </h3>
        {audit.keywords.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {audit.keywords.map((keyword, idx) => (
              <span
                key={idx}
                className="inline-flex items-center rounded-md bg-primary/10 px-3 py-1.5 text-sm font-medium text-primary"
              >
                {keyword}
              </span>
            ))}
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">暂无关键词</p>
        )}
      </div>

      {/* GEO Score™ 总览和明细 */}
      {audit.status === 'completed' && audit.geo_score !== undefined && audit.geo_score !== null ? (
        <>
          {/* GEO Score™ 总览 */}
          <div className="mb-6 rounded-lg border bg-card p-6">
            <div className="mb-6 flex items-center justify-between">
              <h3 className="text-lg font-semibold">GEO Score™ 总览</h3>
            </div>
            <div className="flex justify-center">
              <GeoScoreOverview score={audit.geo_score} size="large" showLabel={true} />
            </div>
          </div>

          {/* 评分明细（如果有完整数据） */}
          {audit.geo_score_detail ? (
            <div className="mb-6 rounded-lg border bg-card p-6">
              <div className="mb-6 flex items-center justify-between">
                <h3 className="text-lg font-semibold">评分明细</h3>
              </div>
              <ScoreBreakdown geoScore={audit.geo_score_detail} />
            </div>
          ) : (
            <div className="mb-6">
              <EmptyScoreData />
            </div>
          )}
        </>
      ) : audit.status === 'completed' ? (
        <div className="mb-6 rounded-lg border border-yellow-200 bg-yellow-50 p-6 dark:border-yellow-800 dark:bg-yellow-950">
          <div className="flex items-start gap-4">
            <div className="text-2xl">⚠️</div>
            <div className="flex-1">
              <h4 className="mb-2 text-sm font-medium text-yellow-800 dark:text-yellow-200">
                暂无评分数据
              </h4>
              <p className="text-sm text-yellow-700 dark:text-yellow-300">
                检测已完成，但未生成评分数据。可能是检测过程中出现了错误。
              </p>
            </div>
          </div>
        </div>
      ) : null}

      {/* 错误信息 */}
      {audit.error && (
        <div className="mb-6 rounded-lg border border-red-200 bg-red-50 p-6 dark:border-red-800 dark:bg-red-950">
          <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-red-800 dark:text-red-200">
            错误信息
          </h3>
          <p className="text-sm text-red-800 dark:text-red-200">{audit.error}</p>
        </div>
      )}

      {/* 操作提示 */}
      {audit.status === 'running' && (
        <div className="mb-6 rounded-lg border border-blue-200 bg-blue-50 p-4 dark:border-blue-800 dark:bg-blue-950">
          <div className="flex items-start gap-3">
            <div className="text-xl">⏳</div>
            <div className="flex-1">
              <p className="mb-1 text-sm font-medium text-blue-800 dark:text-blue-200">
                检测正在进行中
              </p>
              <p className="text-sm text-blue-700 dark:text-blue-300">
                请稍后刷新页面查看结果。检测完成后将显示 GEO Score™ 评分和详细分析。
              </p>
            </div>
          </div>
        </div>
      )}

      {audit.status === 'pending' && (
        <div className="mb-6 rounded-lg border border-yellow-200 bg-yellow-50 p-4 dark:border-yellow-800 dark:bg-yellow-950">
          <div className="flex items-start gap-3">
            <div className="text-xl">⏸️</div>
            <div className="flex-1">
              <p className="mb-1 text-sm font-medium text-yellow-800 dark:text-yellow-200">
                检测任务已创建，等待执行
              </p>
              <p className="text-sm text-yellow-700 dark:text-yellow-300">
                检测任务已在队列中，即将开始执行。执行完成后将显示评分结果。
              </p>
            </div>
          </div>
        </div>
      )}

      {/* 策略建议 */}
      {audit.status === 'completed' && audit.strategy && (
        <div className="mb-6 space-y-4">
          {/* 策略摘要（如果有摘要或重点关注领域） */}
          {(audit.strategy.summary ||
            (audit.strategy.focus_areas && audit.strategy.focus_areas.length > 0)) && (
            <StrategySummary strategy={audit.strategy} />
          )}

          {/* 策略建议列表 */}
          {audit.strategy.recommendations && audit.strategy.recommendations.length > 0 && (
            <div className="rounded-lg border bg-card p-6">
              <h3 className="mb-6 text-lg font-semibold">策略建议</h3>
              <StrategyRecommendationsList recommendations={audit.strategy.recommendations} />
            </div>
          )}
        </div>
      )}

      {/* 后续可添加的内容 */}
      {/* - 原始数据展示 */}
      {/* - 历史趋势 */}

      {/* Toast 通知容器 */}
      <ToastContainer toasts={toasts} onClose={removeToast} />

      {/* 轮询状态指示器（仅在轮询时显示） */}
      {polling && audit && (
        <div className="fixed bottom-4 left-4 z-40 flex items-center gap-2 rounded-full bg-blue-600 px-4 py-2 text-sm text-white shadow-lg">
          <div className="h-2 w-2 animate-pulse rounded-full bg-white" />
          <span>实时更新中...</span>
        </div>
      )}
    </div>
  )
}

/**
 * 检测详情页（带错误边界）
 */
export default function AuditDetailPage() {
  return (
    <ErrorBoundary>
      <AuditDetailPageContent />
    </ErrorBoundary>
  )
}

