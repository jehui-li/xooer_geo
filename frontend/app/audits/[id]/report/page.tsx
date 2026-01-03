'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { getAudit } from '@/lib/api'
import type { AuditResponse } from '@/types/api'
import { BrandOverview, type BrandOverviewData, CompetitorComparison, type CompetitorComparisonData } from '@/components/reports'
import { AuditDetailSkeleton } from '@/components/ui/Skeleton'
import { AuditNotFoundError, NetworkError } from '@/components/ui/FriendlyError'

/**
 * 品牌 AI 搜索可见度检测报告页面
 */
export default function BrandReportPage() {
  const params = useParams()
  const router = useRouter()
  const auditId = params.id as string

  const [audit, setAudit] = useState<AuditResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [reportData, setReportData] = useState<BrandOverviewData | null>(null)
  const [competitorData, setCompetitorData] = useState<CompetitorComparisonData | null>(null)
  const [polling, setPolling] = useState(false)
  const [activePlatform, setActivePlatform] = useState<string>('ChatGPT')

  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null)

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
        setAudit(data)

        // 如果检测已完成，生成报告数据
        if (data.status === 'completed') {
          // TODO: 从后端API获取报告数据
          // 目前使用模拟数据
          const mockReportData: BrandOverviewData = generateMockReportData(data)
          const mockCompetitorData: CompetitorComparisonData = generateMockCompetitorData(data)
          setReportData(mockReportData)
          setCompetitorData(mockCompetitorData)
          setPolling(false)
          // 清除轮询
          if (pollingIntervalRef.current) {
            clearInterval(pollingIntervalRef.current)
            pollingIntervalRef.current = null
          }
        } else if (data.status === 'running' || data.status === 'pending') {
          // 如果检测还在进行中，显示预览报告（使用模拟数据）
          // 这样用户可以先看到报告结构，同时等待真实数据生成
          if (!reportData) {
            const previewReportData: BrandOverviewData = generateMockReportData(data)
            const previewCompetitorData: CompetitorComparisonData = generateMockCompetitorData(data)
            setReportData(previewReportData)
            setCompetitorData(previewCompetitorData)
          }
          // 继续轮询，等待检测完成
          setPolling(true)
        } else if (data.status === 'failed') {
          setPolling(false)
          if (pollingIntervalRef.current) {
            clearInterval(pollingIntervalRef.current)
            pollingIntervalRef.current = null
          }
        }
      } catch (err: any) {
        if (!silent) {
          if (err?.response?.status === 404) {
            setError('not_found')
          } else if (err?.response?.status === 0 || !err?.response) {
            setError('network')
          } else {
            setError('unknown')
          }
          console.error('Failed to fetch audit:', err)
        }
      } finally {
        if (!silent) {
          setLoading(false)
        }
      }
    },
    [auditId]
  )

  // 初始加载
  useEffect(() => {
    fetchAudit()
  }, [fetchAudit])

  // 轮询检测状态
  useEffect(() => {
    if (polling && !pollingIntervalRef.current) {
      pollingIntervalRef.current = setInterval(() => {
        fetchAudit(true) // 静默获取，不显示加载状态
      }, 3000) // 每3秒轮询一次
    }

    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current)
        pollingIntervalRef.current = null
      }
    }
  }, [polling, fetchAudit])

  // 生成模拟报告数据（待后端API实现后替换）
  function generateMockReportData(audit: AuditResponse): BrandOverviewData {
    const now = new Date()
    const startDate = new Date(now)
    startDate.setDate(startDate.getDate() - 7) // 7天前

    return {
      period: {
        start: startDate.toISOString().split('T')[0],
        end: now.toISOString().split('T')[0],
      },
      metrics: {
        mentionRate: {
          current: 65,
          industryAverage: 58,
          competitorPercentile: 35,
          suggestion: '建议增加品牌曝光度',
        },
        firstMentionRate: {
          current: 42,
          industryAverage: 38,
          competitorPercentile: 40,
          suggestion: '提升品牌知名度',
        },
        firstChoiceRate: {
          current: 35,
          industryAverage: 32,
          competitorPercentile: 45,
          suggestion: '优化产品描述和定位',
        },
        positiveMentionRate: {
          current: 78,
          industryAverage: 72,
          competitorPercentile: 30,
          suggestion: '保持正面形象',
        },
        negativeMentionRate: {
          current: 8,
          industryAverage: 12,
          competitorPercentile: 25,
          suggestion: '负面提及率较低，表现良好',
        },
      },
    }
  }

  // 生成模拟竞品对比数据（待后端API实现后替换）
  function generateMockCompetitorData(audit: AuditResponse): CompetitorComparisonData {
    const now = new Date()
    const startDate = new Date(now)
    startDate.setDate(startDate.getDate() - 7) // 7天前

    const currentBrandName = audit.brand_name || audit.target_brand || '当前品牌'

    return {
      period: {
        start: startDate.toISOString().split('T')[0],
        end: now.toISOString().split('T')[0],
      },
      competitors: [
        {
          name: '速卖通',
          mentionRate: 15.38,
          firstMentionRate: 0,
          firstChoiceRate: 0,
          positiveMentionRate: 100,
          negativeMentionRate: 16.67,
        },
        {
          name: '阿里巴巴国际站',
          mentionRate: 15.38,
          firstMentionRate: 0,
          firstChoiceRate: 0,
          positiveMentionRate: 83.33,
          negativeMentionRate: 16.67,
        },
        {
          name: currentBrandName,
          mentionRate: 2.56,
          firstMentionRate: 0,
          firstChoiceRate: 0,
          positiveMentionRate: 100,
          negativeMentionRate: 0,
          isCurrentBrand: true,
        },
        {
          name: '得物App',
          mentionRate: 2.56,
          firstMentionRate: 2.56,
          firstChoiceRate: 0,
          positiveMentionRate: 100,
          negativeMentionRate: 0,
        },
        {
          name: '一品威客网',
          mentionRate: 2.56,
          firstMentionRate: 0,
          firstChoiceRate: 0,
          positiveMentionRate: 100,
          negativeMentionRate: 0,
        },
        {
          name: '发发奇',
          mentionRate: 2.56,
          firstMentionRate: 0,
          firstChoiceRate: 0,
          positiveMentionRate: 100,
          negativeMentionRate: 0,
        },
        {
          name: '寰免',
          mentionRate: 2.56,
          firstMentionRate: 0,
          firstChoiceRate: 0,
          positiveMentionRate: 100,
          negativeMentionRate: 0,
        },
      ],
    }
  }

  // 加载状态
  if (loading) {
    return (
      <div className="container py-8">
        <AuditDetailSkeleton />
      </div>
    )
  }

  // 错误状态
  if (error === 'not_found') {
    return (
      <div className="container py-8">
        <AuditNotFoundError />
      </div>
    )
  }

  if (error === 'network') {
    return (
      <div className="container py-8">
        <NetworkError />
      </div>
    )
  }

  if (error || !audit) {
    return (
      <div className="container py-8">
        <div className="rounded-lg border border-red-200 bg-red-50 p-6 dark:border-red-800 dark:bg-red-950">
          <h3 className="mb-2 text-lg font-semibold text-red-900 dark:text-red-100">
            获取报告失败
          </h3>
          <p className="text-sm text-red-700 dark:text-red-300">
            {error || '未知错误，请稍后重试'}
          </p>
        </div>
      </div>
    )
  }

  // 如果检测失败
  if (audit.status === 'failed') {
    return (
      <div className="container py-8">
        {/* 页面标题 */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold tracking-tight">品牌 AI 搜索可见度检测报告</h1>
          <p className="text-muted-foreground mt-2">
            品牌：{audit.brand_name || audit.target_brand || '当前品牌'}
          </p>
        </div>

        <div className="rounded-lg border border-red-200 bg-red-50 p-6 dark:border-red-800 dark:bg-red-950">
          <div className="mb-4 flex items-center gap-3">
            <h3 className="text-lg font-semibold text-red-900 dark:text-red-100">
              检测状态：失败
            </h3>
          </div>
          <p className="mb-4 text-sm text-red-700 dark:text-red-300">
            检测执行失败，请稍后重试或联系技术支持
          </p>
          <div className="flex gap-4">
            <Link
              href={`/audits/${auditId}`}
              className="inline-flex h-10 items-center justify-center rounded-md border border-red-300 bg-white px-4 text-sm font-medium text-red-900 shadow-sm transition-colors hover:bg-red-100 dark:border-red-700 dark:bg-red-950 dark:text-red-100 dark:hover:bg-red-900"
            >
              查看检测详情
            </Link>
            <button
              onClick={() => fetchAudit()}
              className="inline-flex h-10 items-center justify-center rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90"
            >
              重新加载
            </button>
          </div>
        </div>
      </div>
    )
  }

  // 如果报告数据未准备好
  if (!reportData) {
    return (
      <div className="container py-8">
        <div className="rounded-lg border border-blue-200 bg-blue-50 p-6 dark:border-blue-800 dark:bg-blue-950">
          <h3 className="mb-2 text-lg font-semibold text-blue-900 dark:text-blue-100">
            报告生成中
          </h3>
          <p className="text-sm text-blue-700 dark:text-blue-300">
            正在生成品牌 AI 搜索可见度检测报告，请稍候...
          </p>
        </div>
      </div>
    )
  }

  // 获取品牌名称
  const brandName = audit.brand_name || audit.target_brand || '当前品牌'

  return (
    <div className="container py-8">
      {/* 页面标题 */}
      <div className="mb-6">
        <div className="mb-2 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">品牌 AI 搜索可见度检测报告</h1>
          </div>
          <Link
            href={`/audits/${auditId}`}
            className="text-sm text-muted-foreground hover:text-foreground"
          >
            返回检测详情
          </Link>
        </div>
      </div>

      {/* 第一部分：品牌概览 */}
      <div className="mb-8">
        <h2 className="mb-4 text-2xl font-semibold">品牌概览</h2>
        <BrandOverview 
          data={reportData} 
          brandName={brandName}
          activePlatform={activePlatform}
          onPlatformChange={setActivePlatform}
        />
      </div>

      {/* 第二部分：竞品对比 */}
      {competitorData && (
        <div className="mb-8">
          <CompetitorComparison 
            data={competitorData}
            currentBrandName={brandName}
          />
        </div>
      )}
    </div>
  )
}

