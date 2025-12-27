"""
简单内存缓存管理器
基于 query+model 的 hash key 进行缓存
"""

import hashlib
from typing import Dict, Optional, Any
from datetime import datetime, timedelta

from src.models.cache import CacheResponse
from utils.logger import logger


class CacheManager:
    """简单内存缓存管理器"""
    
    def __init__(self, default_expiry_hours: int = 24):
        """
        初始化缓存管理器
        
        Args:
            default_expiry_hours: 默认过期时间（小时），默认 24 小时
        """
        self._cache: Dict[str, CacheResponse] = {}
        self.default_expiry_hours = default_expiry_hours
        logger.info(f"Cache manager initialized with default expiry: {default_expiry_hours} hours")
    
    def get_cache_key(self, query: str, model: str) -> str:
        """
        生成缓存键（基于 query+model 的 hash）
        
        Args:
            query: 查询文本
            model: 模型名称
        
        Returns:
            缓存键字符串
        """
        key_string = f"{query}|{model}"
        return hashlib.md5(key_string.encode("utf-8")).hexdigest()
    
    def get(self, query: str, model: str) -> Optional[CacheResponse]:
        """
        从缓存中获取响应
        
        Args:
            query: 查询文本
            model: 模型名称
        
        Returns:
            CacheResponse 对象，如果未找到或已过期则返回 None
        """
        cache_key = self.get_cache_key(query, model)
        
        if cache_key not in self._cache:
            return None
        
        cached_response = self._cache[cache_key]
        
        # 检查是否过期
        if datetime.utcnow() > cached_response.expires_at:
            logger.debug(f"Cache expired for key: {cache_key}")
            del self._cache[cache_key]
            return None
        
        # 更新命中次数
        cached_response.hit_count += 1
        logger.debug(f"Cache hit for key: {cache_key}, hit count: {cached_response.hit_count}")
        
        return cached_response
    
    def set(
        self,
        query: str,
        model: str,
        temperature: float,
        content: str,
        citations: list = None,
        usage: Dict[str, int] = None,
        expires_at: Optional[datetime] = None
    ) -> CacheResponse:
        """
        设置缓存
        
        Args:
            query: 查询文本
            model: 模型名称
            temperature: Temperature 参数（用于存储，但不影响缓存键）
            content: 响应内容
            citations: 引用链接列表
            usage: Token 使用情况
            expires_at: 过期时间，如果为 None 则使用默认过期时间
        
        Returns:
            CacheResponse 对象
        """
        cache_key = self.get_cache_key(query, model)
        
        if expires_at is None:
            expires_at = datetime.utcnow() + timedelta(hours=self.default_expiry_hours)
        
        cached_response = CacheResponse(
            cache_key=cache_key,
            query=query,
            model=model,
            temperature=temperature,
            content=content,
            citations=citations or [],
            usage=usage or {},
            cached_at=datetime.utcnow(),
            expires_at=expires_at,
            hit_count=0,
            metadata={}
        )
        
        self._cache[cache_key] = cached_response
        logger.debug(f"Cache set for key: {cache_key}, expires at: {expires_at}")
        
        return cached_response
    
    def delete(self, query: str, model: str) -> bool:
        """
        删除缓存
        
        Args:
            query: 查询文本
            model: 模型名称
        
        Returns:
            True 如果删除成功，False 如果不存在
        """
        cache_key = self.get_cache_key(query, model)
        
        if cache_key in self._cache:
            del self._cache[cache_key]
            logger.debug(f"Cache deleted for key: {cache_key}")
            return True
        
        return False
    
    def clear_expired(self) -> int:
        """
        清除所有过期的缓存
        
        Returns:
            清除的缓存数量
        """
        now = datetime.utcnow()
        expired_keys = [
            key for key, value in self._cache.items()
            if now > value.expires_at
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            logger.info(f"Cleared {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)
    
    def clear_all(self) -> int:
        """
        清除所有缓存
        
        Returns:
            清除的缓存数量
        """
        count = len(self._cache)
        self._cache.clear()
        logger.info(f"Cleared all {count} cache entries")
        return count
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            缓存统计字典
        """
        now = datetime.utcnow()
        total_count = len(self._cache)
        expired_count = sum(1 for value in self._cache.values() if now > value.expires_at)
        total_hits = sum(value.hit_count for value in self._cache.values())
        
        return {
            "total_entries": total_count,
            "active_entries": total_count - expired_count,
            "expired_entries": expired_count,
            "total_hits": total_hits,
            "average_hits_per_entry": total_hits / total_count if total_count > 0 else 0
        }


# 全局缓存管理器实例
_global_cache_manager: Optional[CacheManager] = None


def get_cache_manager(expiry_hours: int = 24) -> CacheManager:
    """
    获取全局缓存管理器实例（单例模式）
    
    Args:
        expiry_hours: 默认过期时间（小时）
    
    Returns:
        CacheManager 实例
    """
    global _global_cache_manager
    if _global_cache_manager is None:
        _global_cache_manager = CacheManager(default_expiry_hours=expiry_hours)
    return _global_cache_manager

