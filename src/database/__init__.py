"""
数据库模块
提供 MongoDB 异步连接池和数据库操作接口
"""

from src.database.mongodb_pool import (
    MongoDBPool,
    get_database,
    get_collection,
    get_pool,
    initialize_pool,
    close_pool
)
from src.database.db_operations import (
    insert_one,
    insert_many,
    find_one,
    find_many,
    update_one,
    update_many,
    delete_one,
    delete_many,
    count_documents,
    aggregate
)

__all__ = [
    "MongoDBPool",
    "get_database",
    "get_collection",
    "get_pool",
    "initialize_pool",
    "close_pool",
    "insert_one",
    "insert_many",
    "find_one",
    "find_many",
    "update_one",
    "update_many",
    "delete_one",
    "delete_many",
    "count_documents",
    "aggregate"
]

