"""
探针生成器测试
"""

import pytest
from src.probes import ProbeGenerator, Language
from src.models.probe import ProbeType


def test_direct_recommendation_english():
    """测试直接推荐类（英文）"""
    generator = ProbeGenerator(default_language=Language.EN)
    query = generator.generate(
        keyword="project management software",
        probe_type=ProbeType.DIRECT_RECOMMENDATION
    )
    assert "project management software" in query
    assert "best" in query.lower() or "market" in query.lower()


def test_direct_recommendation_chinese():
    """测试直接推荐类（中文）"""
    generator = ProbeGenerator(default_language=Language.ZH)
    query = generator.generate(
        keyword="项目管理软件",
        probe_type=ProbeType.DIRECT_RECOMMENDATION,
        language=Language.ZH
    )
    assert "项目管理软件" in query
    assert "最好" in query or "哪些" in query


def test_attribute_comparison_english():
    """测试属性对比类（英文）"""
    generator = ProbeGenerator(default_language=Language.EN)
    query = generator.generate(
        keyword="project management software",
        probe_type=ProbeType.ATTRIBUTE_COMPARISON,
        target_brand="Asana",
        competitor_brands=["Trello", "Monday.com"]
    )
    assert "Asana" in query
    assert "Trello" in query
    assert "Monday.com" in query
    assert "compare" in query.lower() or "pros" in query.lower()


def test_attribute_comparison_chinese():
    """测试属性对比类（中文）"""
    generator = ProbeGenerator(default_language=Language.ZH)
    query = generator.generate(
        keyword="项目管理软件",
        probe_type=ProbeType.ATTRIBUTE_COMPARISON,
        language=Language.ZH,
        target_brand="Asana",
        competitor_brands=["Trello", "Monday.com"]
    )
    assert "Asana" in query
    assert "Trello" in query
    assert "优缺点" in query or "对比" in query


def test_solution_based_english():
    """测试解决方案类（英文）"""
    generator = ProbeGenerator(default_language=Language.EN)
    query = generator.generate(
        keyword="project management software",
        probe_type=ProbeType.SOLUTION_BASED,
        pain_point="team collaboration issues"
    )
    assert "team collaboration issues" in query
    assert "how" in query.lower() or "solve" in query.lower()


def test_solution_based_chinese():
    """测试解决方案类（中文）"""
    generator = ProbeGenerator(default_language=Language.ZH)
    query = generator.generate(
        keyword="项目管理软件",
        probe_type=ProbeType.SOLUTION_BASED,
        language=Language.ZH,
        pain_point="团队协作问题"
    )
    assert "团队协作问题" in query
    assert "如何" in query or "解决" in query


def test_attribute_comparison_missing_target_brand():
    """测试属性对比类缺少目标品牌时的错误处理"""
    generator = ProbeGenerator()
    with pytest.raises(ValueError, match="target_brand"):
        generator.generate(
            keyword="project management software",
            probe_type=ProbeType.ATTRIBUTE_COMPARISON
        )


def test_generate_all_types():
    """测试生成所有类型的探针"""
    generator = ProbeGenerator(default_language=Language.EN)
    all_probes = generator.generate_all_types(
        keyword="project management software",
        target_brand="Asana"
    )
    assert ProbeType.DIRECT_RECOMMENDATION in all_probes
    assert ProbeType.ATTRIBUTE_COMPARISON in all_probes
    assert ProbeType.SOLUTION_BASED in all_probes
    assert len(all_probes) == 3


def test_generate_batch():
    """测试批量生成探针"""
    generator = ProbeGenerator(default_language=Language.EN)
    keywords = ["project management software", "CRM software"]
    result = generator.generate_batch(
        keywords=keywords,
        target_brand="Asana"
    )
    assert len(result) == 2
    assert "project management software" in result
    assert "CRM software" in result
    for keyword in keywords:
        assert ProbeType.DIRECT_RECOMMENDATION in result[keyword]
        assert ProbeType.SOLUTION_BASED in result[keyword]


def test_solution_based_without_pain_point():
    """测试解决方案类未提供痛点时使用关键词作为痛点"""
    generator = ProbeGenerator(default_language=Language.EN)
    query = generator.generate(
        keyword="project management software",
        probe_type=ProbeType.SOLUTION_BASED
    )
    assert "project management software" in query


def test_attribute_comparison_without_competitors():
    """测试属性对比类未提供竞争对手时使用默认表述"""
    generator = ProbeGenerator(default_language=Language.EN)
    query = generator.generate(
        keyword="project management software",
        probe_type=ProbeType.ATTRIBUTE_COMPARISON,
        target_brand="Asana"
    )
    assert "Asana" in query
    assert "other brands" in query or "compare" in query.lower()

