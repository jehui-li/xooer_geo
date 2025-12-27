"""
OpenAI 客户端测试脚本
注意：需要配置 OPENAI_API_KEY 环境变量才能运行
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.connectors.openai_client import OpenAIClient, get_client


async def test_simple_query():
    """测试简单查询"""
    print("=" * 50)
    print("测试 OpenAI 客户端 - 简单查询")
    print("=" * 50)
    
    try:
        client = get_client()
        
        query = "请用一句话介绍人工智能"
        print(f"\n发送查询: {query}")
        
        result = await client.simple_query(query, temperature=0.7)
        
        print(f"\n✅ 请求成功！")
        print(f"模型: {result['model']}")
        print(f"内容: {result['content'][:200]}...")  # 只显示前200字符
        print(f"Token 使用: {result['usage']}")
        
        return True
        
    except ValueError as e:
        print(f"\n❌ 配置错误: {e}")
        print("请确保在 .env 文件中设置了 OPENAI_API_KEY")
        return False
        
    except Exception as e:
        print(f"\n❌ 请求失败: {e}")
        return False


async def test_chat_completion():
    """测试聊天完成接口"""
    print("\n" + "=" * 50)
    print("测试 OpenAI 客户端 - 聊天完成")
    print("=" * 50)
    
    try:
        client = get_client()
        
        messages = [
            {"role": "user", "content": "什么是 GEO？"}
        ]
        
        print(f"\n发送消息: {messages[0]['content']}")
        
        result = await client.chat_completion(
            messages=messages,
            model="gpt-4o",
            temperature=0.7
        )
        
        print(f"\n✅ 请求成功！")
        print(f"模型: {result['model']}")
        print(f"内容: {result['content'][:200]}...")
        print(f"Token 使用: {result['usage']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 请求失败: {e}")
        return False


async def main():
    """主测试函数"""
    print("\n开始测试 OpenAI 客户端...\n")
    
    results = []
    results.append(await test_simple_query())
    results.append(await test_chat_completion())
    
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

