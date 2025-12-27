"""
缓存数据模型
定义 API 响应缓存的数据结构
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class CacheResponse(BaseModel):
    """缓存响应模型"""
    cache_key: str = Field(..., description="缓存键（查询文本 + 模型 + temperature 的 hash）")
    query: str = Field(..., description="查询文本")
    model: str = Field(..., description="模型名称")
    temperature: float = Field(..., description="Temperature 参数")
    content: str = Field(..., description="缓存的响应内容")
    citations: list = Field(default_factory=list, description="引用链接列表")
    usage: Dict[str, int] = Field(default_factory=dict, description="Token 使用情况")
    cached_at: datetime = Field(default_factory=datetime.utcnow, description="缓存时间")
    expires_at: datetime = Field(..., description="过期时间")
    hit_count: int = Field(0, description="命中次数")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="额外元数据")
    
    class Config:
        json_schema_extra = {
            "example": {
                "cache_key": "hash_abc123",
                "query": "What are the best project management software?",
                "model": "gpt-4o",
                "temperature": 0.7,
                "content": "Here are some of the best...",
                "citations": [],
                "usage": {"prompt_tokens": 100, "completion_tokens": 200, "total_tokens": 300},
                "cached_at": "2024-01-01T00:00:00Z",
                "expires_at": "2024-01-02T00:00:00Z",
                "hit_count": 0,
                "metadata": {}
            }
        }

