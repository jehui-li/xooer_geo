'use client'

import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts'

interface GeoScoreOverviewProps {
  score: number
  size?: 'small' | 'medium' | 'large'
  showLabel?: boolean
  className?: string
}

/**
 * GEO Score™ 总览组件
 * 显示大号数字和仪表盘/进度环
 */
export function GeoScoreOverview({
  score,
  size = 'large',
  showLabel = true,
  className = '',
}: GeoScoreOverviewProps) {
  // 确保分数在 0-100 范围内
  const normalizedScore = Math.max(0, Math.min(100, score))

  // 根据分数确定颜色
  const getScoreColor = (score: number): string => {
    if (score >= 80) return '#10b981' // green-500
    if (score >= 60) return '#eab308' // yellow-500
    return '#ef4444' // red-500
  }

  const scoreColor = getScoreColor(normalizedScore)

  // 获取评价文本
  const getScoreLabel = (score: number): string => {
    if (score >= 80) return '优秀'
    if (score >= 60) return '良好'
    if (score >= 40) return '一般'
    return '待改进'
  }

  // 根据尺寸设置样式
  const sizeConfig = {
    small: {
      chartSize: 120,
      fontSize: 'text-2xl',
      numberSize: 'text-3xl',
    },
    medium: {
      chartSize: 180,
      fontSize: 'text-lg',
      numberSize: 'text-4xl',
    },
    large: {
      chartSize: 240,
      fontSize: 'text-base',
      numberSize: 'text-5xl',
    },
  }

  const config = sizeConfig[size]

  // 准备图表数据（使用 Pie Chart 实现进度环）
  // 两个数据点：已完成的部分和剩余的部分
  const chartData = [
    {
      name: 'score',
      value: normalizedScore,
      fill: scoreColor,
    },
    {
      name: 'remaining',
      value: 100 - normalizedScore,
      fill: '#e5e7eb', // gray-200 for background
    },
  ]

  // 计算环形图的半径
  // innerRadius 是内圆半径，outerRadius 是外圆半径
  // 环的宽度 = outerRadius - innerRadius
  const outerRadius = config.chartSize * 0.45 // 外圆半径约为图表尺寸的45%
  const innerRadius = outerRadius * 0.7 // 内圆半径约为外圆半径的70%，形成环状

  return (
    <div className={`flex flex-col items-center ${className}`}>
      {/* 仪表盘图表 */}
      <div className="relative" style={{ width: config.chartSize, height: config.chartSize }}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              innerRadius={innerRadius}
              outerRadius={outerRadius}
              startAngle={90}
              endAngle={-270}
              dataKey="value"
              animationDuration={1500}
              animationEasing="ease-out"
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.fill} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>

        {/* 中心数字显示 */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <div className={`font-bold ${config.numberSize}`} style={{ color: scoreColor }}>
            {normalizedScore.toFixed(1)}
          </div>
          <div className={`${config.fontSize} font-medium text-muted-foreground mt-1`}>
            / 100
          </div>
          {showLabel && (
            <div
              className={`text-xs font-medium mt-2`}
              style={{ color: scoreColor }}
            >
              {getScoreLabel(normalizedScore)}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

