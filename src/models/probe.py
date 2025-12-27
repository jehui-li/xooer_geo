"""
探针相关数据模型
定义探针类型和探针响应的数据结构
"""

from enum import Enum
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ProbeType(str, Enum):
    """探针类型枚举"""
    DIRECT_RECOMMENDATION = "direct_recommendation"  # 直接推荐类
    ATTRIBUTE_COMPARISON = "attribute_comparison"    # 属性对比类
    SOLUTION_BASED = "solution_based"                # 解决方案类


class Citation(BaseModel):
    """引用链接模型"""
    url: str = Field(..., description="引用链接 URL")
    title: Optional[str] = Field(None, description="链接标题")
    text: Optional[str] = Field(None, description="引用文本片段")
    citation_type: str = Field("unknown", description="引用类型：official, authoritative, third_party, unknown")
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com/product",
                "title": "Product Page",
                "text": "This is a great product...",
                "citation_type": "official"
            }
        }


class ProbeResponse(BaseModel):
    """探针响应模型（原始 LLM 响应）"""
    probe_id: str = Field(..., description="探针 ID")
    probe_type: ProbeType = Field(..., description="探针类型")
    keyword: str = Field(..., description="关键词")
    model: str = Field(..., description="模型名称（如 gpt-4o, gemini-1.5-pro）")
    query: str = Field(..., description="查询文本")
    temperature: float = Field(..., description="Temperature 参数")
    content: str = Field(..., description="LLM 返回的原始内容")
    citations: List[Citation] = Field(default_factory=list, description="引用链接列表")
    usage: Dict[str, int] = Field(default_factory=dict, description="Token 使用情况")
    response_time_ms: Optional[int] = Field(None, description="响应时间（毫秒）")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="响应时间戳")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="额外元数据")
    
    class Config:
        json_schema_extra = {
            "example": {
                "probe_id": "probe_001",
                "probe_type": "direct_recommendation",
                "keyword": "project management software",
                "model": "gpt-4o",
                "query": "What are the best project management software currently on the market?",
                "temperature": 0.7,
                "content": "Here are some of the best project management software...",
                "citations": [],
                "usage": {"prompt_tokens": 100, "completion_tokens": 200, "total_tokens": 300},
                "response_time_ms": 1500,
                "timestamp": "2024-01-01T00:00:00Z",
                "metadata": {}
            }
        }

