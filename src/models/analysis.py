"""
分析结果数据模型
定义品牌提及、情感分析等分析结果的数据结构
"""

from enum import Enum
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from src.models.probe import Citation


class Sentiment(str, Enum):
    """情感标签枚举"""
    POSITIVE = "positive"    # 积极
    NEUTRAL = "neutral"     # 中立
    NEGATIVE = "negative"  # 消极


class BrandMention(BaseModel):
    """品牌提及模型"""
    brand_name: str = Field(..., description="品牌名称")
    is_mentioned: bool = Field(..., description="是否被提及")
    ranking: Optional[int] = Field(None, description="推荐顺序（1-10），如果未提及则为 None")
    sentiment: Optional[Sentiment] = Field(None, description="情感标签")
    mention_text: Optional[str] = Field(None, description="提及的文本片段")
    citations: List[Citation] = Field(default_factory=list, description="相关的引用链接")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="提取的产品属性（价格、功能等）")
    accuracy_score: Optional[float] = Field(None, ge=0, le=1, description="内容准确度评分（0-1）")
    hallucination_risk: bool = Field(False, description="是否存在幻觉风险（错误信息）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "brand_name": "Asana",
                "is_mentioned": True,
                "ranking": 1,
                "sentiment": "positive",
                "mention_text": "Asana is one of the best project management tools...",
                "citations": [],
                "attributes": {"price": "$10.99/month", "features": ["task management", "collaboration"]},
                "accuracy_score": 0.95,
                "hallucination_risk": False
            }
        }


class ProbeResult(BaseModel):
    """探针结果模型（单个探针的分析结果）"""
    probe_id: str = Field(..., description="探针 ID")
    probe_type: str = Field(..., description="探针类型")
    keyword: str = Field(..., description="关键词")
    model: str = Field(..., description="模型名称")
    temperature: float = Field(..., description="Temperature 参数")
    brand_mentions: List[BrandMention] = Field(default_factory=list, description="品牌提及列表")
    total_mentions: int = Field(0, description="总提及次数")
    has_target_brand: bool = Field(False, description="是否包含目标品牌")
    target_brand_ranking: Optional[int] = Field(None, description="目标品牌排名")
    target_brand_sentiment: Optional[Sentiment] = Field(None, description="目标品牌情感")
    official_citations_count: int = Field(0, description="官网引用数量")
    authoritative_citations_count: int = Field(0, description="权威来源引用数量")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="分析时间戳")
    
    class Config:
        json_schema_extra = {
            "example": {
                "probe_id": "probe_001",
                "probe_type": "direct_recommendation",
                "keyword": "project management software",
                "model": "gpt-4o",
                "temperature": 0.7,
                "brand_mentions": [],
                "total_mentions": 5,
                "has_target_brand": True,
                "target_brand_ranking": 1,
                "target_brand_sentiment": "positive",
                "official_citations_count": 1,
                "authoritative_citations_count": 2,
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }

