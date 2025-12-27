"""
审计结果数据模型
定义完整的审计报告数据结构
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from src.models.analysis import ProbeResult
from src.models.scoring import GeoScore


class KeywordResult(BaseModel):
    """关键词结果模型（一个关键词在所有模型上的结果）"""
    keyword: str = Field(..., description="关键词")
    probe_results: List[ProbeResult] = Field(default_factory=list, description="所有探针结果")
    total_probes: int = Field(0, description="探针总数")
    total_responses: int = Field(0, description="响应总数")
    mention_rate: float = Field(0.0, ge=0, le=1, description="提及率（0-1）")
    average_ranking: Optional[float] = Field(None, description="平均排名")
    best_ranking: Optional[int] = Field(None, description="最佳排名")
    worst_ranking: Optional[int] = Field(None, description="最差排名")
    models_tested: List[str] = Field(default_factory=list, description="测试的模型列表")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="结果时间戳")
    
    class Config:
        json_schema_extra = {
            "example": {
                "keyword": "project management software",
                "probe_results": [],
                "total_probes": 15,
                "total_responses": 15,
                "mention_rate": 0.8,
                "average_ranking": 2.5,
                "best_ranking": 1,
                "worst_ranking": 5,
                "models_tested": ["gpt-4o", "gemini-1.5-pro"],
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }


class AuditResult(BaseModel):
    """审计结果模型（完整的审计报告）"""
    audit_id: str = Field(..., description="审计 ID（唯一标识）")
    brand_name: str = Field(..., description="品牌名称")
    target_brand: str = Field(..., description="目标品牌（可能与品牌名称不同）")
    keywords: List[str] = Field(default_factory=list, description="测试的关键词列表")
    models: List[str] = Field(default_factory=list, description="测试的模型列表")
    keyword_results: List[KeywordResult] = Field(default_factory=list, description="关键词结果列表")
    geo_score: Optional[GeoScore] = Field(None, description="GEO Score™ 评分")
    status: str = Field("pending", description="审计状态：pending, running, completed, failed")
    started_at: datetime = Field(default_factory=datetime.utcnow, description="开始时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    duration_seconds: Optional[float] = Field(None, description="持续时间（秒）")
    total_api_calls: int = Field(0, description="总 API 调用次数")
    total_cost: Optional[float] = Field(None, description="总成本（美元）")
    error_message: Optional[str] = Field(None, description="错误信息（如果失败）")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="额外元数据")
    
    class Config:
        json_schema_extra = {
            "example": {
                "audit_id": "audit_20240101_001",
                "brand_name": "Asana",
                "target_brand": "Asana",
                "keywords": ["project management software"],
                "models": ["gpt-4o", "gemini-1.5-pro"],
                "keyword_results": [],
                "geo_score": None,
                "status": "completed",
                "started_at": "2024-01-01T00:00:00Z",
                "completed_at": "2024-01-01T00:05:00Z",
                "duration_seconds": 300.0,
                "total_api_calls": 50,
                "total_cost": 5.0,
                "error_message": None,
                "metadata": {}
            }
        }

