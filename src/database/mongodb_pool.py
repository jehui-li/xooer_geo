"""
MongoDB 异步连接池管理模块
使用 motor 实现异步 MongoDB 连接池
"""

import asyncio
from typing import Optional, Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from config.settings import settings
from utils.logger import logger


class MongoDBPool:
    """MongoDB 异步连接池管理器"""
    
    def __init__(
        self,
        uri: Optional[str] = None,
        database_name: Optional[str] = None,
        max_pool_size: int = 100,
        min_pool_size: int = 10,
        max_idle_time_ms: int = 30000,
        connect_timeout_ms: int = 20000,
        server_selection_timeout_ms: int = 30000
    ):
        """
        初始化 MongoDB 连接池
        
        Args:
            uri: MongoDB 连接 URI，如果为 None 则从 settings 读取
            database_name: 数据库名称，如果为 None 则从 settings 读取
            max_pool_size: 最大连接池大小，默认 100
            min_pool_size: 最小连接池大小，默认 10
            max_idle_time_ms: 最大空闲时间（毫秒），默认 30000
            connect_timeout_ms: 连接超时时间（毫秒），默认 20000
            server_selection_timeout_ms: 服务器选择超时时间（毫秒），默认 30000
        """
        self.uri = uri or settings.mongodb_uri
        self.database_name = database_name or settings.mongodb_database
        self.max_pool_size = max_pool_size
        self.min_pool_size = min_pool_size
        self.max_idle_time_ms = max_idle_time_ms
        self.connect_timeout_ms = connect_timeout_ms
        self.server_selection_timeout_ms = server_selection_timeout_ms
        
        self._client: Optional[AsyncIOMotorClient] = None
        self._database: Optional[AsyncIOMotorDatabase] = None
        self._is_connected = False
        
        if not self.uri:
            raise ValueError("MongoDB URI is required. Set MONGODB_URI in .env file.")
        if not self.database_name:
            raise ValueError("MongoDB database name is required. Set MONGODB_DATABASE in .env file.")
    
    async def connect(self) -> None:
        """
        建立 MongoDB 连接池
        
        Raises:
            Exception: 连接失败时抛出异常
        """
        if self._is_connected:
            logger.warning("MongoDB connection pool already connected")
            return
        
        try:
            # 创建 Motor 客户端（自动管理连接池）
            self._client = AsyncIOMotorClient(
                self.uri,
                maxPoolSize=self.max_pool_size,
                minPoolSize=self.min_pool_size,
                maxIdleTimeMS=self.max_idle_time_ms,
                connectTimeoutMS=self.connect_timeout_ms,
                serverSelectionTimeoutMS=self.server_selection_timeout_ms
            )
            
            # 获取数据库实例
            self._database = self._client[self.database_name]
            
            # 测试连接
            await self._client.admin.command('ping')
            
            self._is_connected = True
            logger.info(
                f"MongoDB connection pool connected successfully. "
                f"Database: {self.database_name}, "
                f"Pool size: {self.min_pool_size}-{self.max_pool_size}"
            )
            
        except Exception as e:
            self._is_connected = False
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise Exception(f"MongoDB connection failed: {str(e)}")
    
    async def disconnect(self) -> None:
        """关闭 MongoDB 连接池"""
        if not self._is_connected:
            return
        
        try:
            if self._client:
                self._client.close()
                self._client = None
                self._database = None
                self._is_connected = False
                logger.info("MongoDB connection pool closed")
        except Exception as e:
            logger.error(f"Error closing MongoDB connection: {str(e)}")
    
    async def ping(self) -> bool:
        """
        检查连接是否正常
        
        Returns:
            True 如果连接正常，False 否则
        """
        if not self._is_connected or not self._client:
            return False
        
        try:
            await self._client.admin.command('ping')
            return True
        except Exception as e:
            logger.warning(f"MongoDB ping failed: {str(e)}")
            return False
    
    def get_database(self) -> AsyncIOMotorDatabase:
        """
        获取数据库实例
        
        Returns:
            AsyncIOMotorDatabase 实例
        
        Raises:
            Exception: 如果连接未建立则抛出异常
        """
        if not self._is_connected or not self._database:
            raise Exception("MongoDB connection not established. Call connect() first.")
        return self._database
    
    def get_collection(self, collection_name: str) -> AsyncIOMotorCollection:
        """
        获取集合实例
        
        Args:
            collection_name: 集合名称
        
        Returns:
            AsyncIOMotorCollection 实例
        
        Raises:
            Exception: 如果连接未建立则抛出异常
        """
        database = self.get_database()
        return database[collection_name]
    
    async def create_indexes(
        self,
        collection_name: str,
        indexes: List[Dict[str, Any]]
    ) -> None:
        """
        为集合创建索引
        
        Args:
            collection_name: 集合名称
            indexes: 索引列表，格式：[{"keys": [("field", 1)], "name": "index_name"}]
        
        Raises:
            Exception: 如果连接未建立或创建索引失败则抛出异常
        """
        collection = self.get_collection(collection_name)
        
        try:
            for index in indexes:
                await collection.create_index(
                    index["keys"],
                    name=index.get("name"),
                    unique=index.get("unique", False),
                    background=index.get("background", True)
                )
            logger.info(f"Created {len(indexes)} indexes for collection: {collection_name}")
        except Exception as e:
            logger.error(f"Failed to create indexes for {collection_name}: {str(e)}")
            raise
    
    @property
    def is_connected(self) -> bool:
        """检查连接状态"""
        return self._is_connected
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.disconnect()


