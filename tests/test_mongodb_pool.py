"""
MongoDB 连接池测试脚本
注意：需要配置 MONGODB_URI 环境变量才能运行
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.mongodb_pool import MongoDBPool, get_pool, get_collection, initialize_pool, close_pool


async def test_connection():
    """测试连接"""
    print("=" * 50)
    print("测试 MongoDB 连接池 - 连接测试")
    print("=" * 50)
    
    try:
        pool = await get_pool()
        
        # 测试 ping
        is_alive = await pool.ping()
        if is_alive:
            print("\n✅ 连接成功！")
            print(f"数据库: {pool.database_name}")
            print(f"连接状态: {pool.is_connected}")
            return True
        else:
            print("\n❌ 连接失败：ping 失败")
            return False
            
    except ValueError as e:
        print(f"\n❌ 配置错误: {e}")
        print("请确保在 .env 文件中设置了 MONGODB_URI 和 MONGODB_DATABASE")
        return False
        
    except Exception as e:
        print(f"\n❌ 连接失败: {e}")
        return False


async def test_collection_operations():
    """测试集合操作"""
    print("\n" + "=" * 50)
    print("测试 MongoDB 连接池 - 集合操作")
    print("=" * 50)
    
    try:
        pool = await get_pool()
        collection = pool.get_collection("test_collection")
        
        # 插入测试数据
        test_doc = {
            "name": "test_document",
            "timestamp": datetime.utcnow(),
            "data": {"key": "value"}
        }
        
        result = await collection.insert_one(test_doc)
        print(f"\n✅ 插入文档成功！ID: {result.inserted_id}")
        
        # 查询文档
        found_doc = await collection.find_one({"_id": result.inserted_id})
        if found_doc:
            print(f"✅ 查询文档成功！名称: {found_doc.get('name')}")
        
        # 更新文档
        update_result = await collection.update_one(
            {"_id": result.inserted_id},
            {"$set": {"updated": True}}
        )
        print(f"✅ 更新文档成功！修改数量: {update_result.modified_count}")
        
        # 删除测试数据
        delete_result = await collection.delete_one({"_id": result.inserted_id})
        print(f"✅ 删除文档成功！删除数量: {delete_result.deleted_count}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 操作失败: {e}")
        return False


async def test_index_creation():
    """测试索引创建"""
    print("\n" + "=" * 50)
    print("测试 MongoDB 连接池 - 索引创建")
    print("=" * 50)
    
    try:
        pool = await get_pool()
        
        indexes = [
            {
                "keys": [("name", 1)],
                "name": "name_index",
                "unique": False
            },
            {
                "keys": [("timestamp", -1)],
                "name": "timestamp_index",
                "unique": False
            }
        ]
        
        await pool.create_indexes("test_collection", indexes)
        print("\n✅ 索引创建成功！")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 索引创建失败: {e}")
        return False


async def test_context_manager():
    """测试上下文管理器"""
    print("\n" + "=" * 50)
    print("测试 MongoDB 连接池 - 上下文管理器")
    print("=" * 50)
    
    try:
        async with MongoDBPool() as pool:
            is_alive = await pool.ping()
            if is_alive:
                print("\n✅ 上下文管理器测试成功！")
                return True
            else:
                print("\n❌ 上下文管理器测试失败：ping 失败")
                return False
                
    except Exception as e:
        print(f"\n❌ 上下文管理器测试失败: {e}")
        return False


async def test_get_collection_helper():
    """测试 get_collection 辅助函数"""
    print("\n" + "=" * 50)
    print("测试 MongoDB 连接池 - get_collection 辅助函数")
    print("=" * 50)
    
    try:
        # 确保连接池已初始化
        await get_pool()
        
        # 使用辅助函数获取集合
        collection = get_collection("test_collection")
        
        # 测试操作
        count = await collection.count_documents({})
        print(f"\n✅ 使用辅助函数获取集合成功！文档数量: {count}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 辅助函数测试失败: {e}")
        return False


async def main():
    """主测试函数"""
    print("\n开始测试 MongoDB 连接池...\n")
    
    results = []
    results.append(await test_connection())
    results.append(await test_collection_operations())
    results.append(await test_index_creation())
    results.append(await test_context_manager())
    results.append(await test_get_collection_helper())
    
    # 清理：关闭连接池
    await close_pool()
    
    print("\n" + "=" * 50)
    if all(results):
        print("✅ 所有测试通过！")
        return 0
    else:
        print("❌ 部分测试失败")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

