"""
API 模块
提供 FastAPI 应用和认证功能
"""

from .main import app
from .auth import verify_api_key
from .schemas import AuditRequest, AuditResponse, AuditListResponse

__all__ = [
    "app",
    "verify_api_key",
    "AuditRequest",
    "AuditResponse",
    "AuditListResponse"
]

