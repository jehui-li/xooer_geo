"""
数据模型测试脚本
验证所有数据模型的创建和转换功能
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import (
    ProbeType,
    ProbeResponse,
    Citation,
    BrandMention,
    Sentiment,
    ProbeResult,
    GeoScore,
    ScoreBreakdown,
    AuditResult,
    KeywordResult,
    HistoricalTrend,
    Strategy,
    StrategyRecommendation,
    CacheResponse,
    model_to_dict,
    dict_to_model,
    generate_audit_id,
    generate_probe_id,
    generate_strategy_id,
    generate_cache_key
)


def test_probe_models():
    """测试探针相关模型"""
    print("=" * 50)
    print("测试探针相关模型")
    print("=" * 50)
    
    # 测试 Citation
    citation = Citation(
        url="https://example.com/product",
        title="Product Page",
        text="This is a great product...",
        citation_type="official"
    )
    print(f"✅ Citation 创建成功: {citation.url}")
    
    # 测试 ProbeResponse
    probe_response = ProbeResponse(
        probe_id="probe_001",
        probe_type=ProbeType.DIRECT_RECOMMENDATION,
        keyword="project management software",
        model="gpt-4o",
        query="What are the best project management software?",
        temperature=0.7,
        content="Here are some of the best project management software...",
        citations=[citation],
        usage={"prompt_tokens": 100, "completion_tokens": 200, "total_tokens": 300}
    )
    print(f"✅ ProbeResponse 创建成功: {probe_response.probe_id}")
    
    return True


def test_analysis_models():
    """测试分析相关模型"""
    print("\n" + "=" * 50)
    print("测试分析相关模型")
    print("=" * 50)
    
    # 测试 BrandMention
    brand_mention = BrandMention(
        brand_name="Asana",
        is_mentioned=True,
        ranking=1,
        sentiment=Sentiment.POSITIVE,
        mention_text="Asana is one of the best project management tools...",
        accuracy_score=0.95,
        hallucination_risk=False
    )
    print(f"✅ BrandMention 创建成功: {brand_mention.brand_name}")
    
    # 测试 ProbeResult
    probe_result = ProbeResult(
        probe_id="probe_001",
        probe_type="direct_recommendation",
        keyword="project management software",
        model="gpt-4o",
        temperature=0.7,
        brand_mentions=[brand_mention],
        total_mentions=5,
        has_target_brand=True,
        target_brand_ranking=1,
        target_brand_sentiment=Sentiment.POSITIVE
    )
    print(f"✅ ProbeResult 创建成功: {probe_result.probe_id}")
    
    return True


def test_scoring_models():
    """测试评分相关模型"""
    print("\n" + "=" * 50)
    print("测试评分相关模型")
    print("=" * 50)
    
    # 测试 ScoreBreakdown
    breakdown = ScoreBreakdown(
        som_score=85.0,
        som_percentage=85.0,
        citation_score=75.0,
        ranking_score=80.0,
        accuracy_score=90.0,
        accuracy_percentage=90.0
    )
    print(f"✅ ScoreBreakdown 创建成功: SOM={breakdown.som_score}")
    
    # 测试 GeoScore
    geo_score = GeoScore(
        overall_score=82.5,
        breakdown=breakdown,
        weights={"som": 0.4, "citation": 0.3, "ranking": 0.2, "accuracy": 0.1},
        test_count=50,
        models_tested=["gpt-4o", "gemini-1.5-pro"],
        keywords_tested=["project management software"]
    )
    print(f"✅ GeoScore 创建成功: {geo_score.overall_score}")
    
    return True


def test_audit_models():
    """测试审计相关模型"""
    print("\n" + "=" * 50)
    print("测试审计相关模型")
    print("=" * 50)
    
    # 测试 KeywordResult
    keyword_result = KeywordResult(
        keyword="project management software",
        total_probes=15,
        total_responses=15,
        mention_rate=0.8,
        average_ranking=2.5,
        best_ranking=1,
        worst_ranking=5,
        models_tested=["gpt-4o", "gemini-1.5-pro"]
    )
    print(f"✅ KeywordResult 创建成功: {keyword_result.keyword}")
    
    # 测试 AuditResult
    audit_id = generate_audit_id("Asana")
    audit_result = AuditResult(
        audit_id=audit_id,
        brand_name="Asana",
        target_brand="Asana",
        keywords=["project management software"],
        models=["gpt-4o", "gemini-1.5-pro"],
        keyword_results=[keyword_result],
        status="completed",
        total_api_calls=50
    )
    print(f"✅ AuditResult 创建成功: {audit_result.audit_id}")
    
    return True


def test_utility_functions():
    """测试工具函数"""
    print("\n" + "=" * 50)
    print("测试工具函数")
    print("=" * 50)
    
    # 测试 ID 生成
    audit_id = generate_audit_id("Asana")
    print(f"✅ generate_audit_id: {audit_id}")
    
    probe_id = generate_probe_id("project management", "direct_recommendation", 1)
    print(f"✅ generate_probe_id: {probe_id}")
    
    strategy_id = generate_strategy_id(audit_id)
    print(f"✅ generate_strategy_id: {strategy_id}")
    
    cache_key = generate_cache_key("What is GEO?", "gpt-4o", 0.7)
    print(f"✅ generate_cache_key: {cache_key}")
    
    # 测试模型转换
    from src.models.probe import ProbeResponse, ProbeType
    
    probe = ProbeResponse(
        probe_id="test_001",
        probe_type=ProbeType.DIRECT_RECOMMENDATION,
        keyword="test",
        model="gpt-4o",
        query="test query",
        temperature=0.7,
        content="test content"
    )
    
    # 转换为字典
    probe_dict = model_to_dict(probe)
    print(f"✅ model_to_dict: {len(probe_dict)} 个字段")
    
    # 从字典转换回模型
    probe_restored = dict_to_model(ProbeResponse, probe_dict)
    print(f"✅ dict_to_model: {probe_restored.probe_id}")
    
    return True


def test_strategy_models():
    """测试策略相关模型"""
    print("\n" + "=" * 50)
    print("测试策略相关模型")
    print("=" * 50)
    
    # 测试 StrategyRecommendation
    recommendation = StrategyRecommendation(
        category="citation",
        priority="high",
        title="优化 Schema Markup",
        description="添加结构化数据标记以提高引用率",
        action_items=["添加 JSON-LD", "优化元数据"],
        expected_impact="提高 20-30% 的引用得分"
    )
    print(f"✅ StrategyRecommendation 创建成功: {recommendation.title}")
    
    # 测试 Strategy
    strategy = Strategy(
        strategy_id="strategy_001",
        audit_id="audit_001",
        brand_name="Asana",
        geo_score=82.5,
        target_score=90.0,
        recommendations=[recommendation],
        summary="基于当前 GEO Score™ 分析，建议重点关注引用和排序"
    )
    print(f"✅ Strategy 创建成功: {strategy.strategy_id}")
    
    return True


def test_cache_models():
    """测试缓存相关模型"""
    print("\n" + "=" * 50)
    print("测试缓存相关模型")
    print("=" * 50)
    
    cache = CacheResponse(
        cache_key="hash_abc123",
        query="What are the best project management software?",
        model="gpt-4o",
        temperature=0.7,
        content="Here are some of the best...",
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    print(f"✅ CacheResponse 创建成功: {cache.cache_key}")
    
    return True


def main():
    """主测试函数"""
    print("\n开始测试数据模型...\n")
    
    results = []
    results.append(test_probe_models())
    results.append(test_analysis_models())
    results.append(test_scoring_models())
    results.append(test_audit_models())
    results.append(test_strategy_models())
    results.append(test_cache_models())
    results.append(test_utility_functions())
    
    print("\n" + "=" * 50)
    if all(results):
        print("✅ 所有测试通过！")
        return 0
    else:
        print("❌ 部分测试失败")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

