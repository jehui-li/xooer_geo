'use client'

import { useMemo } from 'react'
import type { StrategyRecommendation } from '@/types/api'
import { StrategyRecommendationCard } from './StrategyRecommendationCard'
import { EmptyStrategyRecommendations } from '@/components/ui/EmptyState'

interface StrategyRecommendationsListProps {
  recommendations: StrategyRecommendation[]
  className?: string
}

/**
 * 策略建议列表组件
 * 卡片列表展示，按优先级排序，显示类别标签
 */
export function StrategyRecommendationsList({
  recommendations,
  className = '',
}: StrategyRecommendationsListProps) {
  // 按优先级排序（high → medium → low）
  const sortedRecommendations = useMemo(() => {
    const priorityOrder = { high: 0, medium: 1, low: 2 }
    return [...recommendations].sort((a, b) => {
      return priorityOrder[a.priority] - priorityOrder[b.priority]
    })
  }, [recommendations])

  if (sortedRecommendations.length === 0) {
    return (
      <div className={className}>
        <EmptyStrategyRecommendations />
      </div>
    )
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {sortedRecommendations.map((recommendation, index) => (
        <StrategyRecommendationCard key={index} recommendation={recommendation} />
      ))}
    </div>
  )
}

