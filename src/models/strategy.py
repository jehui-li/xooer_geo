"""
策略建议数据模型
定义策略生成模块的数据结构
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class StrategyRecommendation(BaseModel):
    """策略建议模型"""
    category: str = Field(..., description="建议类别：som, citation, ranking, accuracy, general")
    priority: str = Field("medium", description="优先级：high, medium, low")
    title: str = Field(..., description="建议标题")
    description: str = Field(..., description="建议描述")
    action_items: List[str] = Field(default_factory=list, description="具体行动项")
    expected_impact: str = Field(..., description="预期影响")
    implementation_difficulty: str = Field("medium", description="实施难度：easy, medium, hard")
    estimated_time: Optional[str] = Field(None, description="预计时间")
    code_examples: Optional[Dict[str, str]] = Field(None, description="代码示例（如 JSON-LD）")
    resources: List[str] = Field(default_factory=list, description="相关资源链接")
    
    class Config:
        json_schema_extra = {
            "example": {
                "category": "citation",
                "priority": "high",
                "title": "优化 Schema Markup",
                "description": "添加结构化数据标记以提高引用率",
                "action_items": [
                    "添加 JSON-LD 结构化数据",
                    "优化网站元数据",
                    "提交 sitemap"
                ],
                "expected_impact": "提高 20-30% 的引用得分",
                "implementation_difficulty": "medium",
                "estimated_time": "2-3 小时",
                "code_examples": {
                    "json_ld": '{"@context": "https://schema.org", ...}'
                },
                "resources": ["https://schema.org/docs"]
            }
        }


class Strategy(BaseModel):
    """策略模型（完整的策略报告）"""
    strategy_id: str = Field(..., description="策略 ID")
    audit_id: str = Field(..., description="关联的审计 ID")
    brand_name: str = Field(..., description="品牌名称")
    geo_score: float = Field(..., ge=0, le=100, description="当前 GEO Score™")
    target_score: Optional[float] = Field(None, ge=0, le=100, description="目标 GEO Score™")
    recommendations: List[StrategyRecommendation] = Field(default_factory=list, description="策略建议列表")
    summary: str = Field(..., description="策略摘要")
    focus_areas: List[str] = Field(default_factory=list, description="重点关注领域")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="生成时间")
    model_used: Optional[str] = Field(None, description="生成策略使用的模型")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="额外元数据")
    
    class Config:
        json_schema_extra = {
            "example": {
                "strategy_id": "strategy_20240101_001",
                "audit_id": "audit_20240101_001",
                "brand_name": "Asana",
                "geo_score": 82.5,
                "target_score": 90.0,
                "recommendations": [],
                "summary": "基于当前 GEO Score™ 分析，建议重点关注...",
                "focus_areas": ["citation", "ranking"],
                "generated_at": "2024-01-01T00:00:00Z",
                "model_used": "gpt-4o-128k",
                "metadata": {}
            }
        }

