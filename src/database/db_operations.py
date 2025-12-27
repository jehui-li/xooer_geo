"""
MongoDB 数据库操作辅助函数
提供常用的 CRUD 操作封装
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorCollection
from src.database.mongodb_pool import get_collection
from utils.logger import logger


async def insert_one(
    collection_name: str,
    document: Dict[str, Any],
    add_timestamp: bool = True
) -> str:
    """
    插入单个文档
    
    Args:
        collection_name: 集合名称
        document: 文档数据
        add_timestamp: 是否自动添加时间戳，默认 True
    
    Returns:
        插入的文档 ID
    """
    collection = get_collection(collection_name)
    
    if add_timestamp:
        document["created_at"] = datetime.utcnow()
        document["updated_at"] = datetime.utcnow()
    
    result = await collection.insert_one(document)
    logger.debug(f"Inserted document into {collection_name}, ID: {result.inserted_id}")
    return str(result.inserted_id)


async def insert_many(
    collection_name: str,
    documents: List[Dict[str, Any]],
    add_timestamp: bool = True
) -> List[str]:
    """
    插入多个文档
    
    Args:
        collection_name: 集合名称
        documents: 文档列表
        add_timestamp: 是否自动添加时间戳，默认 True
    
    Returns:
        插入的文档 ID 列表
    """
    collection = get_collection(collection_name)
    
    if add_timestamp:
        now = datetime.utcnow()
        for doc in documents:
            doc["created_at"] = now
            doc["updated_at"] = now
    
    result = await collection.insert_many(documents)
    logger.debug(f"Inserted {len(result.inserted_ids)} documents into {collection_name}")
    return [str(id) for id in result.inserted_ids]


async def find_one(
    collection_name: str,
    filter: Dict[str, Any],
    projection: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """
    查找单个文档
    
    Args:
        collection_name: 集合名称
        filter: 查询条件
        projection: 投影字段，可选
    
    Returns:
        找到的文档，如果不存在则返回 None
    """
    collection = get_collection(collection_name)
    return await collection.find_one(filter, projection)


async def find_many(
    collection_name: str,
    filter: Dict[str, Any],
    projection: Optional[Dict[str, Any]] = None,
    sort: Optional[List[tuple]] = None,
    limit: Optional[int] = None,
    skip: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    查找多个文档
    
    Args:
        collection_name: 集合名称
        filter: 查询条件
        projection: 投影字段，可选
        sort: 排序规则，格式：[("field", 1)]，1 为升序，-1 为降序
        limit: 限制返回数量，可选
        skip: 跳过数量，可选
    
    Returns:
        文档列表
    """
    collection = get_collection(collection_name)
    cursor = collection.find(filter, projection)
    
    if sort:
        cursor = cursor.sort(sort)
    if skip:
        cursor = cursor.skip(skip)
    if limit:
        cursor = cursor.limit(limit)
    
    return await cursor.to_list(length=limit or 1000)


async def update_one(
    collection_name: str,
    filter: Dict[str, Any],
    update: Dict[str, Any],
    upsert: bool = False,
    add_timestamp: bool = True
) -> bool:
    """
    更新单个文档
    
    Args:
        collection_name: 集合名称
        filter: 查询条件
        update: 更新操作（使用 MongoDB 更新操作符，如 $set）
        upsert: 如果文档不存在是否创建，默认 False
        add_timestamp: 是否自动更新 updated_at，默认 True
    
    Returns:
        True 如果更新成功，False 否则
    """
    collection = get_collection(collection_name)
    
    if add_timestamp:
        if "$set" not in update:
            update["$set"] = {}
        update["$set"]["updated_at"] = datetime.utcnow()
    
    result = await collection.update_one(filter, update, upsert=upsert)
    logger.debug(
        f"Updated document in {collection_name}, "
        f"Matched: {result.matched_count}, Modified: {result.modified_count}"
    )
    return result.modified_count > 0 or result.upserted_id is not None


async def update_many(
    collection_name: str,
    filter: Dict[str, Any],
    update: Dict[str, Any],
    add_timestamp: bool = True
) -> int:
    """
    更新多个文档
    
    Args:
        collection_name: 集合名称
        filter: 查询条件
        update: 更新操作（使用 MongoDB 更新操作符，如 $set）
        add_timestamp: 是否自动更新 updated_at，默认 True
    
    Returns:
        修改的文档数量
    """
    collection = get_collection(collection_name)
    
    if add_timestamp:
        if "$set" not in update:
            update["$set"] = {}
        update["$set"]["updated_at"] = datetime.utcnow()
    
    result = await collection.update_many(filter, update)
    logger.debug(f"Updated {result.modified_count} documents in {collection_name}")
    return result.modified_count


async def delete_one(
    collection_name: str,
    filter: Dict[str, Any]
) -> bool:
    """
    删除单个文档
    
    Args:
        collection_name: 集合名称
        filter: 查询条件
    
    Returns:
        True 如果删除成功，False 否则
    """
    collection = get_collection(collection_name)
    result = await collection.delete_one(filter)
    logger.debug(f"Deleted document from {collection_name}, Deleted: {result.deleted_count}")
    return result.deleted_count > 0


async def delete_many(
    collection_name: str,
    filter: Dict[str, Any]
) -> int:
    """
    删除多个文档
    
    Args:
        collection_name: 集合名称
        filter: 查询条件
    
    Returns:
        删除的文档数量
    """
    collection = get_collection(collection_name)
    result = await collection.delete_many(filter)
    logger.debug(f"Deleted {result.deleted_count} documents from {collection_name}")
    return result.deleted_count


async def count_documents(
    collection_name: str,
    filter: Optional[Dict[str, Any]] = None
) -> int:
    """
    统计文档数量
    
    Args:
        collection_name: 集合名称
        filter: 查询条件，可选
    
    Returns:
        文档数量
    """
    collection = get_collection(collection_name)
    filter = filter or {}
    return await collection.count_documents(filter)


async def aggregate(
    collection_name: str,
    pipeline: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    聚合查询
    
    Args:
        collection_name: 集合名称
        pipeline: 聚合管道
    
    Returns:
        聚合结果列表
    """
    collection = get_collection(collection_name)
    cursor = collection.aggregate(pipeline)
    return await cursor.to_list(length=None)

