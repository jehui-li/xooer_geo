"""
API 认证模块
提供简单的 API Key 认证
"""

from typing import Optional
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from config.settings import settings

# API Key Header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
    """
    验证 API Key
    
    Args:
        api_key: 从请求头中提取的 API Key
    
    Returns:
        API Key 字符串
    
    Raises:
        HTTPException: 如果 API Key 无效
    """
    # 从 settings 获取配置的 API Key
    # 注意：这里应该从环境变量或配置文件中读取，而不是硬编码
    valid_api_key = getattr(settings, "api_key", None)
    
    if not valid_api_key:
        # 如果没有配置 API Key，跳过认证（开发环境）
        return "dev_key"
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key is required. Please provide X-API-Key header.",
            headers={"WWW-Authenticate": "APIKey"},
        )
    
    if api_key != valid_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
            headers={"WWW-Authenticate": "APIKey"},
        )
    
    return api_key

