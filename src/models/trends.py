"""
历史趋势数据模型
定义历史趋势分析的数据结构
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class HistoricalTrend(BaseModel):
    """历史趋势数据模型"""
    brand_name: str = Field(..., description="品牌名称")
    keyword: str = Field(..., description="关键词")
    date: datetime = Field(..., description="日期")
    geo_score: float = Field(..., ge=0, le=100, description="GEO Score™")
    som_percentage: float = Field(..., ge=0, le=100, description="SOM 百分比")
    citation_score: float = Field(..., ge=0, le=100, description="引文得分")
    ranking_score: float = Field(..., ge=0, le=100, description="排序得分")
    accuracy_score: float = Field(..., ge=0, le=100, description="准确度得分")
    average_ranking: Optional[float] = Field(None, description="平均排名")
    mention_count: int = Field(0, description="提及次数")
    total_tests: int = Field(0, description="总测试次数")
    models_tested: List[str] = Field(default_factory=list, description="测试的模型列表")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="额外元数据")
    
    class Config:
        json_schema_extra = {
            "example": {
                "brand_name": "Asana",
                "keyword": "project management software",
                "date": "2024-01-01T00:00:00Z",
                "geo_score": 82.5,
                "som_percentage": 85.0,
                "citation_score": 75.0,
                "ranking_score": 80.0,
                "accuracy_score": 90.0,
                "average_ranking": 2.5,
                "mention_count": 40,
                "total_tests": 50,
                "models_tested": ["gpt-4o", "gemini-1.5-pro"],
                "metadata": {}
            }
        }

