"""
评分相关数据模型
定义 GEO Score™ 评分的数据结构
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class ScoreBreakdown(BaseModel):
    """评分细分明细"""
    som_score: float = Field(..., ge=0, le=100, description="SOM（模型占有率）得分 0-100")
    som_percentage: float = Field(..., ge=0, le=100, description="SOM 百分比（出现频率）")
    citation_score: float = Field(..., ge=0, le=100, description="权威引文比得分 0-100")
    official_citations: int = Field(0, description="官网引用数量")
    authoritative_citations: int = Field(0, description="权威来源引用数量")
    ranking_score: float = Field(..., ge=0, le=100, description="排序权重得分 0-100")
    average_ranking: Optional[float] = Field(None, description="平均排名")
    top3_count: int = Field(0, description="进入前三名的次数")
    accuracy_score: float = Field(..., ge=0, le=100, description="内容准确度得分 0-100")
    accuracy_percentage: float = Field(..., ge=0, le=100, description="准确度百分比")
    hallucination_count: int = Field(0, description="幻觉（错误信息）数量")
    
    class Config:
        json_schema_extra = {
            "example": {
                "som_score": 85.0,
                "som_percentage": 85.0,
                "citation_score": 75.0,
                "official_citations": 10,
                "authoritative_citations": 5,
                "ranking_score": 80.0,
                "average_ranking": 2.5,
                "top3_count": 8,
                "accuracy_score": 90.0,
                "accuracy_percentage": 90.0,
                "hallucination_count": 1
            }
        }


class GeoScore(BaseModel):
    """GEO Score™ 评分模型"""
    overall_score: float = Field(..., ge=0, le=100, description="总体 GEO Score™（0-100）")
    breakdown: ScoreBreakdown = Field(..., description="评分明细")
    weights: Dict[str, float] = Field(default_factory=dict, description="权重配置")
    confidence_interval: Optional[Dict[str, float]] = Field(None, description="置信区间")
    test_count: int = Field(..., description="测试总次数")
    models_tested: list = Field(default_factory=list, description="测试的模型列表")
    keywords_tested: list = Field(default_factory=list, description="测试的关键词列表")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="评分时间戳")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="额外元数据")
    
    class Config:
        json_schema_extra = {
            "example": {
                "overall_score": 82.5,
                "breakdown": {},
                "weights": {
                    "som": 0.4,
                    "citation": 0.3,
                    "ranking": 0.2,
                    "accuracy": 0.1
                },
                "confidence_interval": {"lower": 80.0, "upper": 85.0},
                "test_count": 50,
                "models_tested": ["gpt-4o", "gemini-1.5-pro"],
                "keywords_tested": ["project management software"],
                "timestamp": "2024-01-01T00:00:00Z",
                "metadata": {}
            }
        }

