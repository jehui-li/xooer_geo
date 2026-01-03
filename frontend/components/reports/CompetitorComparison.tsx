'use client'

import { useState, useMemo } from 'react'
import { Info, ChevronDown, Download, Building2 } from 'lucide-react'
import { formatPercent } from '@/lib/utils/formatters'

/**
 * 竞品数据接口
 */
export interface CompetitorData {
  name: string // 竞品名称
  mentionRate: number // 提及率 (0-100)
  firstMentionRate: number // 首位提及率 (0-100)
  firstChoiceRate: number // 首选推荐率 (0-100)
  positiveMentionRate: number // 正面提及率 (0-100)
  negativeMentionRate: number // 负面提及率 (0-100)
  isCurrentBrand?: boolean // 是否为当前品牌
}

/**
 * 竞品对比数据接口
 */
export interface CompetitorComparisonData {
  period: {
    start: string // 格式：YYYY-MM-DD
    end: string // 格式：YYYY-MM-DD
  }
  competitors: CompetitorData[]
}

interface CompetitorComparisonProps {
  data: CompetitorComparisonData
  currentBrandName: string
  className?: string
  onViewDetails?: (competitorName: string) => void
}

type SortField = 'mentionRate' | 'firstMentionRate' | 'firstChoiceRate' | 'positiveMentionRate' | 'negativeMentionRate'
type SortOrder = 'asc' | 'desc' | null

/**
 * 竞品对比组件
 * 显示竞品对比表格，支持排序和导出
 */
export function CompetitorComparison({
  data,
  currentBrandName,
  className = '',
  onViewDetails,
}: CompetitorComparisonProps) {
  const [sortField, setSortField] = useState<SortField | null>(null)
  const [sortOrder, setSortOrder] = useState<SortOrder>(null)

  // 格式化日期
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    }).replace(/\//g, '-')
  }

  // 处理排序
  const handleSort = (field: SortField) => {
    if (sortField === field) {
      // 如果点击同一列，切换排序顺序
      if (sortOrder === 'desc') {
        setSortOrder(null)
        setSortField(null)
      } else if (sortOrder === 'asc') {
        setSortOrder('desc')
      } else {
        setSortOrder('asc')
      }
    } else {
      setSortField(field)
      setSortOrder('desc')
    }
  }

  // 排序后的数据
  const sortedCompetitors = useMemo(() => {
    if (!sortField || !sortOrder) {
      return data.competitors
    }

    return [...data.competitors].sort((a, b) => {
      const aValue = a[sortField]
      const bValue = b[sortField]
      
      if (sortOrder === 'asc') {
        return aValue - bValue
      } else {
        return bValue - aValue
      }
    })
  }, [data.competitors, sortField, sortOrder])

  // 获取排序图标
  const getSortIcon = (field: SortField) => {
    if (sortField !== field) {
      return <ChevronDown className="ml-1 h-3 w-3 text-gray-400" />
    }
    if (sortOrder === 'desc') {
      return <ChevronDown className="ml-1 h-3 w-3 text-red-600" />
    }
    if (sortOrder === 'asc') {
      return <ChevronDown className="ml-1 h-3 w-3 rotate-180 text-red-600" />
    }
    return <ChevronDown className="ml-1 h-3 w-3 text-gray-400" />
  }

  // 导出数据
  const handleExport = () => {
    // TODO: 实现导出功能
    console.log('导出竞品对比数据', sortedCompetitors)
  }

  // 查看详情
  const handleViewDetails = (competitorName: string) => {
    if (onViewDetails) {
      onViewDetails(competitorName)
    } else {
      // TODO: 实现查看详情功能
      console.log('查看详情', competitorName)
    }
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {/* 标题和操作栏 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h3 className="text-lg font-semibold">竞品对比</h3>
          <Info className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm text-muted-foreground">
            统计周期: {formatDate(data.period.start)} 至 {formatDate(data.period.end)}
          </span>
        </div>
        <button
          onClick={handleExport}
          className="inline-flex h-9 items-center justify-center gap-2 rounded-md border border-input bg-background px-4 text-sm font-medium shadow-sm transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50"
        >
          <Download className="h-4 w-4" />
          导出数据
        </button>
      </div>

      {/* 表格 */}
      <div className="rounded-lg border bg-card">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b bg-muted/50">
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">
                  竞品名称
                </th>
                <th
                  className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground cursor-pointer hover:bg-muted/70 transition-colors"
                  onClick={() => handleSort('mentionRate')}
                >
                  <div className="flex items-center">
                    提及率
                    {getSortIcon('mentionRate')}
                  </div>
                </th>
                <th
                  className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground cursor-pointer hover:bg-muted/70 transition-colors"
                  onClick={() => handleSort('firstMentionRate')}
                >
                  <div className="flex items-center">
                    首位提及率
                    {getSortIcon('firstMentionRate')}
                  </div>
                </th>
                <th
                  className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground cursor-pointer hover:bg-muted/70 transition-colors"
                  onClick={() => handleSort('firstChoiceRate')}
                >
                  <div className="flex items-center">
                    首选推荐率
                    {getSortIcon('firstChoiceRate')}
                  </div>
                </th>
                <th
                  className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground cursor-pointer hover:bg-muted/70 transition-colors"
                  onClick={() => handleSort('positiveMentionRate')}
                >
                  <div className="flex items-center">
                    正面提及率
                    {getSortIcon('positiveMentionRate')}
                  </div>
                </th>
                <th
                  className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground cursor-pointer hover:bg-muted/70 transition-colors"
                  onClick={() => handleSort('negativeMentionRate')}
                >
                  <div className="flex items-center">
                    负面提及率
                    {getSortIcon('negativeMentionRate')}
                  </div>
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-muted-foreground">
                  操作
                </th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {sortedCompetitors.map((competitor, index) => {
                const isCurrentBrand = competitor.isCurrentBrand || competitor.name === currentBrandName
                return (
                  <tr
                    key={index}
                    className={`transition-colors hover:bg-muted/50 ${
                      isCurrentBrand ? 'bg-blue-50 dark:bg-blue-950/30' : ''
                    }`}
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        <Building2 className="h-4 w-4 text-muted-foreground" />
                        <span className="text-sm font-medium">
                          {competitor.name}
                          {isCurrentBrand && (
                            <span className="ml-2 text-xs text-blue-600 dark:text-blue-400">(当前品牌)</span>
                          )}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {formatPercent(competitor.mentionRate / 100)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {formatPercent(competitor.firstMentionRate / 100)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {formatPercent(competitor.firstChoiceRate / 100)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {formatPercent(competitor.positiveMentionRate / 100)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {formatPercent(competitor.negativeMentionRate / 100)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                      <button
                        onClick={() => handleViewDetails(competitor.name)}
                        className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                      >
                        查看详情
                      </button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

