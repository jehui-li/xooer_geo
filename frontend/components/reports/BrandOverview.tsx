'use client'

import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer, Legend } from 'recharts'
import { formatPercent } from '@/lib/utils/formatters'

/**
 * 品牌概览数据接口
 */
export interface BrandOverviewData {
  // 统计周期
  period: {
    start: string // 格式：YYYY-MM-DD
    end: string // 格式：YYYY-MM-DD
  }
  // 五个维度的数据
  metrics: {
    // 提及率
    mentionRate: {
      current: number // 当前品牌的值（0-100）
      industryAverage: number // 行业平均值（0-100）
      competitorPercentile: number // 低于多少比例的竞品（0-100）
      suggestion?: string // 优化建议
    }
    // 首位提及率
    firstMentionRate: {
      current: number
      industryAverage: number
      competitorPercentile: number
      suggestion?: string
    }
    // 首选推荐率
    firstChoiceRate: {
      current: number
      industryAverage: number
      competitorPercentile: number
      suggestion?: string
    }
    // 正面提及率
    positiveMentionRate: {
      current: number
      industryAverage: number
      competitorPercentile: number
      suggestion?: string
    }
    // 负面提及率
    negativeMentionRate: {
      current: number
      industryAverage: number
      competitorPercentile: number
      suggestion?: string
    }
  }
}

interface BrandOverviewProps {
  data: BrandOverviewData
  brandName: string
  className?: string
  activePlatform?: string
  onPlatformChange?: (platform: string) => void
}

/**
 * 品牌概览组件
 * 显示统计周期、五边形雷达图和数据详情
 */
export function BrandOverview({ 
  data, 
  brandName, 
  className = '',
  activePlatform = 'ChatGPT',
  onPlatformChange
}: BrandOverviewProps) {
  // 准备雷达图数据
  const radarData = [
    {
      dimension: '提及率',
      current: data.metrics.mentionRate.current,
      industryAverage: data.metrics.mentionRate.industryAverage,
    },
    {
      dimension: '首位提及率',
      current: data.metrics.firstMentionRate.current,
      industryAverage: data.metrics.firstMentionRate.industryAverage,
    },
    {
      dimension: '首选推荐率',
      current: data.metrics.firstChoiceRate.current,
      industryAverage: data.metrics.firstChoiceRate.industryAverage,
    },
    {
      dimension: '正面提及率',
      current: data.metrics.positiveMentionRate.current,
      industryAverage: data.metrics.positiveMentionRate.industryAverage,
    },
    {
      dimension: '负面提及率',
      current: data.metrics.negativeMentionRate.current,
      industryAverage: data.metrics.negativeMentionRate.industryAverage,
    },
  ]

  // 格式化日期
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    })
  }

  // 获取指标卡片数据
  const metricCards = [
    {
      label: '提及率',
      data: data.metrics.mentionRate,
    },
    {
      label: '首位提及率',
      data: data.metrics.firstMentionRate,
    },
    {
      label: '首选推荐率',
      data: data.metrics.firstChoiceRate,
    },
    {
      label: '正面提及率',
      data: data.metrics.positiveMentionRate,
    },
    {
      label: '负面提及率',
      data: data.metrics.negativeMentionRate,
    },
  ]

  return (
    <div className={`space-y-6 ${className}`}>
      {/* 统计周期 */}
      <div className="rounded-lg border bg-card p-4">
        <div className="flex items-center justify-between">
          <div className="text-sm font-medium text-muted-foreground">
            统计周期：{formatDate(data.period.start)} 至 {formatDate(data.period.end)}
          </div>
          <button
            onClick={() => {
              // TODO: 实现导出报告功能
              console.log('导出报告')
            }}
            className="inline-flex h-9 items-center justify-center rounded-md border border-input bg-background px-4 text-sm font-medium shadow-sm transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50"
          >
            导出报告
          </button>
        </div>
      </div>

      {/* AI平台导航标签栏 */}
      {onPlatformChange && (
        <div className="border-b border-border">
          <div className="flex gap-8">
            {['ChatGPT', '豆包', 'Gemini', '通义', 'grok', 'Perplexity'].map((platform) => (
              <button
                key={platform}
                onClick={() => onPlatformChange(platform)}
                className={`pb-3 text-sm font-medium transition-colors ${
                  activePlatform === platform
                    ? 'border-b-2 border-blue-600 text-blue-600 dark:border-blue-400 dark:text-blue-400'
                    : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
                }`}
              >
                {platform}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* 品牌概览内容：左侧雷达图 + 右侧数据 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 左侧：雷达图 */}
        <div className="rounded-lg border bg-card p-6">
          <h3 className="mb-4 text-lg font-semibold">品牌对比雷达图</h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={radarData}>
                <PolarGrid stroke="#e5e7eb" />
                <PolarAngleAxis
                  dataKey="dimension"
                  tick={{ fill: '#6b7280', fontSize: 12 }}
                />
                <PolarRadiusAxis
                  angle={90}
                  domain={[0, 100]}
                  tick={{ fill: '#9ca3af', fontSize: 10 }}
                />
                {/* 当前品牌（蓝色） */}
                <Radar
                  name={`${brandName} (当前品牌)`}
                  dataKey="current"
                  stroke="#3b82f6"
                  fill="#3b82f6"
                  fillOpacity={0.6}
                  animationDuration={1500}
                  animationEasing="ease-out"
                />
                {/* 行业平均（红色） */}
                <Radar
                  name="行业平均"
                  dataKey="industryAverage"
                  stroke="#ef4444"
                  fill="#ef4444"
                  fillOpacity={0.3}
                  animationDuration={1500}
                  animationEasing="ease-out"
                />
                <Legend />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 右侧：数据详情 */}
        <div className="rounded-lg border bg-card p-6">
          <h3 className="mb-4 text-lg font-semibold">维度数据详情</h3>
          <div className="space-y-4">
            {metricCards.map((metric, index) => {
              const { label, data: metricData } = metric
              const isPositive = label.includes('正面') || (!label.includes('负面') && label !== '负面提及率')
              const isBetter = isPositive
                ? metricData.current >= metricData.industryAverage
                : metricData.current <= metricData.industryAverage

              return (
                <div
                  key={index}
                  className="rounded-md border bg-background p-4 space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">{label}</span>
                    <span className="text-sm font-semibold">
                      {formatPercent(metricData.current / 100)}
                    </span>
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {isBetter ? (
                      <span className="text-green-600 dark:text-green-400">
                        高于行业平均 {formatPercent(metricData.industryAverage / 100)}
                      </span>
                    ) : (
                      <span className="text-orange-600 dark:text-orange-400">
                        低于行业平均 {formatPercent(metricData.industryAverage / 100)}
                      </span>
                    )}
                    {metricData.competitorPercentile > 0 && (
                      <span className="ml-2">
                        ，低于 {formatPercent(metricData.competitorPercentile / 100)} 的竞品
                      </span>
                    )}
                    {metricData.suggestion && (
                      <div className="mt-1 text-blue-600 dark:text-blue-400">
                        （{metricData.suggestion}）
                      </div>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}

