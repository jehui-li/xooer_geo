#!/usr/bin/env python3
"""
数据库初始化脚本
用于创建 MongoDB 索引以提高查询性能
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database.mongodb_pool import get_pool
from utils.logger import logger


async def init_indexes():
    """初始化数据库索引"""
    try:
        pool = await get_pool()
        
        # audit_results 集合索引
        audit_indexes = [
            {
                "keys": [("audit_id", 1)],
                "name": "audit_id_index",
                "unique": True
            },
            {
                "keys": [("brand_name", 1)],
                "name": "brand_name_index",
                "unique": False
            },
            {
                "keys": [("status", 1)],
                "name": "status_index",
                "unique": False
            },
            {
                "keys": [("started_at", -1)],
                "name": "started_at_index",
                "unique": False
            },
            {
                "keys": [("brand_name", 1), ("started_at", -1)],
                "name": "brand_name_started_at_index",
                "unique": False
            }
        ]
        
        await pool.create_indexes("audit_results", audit_indexes)
        logger.info("✅ Created indexes for audit_results collection")
        print("✅ audit_results 集合索引创建完成")
        
        # probe_responses 集合索引
        probe_indexes = [
            {
                "keys": [("probe_id", 1)],
                "name": "probe_id_index",
                "unique": True
            },
            {
                "keys": [("keyword", 1)],
                "name": "keyword_index",
                "unique": False
            },
            {
                "keys": [("model", 1)],
                "name": "model_index",
                "unique": False
            },
            {
                "keys": [("query", 1)],
                "name": "query_index",
                "unique": False
            },
            {
                "keys": [("timestamp", -1)],
                "name": "timestamp_index",
                "unique": False
            },
            {
                "keys": [("keyword", 1), ("model", 1), ("query", 1)],
                "name": "keyword_model_query_index",
                "unique": False
            }
        ]
        
        await pool.create_indexes("probe_responses", probe_indexes)
        logger.info("✅ Created indexes for probe_responses collection")
        print("✅ probe_responses 集合索引创建完成")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 数据库索引初始化失败: {str(e)}")
        print(f"❌ 错误: {str(e)}")
        return False


async def verify_connection():
    """验证数据库连接"""
    try:
        pool = await get_pool()
        database = pool.get_database()
        
        # 执行 ping 命令验证连接
        await pool._client.admin.command('ping')
        
        print(f"✅ 数据库连接成功")
        print(f"   数据库名称: {database.name}")
        print(f"   连接 URI: {pool.uri}")
        return True
        
    except Exception as e:
        logger.error(f"❌ 数据库连接失败: {str(e)}")
        print(f"❌ 连接失败: {str(e)}")
        print("\n提示: 请确保 MongoDB 服务已启动")
        print("启动方式:")
        print("  - macOS: brew services start mongodb-community")
        print("  - Docker: docker run -d -p 27017:27017 --name mongodb mongo:latest")
        return False


async def main():
    """主函数"""
    print("=" * 60)
    print("GEO Agent 数据库初始化脚本")
    print("=" * 60)
    print()
    
    # 1. 验证连接
    print("步骤 1/2: 验证数据库连接...")
    if not await verify_connection():
        print("\n❌ 初始化失败：无法连接到数据库")
        sys.exit(1)
    
    print()
    
    # 2. 创建索引
    print("步骤 2/2: 创建数据库索引...")
    if not await init_indexes():
        print("\n❌ 初始化失败：索引创建失败")
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("✅ 数据库初始化完成！")
    print("=" * 60)
    sys.exit(0)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  操作被用户中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ 脚本执行失败: {str(e)}")
        print(f"\n❌ 脚本执行失败: {str(e)}")
        sys.exit(1)

