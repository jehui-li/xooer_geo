'use client'

import type { Strategy } from '@/types/api'
import { formatDateTime } from '@/lib/utils/formatters'

interface StrategySummaryProps {
  strategy: Strategy
  className?: string
}

/**
 * 策略摘要展示组件
 * 包含摘要文本和重点关注领域标签
 */
export function StrategySummary({ strategy, className = '' }: StrategySummaryProps) {
  // 获取重点关注领域标签文本和颜色
  const getFocusAreaInfo = (area: string) => {
    const areaMap: Record<string, { label: string; color: string; icon?: string }> = {
      som: {
        label: 'SOM（模型占有率）',
        color: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
        icon: '📊',
      },
      citation: {
        label: 'Citation（权威引文）',
        color: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
        icon: '🔗',
      },
      ranking: {
        label: 'Ranking（排序权重）',
        color: 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-300',
        icon: '📈',
      },
      accuracy: {
        label: 'Accuracy（内容准确度）',
        color: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
        icon: '✓',
      },
      general: {
        label: 'General（综合优化）',
        color: 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300',
        icon: '⚙️',
      },
    }
    return areaMap[area.toLowerCase()] || { label: area, color: areaMap.general.color, icon: '•' }
  }

  return (
    <div className={`rounded-lg border bg-card p-6 ${className}`}>
      {/* 标题 */}
      <div className="mb-4 flex items-center gap-2">
        <h3 className="text-lg font-semibold">策略摘要</h3>
        {strategy.target_score && (
          <span className="text-sm text-muted-foreground">
            （目标分数：{strategy.target_score.toFixed(1)}）
          </span>
        )}
      </div>

      {/* 摘要文本 */}
      {strategy.summary && (
        <div className="mb-4">
          <p className="leading-relaxed text-muted-foreground">{strategy.summary}</p>
        </div>
      )}

      {/* 重点关注领域标签 */}
      {strategy.focus_areas && strategy.focus_areas.length > 0 && (
        <div>
          <h4 className="mb-3 text-sm font-medium text-muted-foreground">重点关注领域：</h4>
          <div className="flex flex-wrap gap-2">
            {strategy.focus_areas.map((area, index) => {
              const areaInfo = getFocusAreaInfo(area)
              return (
                <span
                  key={index}
                  className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-medium ${areaInfo.color}`}
                >
                  {areaInfo.icon && <span>{areaInfo.icon}</span>}
                  <span>{areaInfo.label}</span>
                </span>
              )
            })}
          </div>
        </div>
      )}

      {/* 额外信息（可选） */}
      <div className="mt-4 flex flex-wrap items-center gap-4 border-t pt-4 text-xs text-muted-foreground">
        {strategy.model_used && (
          <div className="flex items-center gap-1.5">
            <span>模型：</span>
            <span className="font-medium">{strategy.model_used}</span>
          </div>
        )}
        {strategy.generated_at && (
          <div className="flex items-center gap-1.5">
            <span>生成时间：</span>
            <span className="font-medium">{formatDateTime(strategy.generated_at)}</span>
          </div>
        )}
      </div>
    </div>
  )
}

