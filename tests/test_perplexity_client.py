"""
Perplexity 客户端测试脚本
注意：需要配置 PERPLEXITY_API_KEY 环境变量才能运行
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.connectors.perplexity_client import PerplexityClient, get_perplexity_client


async def test_simple_query():
    """测试简单查询"""
    print("=" * 50)
    print("测试 Perplexity 客户端 - 简单查询")
    print("=" * 50)
    
    try:
        client = get_perplexity_client()
        
        query = "目前市场上最好的无线耳机有哪些？"
        print(f"\n发送查询: {query}")
        
        result = await client.simple_query(query, temperature=0.7)
        
        print(f"\n✅ 请求成功！")
        print(f"模型: {result['model']}")
        print(f"内容: {result['content'][:200]}...")  # 只显示前200字符
        print(f"Token 使用: {result['usage']}")
        print(f"引用链接数量: {len(result.get('citations', []))}")
        
        # 显示前3个引用链接
        citations = result.get('citations', [])
        if citations:
            print("\n引用链接（前3个）:")
            for i, citation in enumerate(citations[:3], 1):
                print(f"  {i}. {citation.get('url', 'N/A')}")
                if citation.get('title'):
                    print(f"     标题: {citation['title']}")
        
        return True
        
    except ValueError as e:
        print(f"\n❌ 配置错误: {e}")
        print("请确保在 .env 文件中设置了 PERPLEXITY_API_KEY")
        return False
        
    except Exception as e:
        print(f"\n❌ 请求失败: {e}")
        return False


async def test_chat_completion():
    """测试聊天完成接口"""
    print("\n" + "=" * 50)
    print("测试 Perplexity 客户端 - 聊天完成")
    print("=" * 50)
    
    try:
        client = get_perplexity_client()
        
        messages = [
            {"role": "user", "content": "对比 Dyson、Shark 和 Bissell 吸尘器的优缺点"}
        ]
        
        print(f"\n发送消息: {messages[0]['content']}")
        
        result = await client.chat_completion(
            messages=messages,
            model="llama-3.1-sonar-large-128k-online",
            temperature=0.7,
            return_citations=True
        )
        
        print(f"\n✅ 请求成功！")
        print(f"模型: {result['model']}")
        print(f"内容: {result['content'][:200]}...")
        print(f"Token 使用: {result['usage']}")
        print(f"引用链接数量: {len(result.get('citations', []))}")
        
        # 显示所有引用链接
        citations = result.get('citations', [])
        if citations:
            print("\n引用链接:")
            for i, citation in enumerate(citations, 1):
                print(f"  {i}. {citation.get('url', 'N/A')}")
                if citation.get('title'):
                    print(f"     标题: {citation['title']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 请求失败: {e}")
        return False


async def main():
    """主测试函数"""
    print("\n开始测试 Perplexity 客户端...\n")
    print("注意：Perplexity 是 GEO 的核心指标模型，因为它提供引用链接（citations）\n")
    
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