# 创建全局连接池实例（延迟初始化）
_pool_instance: Optional[MongoDBPool] = None


async def get_pool() -> MongoDBPool:
    """
    获取全局 MongoDB 连接池实例（单例模式）
    如果未连接，会自动建立连接
    
    Returns:
        MongoDBPool 实例
    
    Note:
        如果 MongoDB 未运行，连接会失败但不抛出异常，返回未连接的池实例
    """
    global _pool_instance
    if _pool_instance is None:
        _pool_instance = MongoDBPool()
        try:
            await _pool_instance.connect()
        except Exception as e:
            logger.warning(f"MongoDB connection failed in get_pool: {str(e)}")
            # 不抛出异常，返回未连接的实例
    elif not _pool_instance.is_connected:
        try:
            await _pool_instance.connect()
        except Exception as e:
            logger.warning(f"MongoDB reconnection failed in get_pool: {str(e)}")
            # 不抛出异常，继续使用未连接的实例
    return _pool_instance


def get_database() -> AsyncIOMotorDatabase:
    """
    获取数据库实例（同步函数，需要在异步上下文中使用）
    注意：此函数需要在已连接的连接池上调用
    
    Returns:
        AsyncIOMotorDatabase 实例
    
    Raises:
        Exception: 如果连接未建立则抛出异常
    """
    if _pool_instance is None or not _pool_instance.is_connected:
        raise Exception("MongoDB connection not established. Call get_pool() first.")
    return _pool_instance.get_database()


def get_collection(collection_name: str) -> AsyncIOMotorCollection:
    """
    获取集合实例（同步函数，需要在异步上下文中使用）
    注意：此函数需要在已连接的连接池上调用
    
    Args:
        collection_name: 集合名称
    
    Returns:
        AsyncIOMotorCollection 实例
    
    Raises:
        Exception: 如果连接未建立则抛出异常
    """
    if _pool_instance is None or not _pool_instance.is_connected:
        raise Exception("MongoDB connection not established. Call get_pool() first.")
    return _pool_instance.get_collection(collection_name)


async def initialize_pool() -> MongoDBPool:
    """
    初始化 MongoDB 连接池（应用启动时调用）
    
    Returns:
        MongoDBPool 实例
    """
    return await get_pool()


async def close_pool() -> None:
    """
    关闭 MongoDB 连接池（应用关闭时调用）
    """
    global _pool_instance
    if _pool_instance:
        await _pool_instance.disconnect()
        _pool_instance = None

