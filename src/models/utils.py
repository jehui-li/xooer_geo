"""
数据模型工具函数
提供模型与 MongoDB 文档之间的转换功能
"""

from typing import Dict, Any, Optional
from bson import ObjectId
from datetime import datetime
from pydantic import BaseModel


def model_to_dict(model: BaseModel, exclude_none: bool = False, exclude_unset: bool = False) -> Dict[str, Any]:
    """
    将 Pydantic 模型转换为字典（用于 MongoDB 存储）
    
    Args:
        model: Pydantic 模型实例
        exclude_none: 是否排除 None 值
        exclude_unset: 是否排除未设置的字段
    
    Returns:
        字典格式的数据
    """
    return model.model_dump(exclude_none=exclude_none, exclude_unset=exclude_unset, mode="json")


def dict_to_model(model_class: type[BaseModel], data: Dict[str, Any]) -> BaseModel:
    """
    将字典转换为 Pydantic 模型（从 MongoDB 读取）
    
    Args:
        model_class: Pydantic 模型类
        data: 字典数据（可能包含 MongoDB 的 _id 字段）
    
    Returns:
        Pydantic 模型实例
    """
    # 处理 MongoDB 的 _id 字段
    if "_id" in data:
        # 将 ObjectId 转换为字符串
        if isinstance(data["_id"], ObjectId):
            data["_id"] = str(data["_id"])
        # 或者可以选择不包含 _id
        # data.pop("_id")
    
    # 处理 datetime 字段（MongoDB 返回的 datetime 已经是 Python datetime）
    # Pydantic 会自动处理，但我们需要确保格式正确
    
    return model_class(**data)


def prepare_for_mongodb(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    准备数据用于 MongoDB 存储
    处理特殊类型（如 datetime, ObjectId 等）
    
    Args:
        data: 原始数据字典
    
    Returns:
        处理后的数据字典
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, datetime):
            result[key] = value
        elif isinstance(value, dict):
            result[key] = prepare_for_mongodb(value)
        elif isinstance(value, list):
            result[key] = [prepare_for_mongodb(item) if isinstance(item, dict) else item for item in value]
        else:
            result[key] = value
    return result


def generate_audit_id(brand_name: str, timestamp: Optional[datetime] = None) -> str:
    """
    生成审计 ID
    
    Args:
        brand_name: 品牌名称
        timestamp: 时间戳，如果为 None 则使用当前时间
    
    Returns:
        审计 ID 字符串
    """
    if timestamp is None:
        timestamp = datetime.utcnow()
    
    date_str = timestamp.strftime("%Y%m%d")
    time_str = timestamp.strftime("%H%M%S")
    brand_slug = brand_name.lower().replace(" ", "_").replace("-", "_")
    
    return f"audit_{date_str}_{time_str}_{brand_slug}"


def generate_probe_id(keyword: str, probe_type: str, index: int) -> str:
    """
    生成探针 ID
    
    Args:
        keyword: 关键词
        probe_type: 探针类型
        index: 探针索引
    
    Returns:
        探针 ID 字符串
    """
    keyword_slug = keyword.lower().replace(" ", "_").replace("-", "_")[:20]
    return f"probe_{probe_type}_{keyword_slug}_{index:03d}"


def generate_strategy_id(audit_id: str) -> str:
    """
    生成策略 ID
    
    Args:
        audit_id: 审计 ID
    
    Returns:
        策略 ID 字符串
    """
    return f"strategy_{audit_id}"


def generate_cache_key(query: str, model: str, temperature: float) -> str:
    """
    生成缓存键
    
    Args:
        query: 查询文本
        model: 模型名称
        temperature: Temperature 参数
    
    Returns:
        缓存键字符串（hash）
    """
    import hashlib
    
    key_string = f"{query}|{model}|{temperature}"
    return hashlib.md5(key_string.encode("utf-8")).hexdigest()

