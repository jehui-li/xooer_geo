"""
API 请求和响应模型
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class AuditRequest(BaseModel):
    """创建审计请求"""
    brand_name: str = Field(..., description="品牌名称")
    target_brand: str = Field(..., description="目标品牌名称")
    keywords: List[str] = Field(..., description="关键词列表", min_items=1)
    target_website: Optional[str] = Field(None, description="目标品牌官网 URL")
    ground_truth: Optional[Dict[str, Any]] = Field(None, description="品牌真实数据（用于准确度检查）")


class AuditResponse(BaseModel):
    """审计响应"""
    audit_id: str = Field(..., description="审计 ID")
    brand_name: str = Field(..., description="品牌名称")
    target_brand: str = Field(..., description="目标品牌")
    keywords: List[str] = Field(..., description="关键词列表")
    status: str = Field(..., description="审计状态")
    geo_score: Optional[float] = Field(None, description="GEO Score™")
    started_at: datetime = Field(..., description="开始时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    error: Optional[str] = Field(None, description="错误信息")


class AuditListResponse(BaseModel):
    """审计列表响应"""
    audits: List[AuditResponse] = Field(..., description="审计列表")
    total: int = Field(..., description="总数")


class ErrorResponse(BaseModel):
    """错误响应"""
    error: str = Field(..., description="错误信息")
    detail: Optional[str] = Field(None, description="详细信息")


class StatsResponse(BaseModel):
    """统计数据响应"""
    total_audits: int = Field(..., description="总检测数")
    completed_audits: int = Field(..., description="已完成检测数")
    average_score: Optional[float] = Field(None, description="平均 GEO Score™")
    total_brands: int = Field(..., description="监控品牌数")

