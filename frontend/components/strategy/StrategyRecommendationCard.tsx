'use client'

import { useState } from 'react'
import { ChevronDown, ChevronUp, ExternalLink } from 'lucide-react'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import type { StrategyRecommendation } from '@/types/api'

interface StrategyRecommendationCardProps {
  recommendation: StrategyRecommendation
  className?: string
}

/**
 * 策略建议卡片组件
 * 包含标题、描述、标签、行动项、预期影响、实施难度、代码示例（可展开）和资源链接
 */
export function StrategyRecommendationCard({
  recommendation,
  className = '',
}: StrategyRecommendationCardProps) {
  const [expandedCodeExamples, setExpandedCodeExamples] = useState<Record<string, boolean>>({})

  // 获取类别标签文本和颜色
  const getCategoryInfo = (category: string) => {
    const categoryMap: Record<string, { label: string; color: string }> = {
      som: {
        label: 'SOM',
        color: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
      },
      citation: {
        label: 'Citation',
        color: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
      },
      ranking: {
        label: 'Ranking',
        color: 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-300',
      },
      accuracy: {
        label: 'Accuracy',
        color: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
      },
      general: {
        label: 'General',
        color: 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300',
      },
    }
    return categoryMap[category] || categoryMap.general
  }

  // 获取优先级标签文本和颜色
  const getPriorityInfo = (priority: string) => {
    const priorityMap: Record<string, { label: string; color: string }> = {
      high: {
        label: '高优先级',
        color: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
      },
      medium: {
        label: '中优先级',
        color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300',
      },
      low: {
        label: '低优先级',
        color: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
      },
    }
    return priorityMap[priority] || priorityMap.medium
  }

  // 获取实施难度标签文本和颜色
  const getDifficultyInfo = (difficulty: string) => {
    const difficultyMap: Record<string, { label: string; color: string }> = {
      easy: {
        label: '简单',
        color: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
      },
      medium: {
        label: '中等',
        color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300',
      },
      hard: {
        label: '困难',
        color: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
      },
    }
    return difficultyMap[difficulty] || difficultyMap.medium
  }

  // 检测代码语言
  const detectLanguage = (key: string, code: string): string => {
    // 根据 key 判断
    if (key.toLowerCase().includes('json') || key.toLowerCase().includes('jsonld')) {
      return 'json'
    }
    if (key.toLowerCase().includes('html')) {
      return 'html'
    }
    if (key.toLowerCase().includes('javascript') || key.toLowerCase().includes('js')) {
      return 'javascript'
    }
    if (key.toLowerCase().includes('typescript') || key.toLowerCase().includes('ts')) {
      return 'typescript'
    }
    if (key.toLowerCase().includes('python') || key.toLowerCase().includes('py')) {
      return 'python'
    }
    if (key.toLowerCase().includes('css')) {
      return 'css'
    }

    // 根据代码内容判断
    if (code.trim().startsWith('{') || code.trim().startsWith('[')) {
      return 'json'
    }
    if (code.trim().startsWith('<')) {
      return 'html'
    }

    return 'text'
  }

  // 切换代码示例展开状态
  const toggleCodeExample = (key: string) => {
    setExpandedCodeExamples((prev) => ({
      ...prev,
      [key]: !prev[key],
    }))
  }

  const categoryInfo = getCategoryInfo(recommendation.category)
  const priorityInfo = getPriorityInfo(recommendation.priority)
  const difficultyInfo = getDifficultyInfo(recommendation.implementation_difficulty)

  const hasCodeExamples =
    recommendation.code_examples && Object.keys(recommendation.code_examples).length > 0
  const hasResources = recommendation.resources && recommendation.resources.length > 0

  return (
    <div
      className={`rounded-lg border bg-card p-6 transition-shadow hover:shadow-md ${className}`}
    >
      {/* 卡片头部：标题和标签 */}
      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="flex-1">
          <h4 className="mb-2 text-lg font-semibold">{recommendation.title}</h4>
          <p className="text-sm text-muted-foreground">{recommendation.description}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          {/* 类别标签 */}
          <span
            className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-medium ${categoryInfo.color}`}
          >
            {categoryInfo.label}
          </span>
          {/* 优先级标签 */}
          <span
            className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-medium ${priorityInfo.color}`}
          >
            {priorityInfo.label}
          </span>
        </div>
      </div>

      {/* 行动项列表 */}
      {recommendation.action_items && recommendation.action_items.length > 0 && (
        <div className="mb-4">
          <h5 className="mb-2 text-sm font-medium text-muted-foreground">具体行动项：</h5>
          <ul className="space-y-1.5">
            {recommendation.action_items.map((item, itemIndex) => (
              <li key={itemIndex} className="flex items-start gap-2 text-sm">
                <span className="mt-1 text-primary">•</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* 预期影响 */}
      {recommendation.expected_impact && (
        <div className="mb-4 rounded-md bg-blue-50 p-3 dark:bg-blue-950">
          <div className="flex items-start gap-2">
            <span className="text-blue-600 dark:text-blue-400">💡</span>
            <div>
              <p className="text-xs font-medium text-blue-900 dark:text-blue-100">预期影响：</p>
              <p className="text-sm text-blue-800 dark:text-blue-200">
                {recommendation.expected_impact}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* 实施难度和时间 */}
      <div className="flex flex-wrap items-center gap-4 border-t pt-4">
        <div className="flex items-center gap-2">
          <span className="text-xs text-muted-foreground">实施难度：</span>
          <span
            className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${difficultyInfo.color}`}
          >
            {difficultyInfo.label}
          </span>
        </div>
        {recommendation.estimated_time && (
          <div className="flex items-center gap-2">
            <span className="text-xs text-muted-foreground">预计时间：</span>
            <span className="text-sm font-medium">{recommendation.estimated_time}</span>
          </div>
        )}
      </div>

      {/* 代码示例（可展开，语法高亮） */}
      {hasCodeExamples && (
        <div className="mt-4 border-t pt-4">
          <h5 className="mb-3 text-sm font-medium text-muted-foreground">代码示例：</h5>
          <div className="space-y-3">
            {Object.entries(recommendation.code_examples!).map(([key, value]) => {
              const isExpanded = expandedCodeExamples[key] ?? false
              const language = detectLanguage(key, value)

              return (
                <div key={key} className="rounded-md border bg-muted/50">
                  {/* 代码示例头部：标题和展开按钮 */}
                  <button
                    type="button"
                    onClick={() => toggleCodeExample(key)}
                    className="flex w-full items-center justify-between rounded-t-md border-b bg-muted/80 px-4 py-2 text-left transition-colors hover:bg-muted"
                  >
                    <span className="text-sm font-medium">{key}</span>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-muted-foreground">{language}</span>
                      {isExpanded ? (
                        <ChevronUp className="h-4 w-4 text-muted-foreground" />
                      ) : (
                        <ChevronDown className="h-4 w-4 text-muted-foreground" />
                      )}
                    </div>
                  </button>

                  {/* 代码内容（可展开） */}
                  {isExpanded && (
                    <div className="overflow-hidden rounded-b-md">
                      <SyntaxHighlighter
                        language={language}
                        style={vscDarkPlus}
                        customStyle={{
                          margin: 0,
                          borderRadius: 0,
                          padding: '1rem',
                          fontSize: '0.875rem',
                        }}
                        showLineNumbers
                        wrapLines
                      >
                        {value}
                      </SyntaxHighlighter>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* 资源链接 */}
      {hasResources && (
        <div className="mt-4 border-t pt-4">
          <h5 className="mb-2 text-sm font-medium text-muted-foreground">相关资源：</h5>
          <ul className="space-y-1.5">
            {recommendation.resources!.map((resource, resourceIndex) => (
              <li key={resourceIndex}>
                <a
                  href={resource}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 text-sm text-primary hover:underline"
                >
                  <span>{resource}</span>
                  <ExternalLink className="h-3.5 w-3.5" />
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

