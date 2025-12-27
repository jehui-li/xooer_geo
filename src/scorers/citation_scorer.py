"""
权威引文比评分模块
计算官网引用和权威来源引用的得分
"""

from typing import List
from src.models.analysis import ProbeResult
from utils.logger import logger


class CitationScorer:
    """权威引文比评分器"""
    
    # 权重配置
    OFFICIAL_CITATION_WEIGHT = 1.0  # 官网引用权重
    AUTHORITATIVE_CITATION_WEIGHT = 0.5  # 权威来源引用权重
    
    @staticmethod
    def calculate_citation_score(probe_results: List[ProbeResult]) -> float:
        """
        计算权威引文比得分（0-100）
        
        评分逻辑：
        - 官网引用：每个得 10 分
        - 权威来源引用：每个得 5 分
        - 满分 100 分（如果有 10 个官网引用，或 20 个权威来源引用）
        - 得分 = min(100, (官网引用数 * 10 + 权威来源引用数 * 5))
        
        Args:
            probe_results: 探针结果列表
        
        Returns:
            引文得分（0-100）
        """
        if not probe_results:
            return 0.0
        
        total_official = sum(result.official_citations_count for result in probe_results)
        total_authoritative = sum(result.authoritative_citations_count for result in probe_results)
        
        # 计算得分：官网引用权重更高
        score = (total_official * CitationScorer.OFFICIAL_CITATION_WEIGHT * 10 +
                total_authoritative * CitationScorer.AUTHORITATIVE_CITATION_WEIGHT * 10)
        
        # 限制在 0-100 范围内
        citation_score = min(100.0, max(0.0, score))
        
        logger.debug(
            f"Citation score calculation: "
            f"Official: {total_official}, Authoritative: {total_authoritative}, "
            f"Score: {citation_score:.2f}"
        )
        
        return round(citation_score, 2)
    
    @staticmethod
    def calculate(probe_results: List[ProbeResult]) -> dict:
        """
        计算引文相关指标
        
        Args:
            probe_results: 探针结果列表
        
        Returns:
            包含引文相关指标的字典：
            {
                "citation_score": 75.0,        # 引文得分（0-100）
                "official_citations": 10,      # 官网引用总数
                "authoritative_citations": 5,  # 权威来源引用总数
                "total_citations": 15          # 总引用数
            }
        """
        if not probe_results:
            return {
                "citation_score": 0.0,
                "official_citations": 0,
                "authoritative_citations": 0,
                "total_citations": 0
            }
        
        total_official = sum(result.official_citations_count for result in probe_results)
        total_authoritative = sum(result.authoritative_citations_count for result in probe_results)
        
        # 计算得分
        score = (total_official * CitationScorer.OFFICIAL_CITATION_WEIGHT * 10 +
                total_authoritative * CitationScorer.AUTHORITATIVE_CITATION_WEIGHT * 10)
        citation_score = min(100.0, max(0.0, score))
        
        return {
            "citation_score": round(citation_score, 2),
            "official_citations": total_official,
            "authoritative_citations": total_authoritative,
            "total_citations": total_official + total_authoritative
        }

