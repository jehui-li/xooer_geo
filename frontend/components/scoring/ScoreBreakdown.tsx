'use client'

import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, Cell } from 'recharts'
import type { GeoScore } from '@/types/api'
import { formatPercent } from '@/lib/utils/formatters'

interface ScoreBreakdownProps {
  geoScore: GeoScore
  className?: string
}

/**
 * 评分明细组件
 * 包含四维雷达图、权重显示、柱状图和详细指标表格
 */
export function ScoreBreakdown({ geoScore, className = '' }: ScoreBreakdownProps) {
  const { breakdown, weights } = geoScore

  // 准备雷达图数据
  const radarData = [
    {
      dimension: 'SOM',
      score: breakdown.som_score,
      fullMark: 100,
    },
    {
      dimension: 'Citation',
      score: breakdown.citation_score,
      fullMark: 100,
    },
    {
      dimension: 'Ranking',
      score: breakdown.ranking_score,
      fullMark: 100,
    },
    {
      dimension: 'Accuracy',
      score: breakdown.accuracy_score,
      fullMark: 100,
    },
  ]

  // 准备柱状图数据
  const barData = [
    {
      name: 'SOM',
      score: breakdown.som_score,
      weight: weights.som || 0.4,
      color: '#3b82f6', // blue
    },
    {
      name: 'Citation',
      score: breakdown.citation_score,
      weight: weights.citation || 0.3,
      color: '#10b981', // green
    },
    {
      name: 'Ranking',
      score: breakdown.ranking_score,
      weight: weights.ranking || 0.2,
      color: '#f59e0b', // amber
    },
    {
      name: 'Accuracy',
      score: breakdown.accuracy_score,
      weight: weights.accuracy || 0.1,
      color: '#ef4444', // red
    },
  ]

  // 根据得分获取颜色
  const getScoreColor = (score: number): string => {
    if (score >= 80) return '#10b981' // green
    if (score >= 60) return '#eab308' // yellow
    return '#ef4444' // red
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* 权重显示 */}
      <div className="rounded-lg border bg-card p-6">
        <h3 className="mb-4 text-lg font-semibold">权重配置</h3>
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <div className="flex flex-col items-center rounded-md border p-4">
            <div className="text-2xl font-bold text-blue-600">
              {formatPercent((weights.som || 0.4) * 100)}
            </div>
            <div className="text-sm text-muted-foreground">SOM</div>
          </div>
          <div className="flex flex-col items-center rounded-md border p-4">
            <div className="text-2xl font-bold text-green-600">
              {formatPercent((weights.citation || 0.3) * 100)}
            </div>
            <div className="text-sm text-muted-foreground">Citation</div>
          </div>
          <div className="flex flex-col items-center rounded-md border p-4">
            <div className="text-2xl font-bold text-amber-600">
              {formatPercent((weights.ranking || 0.2) * 100)}
            </div>
            <div className="text-sm text-muted-foreground">Ranking</div>
          </div>
          <div className="flex flex-col items-center rounded-md border p-4">
            <div className="text-2xl font-bold text-red-600">
              {formatPercent((weights.accuracy || 0.1) * 100)}
            </div>
            <div className="text-sm text-muted-foreground">Accuracy</div>
          </div>
        </div>
      </div>

      {/* 雷达图 */}
      <div className="rounded-lg border bg-card p-6">
        <h3 className="mb-4 text-lg font-semibold">四维雷达图</h3>
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
              <Radar
                name="Score"
                dataKey="score"
                stroke="#3b82f6"
                fill="#3b82f6"
                fillOpacity={0.6}
                animationDuration={1500}
                animationEasing="ease-out"
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 柱状图 */}
      <div className="rounded-lg border bg-card p-6">
        <h3 className="mb-4 text-lg font-semibold">各维度得分</h3>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={barData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis
                dataKey="name"
                tick={{ fill: '#6b7280', fontSize: 12 }}
                axisLine={{ stroke: '#e5e7eb' }}
              />
              <YAxis
                domain={[0, 100]}
                tick={{ fill: '#6b7280', fontSize: 12 }}
                axisLine={{ stroke: '#e5e7eb' }}
                label={{ value: 'Score', angle: -90, position: 'insideLeft', fill: '#6b7280' }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#fff',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                }}
                formatter={(value: number) => [`${value.toFixed(1)}`, 'Score']}
              />
              <Legend />
              <Bar
                dataKey="score"
                name="Score"
                radius={[8, 8, 0, 0]}
                animationDuration={1500}
                animationEasing="ease-out"
              >
                {barData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={getScoreColor(entry.score)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 详细指标表格 */}
      <div className="rounded-lg border bg-card p-6">
        <h3 className="mb-4 text-lg font-semibold">详细指标</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b bg-muted/50">
                <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">
                  维度
                </th>
                <th className="px-4 py-3 text-right text-sm font-medium text-muted-foreground">
                  得分
                </th>
                <th className="px-4 py-3 text-right text-sm font-medium text-muted-foreground">
                  权重
                </th>
                <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">
                  详细指标
                </th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {/* SOM 行 */}
              <tr className="hover:bg-muted/50 transition-colors">
                <td className="px-4 py-3 font-medium">SOM (模型占有率)</td>
                <td className="px-4 py-3 text-right">
                  <span className="font-semibold">{breakdown.som_score.toFixed(1)}</span>
                  <span className="text-muted-foreground ml-1">/ 100</span>
                </td>
                <td className="px-4 py-3 text-right text-muted-foreground">
                  {formatPercent((weights.som || 0.4) * 100)}
                </td>
                <td className="px-4 py-3 text-sm text-muted-foreground">
                  出现频率: {breakdown.som_percentage.toFixed(1)}%
                </td>
              </tr>

              {/* Citation 行 */}
              <tr className="hover:bg-muted/50 transition-colors">
                <td className="px-4 py-3 font-medium">Citation (权威引文比)</td>
                <td className="px-4 py-3 text-right">
                  <span className="font-semibold">{breakdown.citation_score.toFixed(1)}</span>
                  <span className="text-muted-foreground ml-1">/ 100</span>
                </td>
                <td className="px-4 py-3 text-right text-muted-foreground">
                  {formatPercent((weights.citation || 0.3) * 100)}
                </td>
                <td className="px-4 py-3 text-sm text-muted-foreground">
                  官网引用: {breakdown.official_citations} | 权威引用:{' '}
                  {breakdown.authoritative_citations}
                </td>
              </tr>

              {/* Ranking 行 */}
              <tr className="hover:bg-muted/50 transition-colors">
                <td className="px-4 py-3 font-medium">Ranking (排序权重)</td>
                <td className="px-4 py-3 text-right">
                  <span className="font-semibold">{breakdown.ranking_score.toFixed(1)}</span>
                  <span className="text-muted-foreground ml-1">/ 100</span>
                </td>
                <td className="px-4 py-3 text-right text-muted-foreground">
                  {formatPercent((weights.ranking || 0.2) * 100)}
                </td>
                <td className="px-4 py-3 text-sm text-muted-foreground">
                  {breakdown.average_ranking !== undefined && breakdown.average_ranking !== null
                    ? `平均排名: ${breakdown.average_ranking.toFixed(1)}`
                    : ''}
                  {breakdown.top3_count > 0 && (
                    <span className="ml-2">| 前3名次数: {breakdown.top3_count}</span>
                  )}
                </td>
              </tr>

              {/* Accuracy 行 */}
              <tr className="hover:bg-muted/50 transition-colors">
                <td className="px-4 py-3 font-medium">Accuracy (内容准确度)</td>
                <td className="px-4 py-3 text-right">
                  <span className="font-semibold">{breakdown.accuracy_score.toFixed(1)}</span>
                  <span className="text-muted-foreground ml-1">/ 100</span>
                </td>
                <td className="px-4 py-3 text-right text-muted-foreground">
                  {formatPercent((weights.accuracy || 0.1) * 100)}
                </td>
                <td className="px-4 py-3 text-sm text-muted-foreground">
                  准确度: {breakdown.accuracy_percentage.toFixed(1)}%
                  {breakdown.hallucination_count > 0 && (
                    <span className="ml-2 text-red-600">
                      | 幻觉数量: {breakdown.hallucination_count}
                    </span>
                  )}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

