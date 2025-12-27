// API 响应类型定义

export interface AuditRequest {
  brand_name: string
  target_brand: string
  keywords: string[]
  target_website?: string
  ground_truth?: Record<string, any>
}

export interface AuditResponse {
  audit_id: string
  brand_name: string
  target_brand: string
  keywords: string[]
  status: 'pending' | 'running' | 'completed' | 'failed'
  geo_score?: number
  geo_score_detail?: GeoScore
  strategy?: Strategy
  started_at: string
  completed_at?: string
  error?: string
}

export interface AuditListResponse {
  audits: AuditResponse[]
  total: number
}

export interface ScoreBreakdown {
  som_score: number
  som_percentage: number
  citation_score: number
  official_citations: number
  authoritative_citations: number
  ranking_score: number
  average_ranking?: number
  top3_count: number
  accuracy_score: number
  accuracy_percentage: number
  hallucination_count: number
}

export interface GeoScore {
  overall_score: number
  breakdown: ScoreBreakdown
  weights: {
    som: number
    citation: number
    ranking: number
    accuracy: number
  }
  confidence_interval?: {
    lower: number
    upper: number
  }
  test_count: number
  models_tested: string[]
  keywords_tested: string[]
  timestamp: string
  metadata?: Record<string, any>
}

export interface StrategyRecommendation {
  category: 'som' | 'citation' | 'ranking' | 'accuracy' | 'general'
  priority: 'high' | 'medium' | 'low'
  title: string
  description: string
  action_items: string[]
  expected_impact: string
  implementation_difficulty: 'easy' | 'medium' | 'hard'
  estimated_time?: string
  code_examples?: Record<string, string>
  resources?: string[]
}

export interface Strategy {
  strategy_id: string
  audit_id: string
  brand_name: string
  geo_score: number
  target_score?: number
  recommendations: StrategyRecommendation[]
  summary: string
  focus_areas: string[]
  generated_at: string
  model_used?: string
  metadata?: Record<string, any>
}

export interface ErrorResponse {
  error: string
  detail?: string
}

