"""
GEO Score™ 综合评分引擎
整合所有子评分模块，计算最终的 GEO Score™
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

from src.models.analysis import ProbeResult
from src.models.scoring import GeoScore, ScoreBreakdown
from src.scorers.som_scorer import SOMScorer
from src.scorers.citation_scorer import CitationScorer
from src.scorers.ranking_scorer import RankingScorer
from src.scorers.accuracy_scorer import AccuracyScorer
from utils.logger import logger


class GeoScorer:
    """GEO Score™ 综合评分引擎"""
    
    # 固定权重配置
    WEIGHTS = {
        "som": 0.4,      # SOM（模型占有率）权重 40%
        "citation": 0.3,  # 权威引文比权重 30%
        "ranking": 0.2,   # 排序权重 20%
        "accuracy": 0.1   # 内容准确度权重 10%
    }
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        初始化 GEO 评分器
        
        Args:
            weights: 权重配置，如果为 None 则使用默认固定权重
        """
        if weights is None:
            self.weights = self.WEIGHTS.copy()
        else:
            # 验证权重总和是否为 1.0
            total = sum(weights.values())
            if abs(total - 1.0) > 0.01:  # 允许小的浮点数误差
                raise ValueError(f"Weights must sum to 1.0, got {total}")
            self.weights = weights
    
    def calculate_geo_score(self, probe_results: List[ProbeResult]) -> GeoScore:
        """
        计算 GEO Score™
        
        公式：
        GEO Score = SOM * 0.4 + Citation * 0.3 + Ranking * 0.2 + Accuracy * 0.1
        
        Args:
            probe_results: 探针结果列表
        
        Returns:
            GeoScore 对象
        """
        if not probe_results:
            logger.warning("Empty probe results, returning zero score")
            return self._create_zero_score(probe_results)
        
        # 诊断日志：检查 probe_results 的内容
        logger.info(f"Calculating GEO Score from {len(probe_results)} probe results")
        mentioned_count = sum(1 for r in probe_results if r.has_target_brand)
        total_citations = sum(r.official_citations_count + r.authoritative_citations_count for r in probe_results)
        rankings = [r.target_brand_ranking for r in probe_results if r.has_target_brand and r.target_brand_ranking]
        logger.info(
            f"Probe results summary: "
            f"Total: {len(probe_results)}, "
            f"Target mentioned: {mentioned_count}, "
            f"Total citations: {total_citations}, "
            f"Rankings: {rankings[:5] if rankings else 'None'}"
        )
        
        # 1. 计算 SOM 得分
        som_data = SOMScorer.calculate(probe_results)
        logger.debug(f"SOM calculation: {som_data}")
        
        # 2. 计算引文得分
        citation_data = CitationScorer.calculate(probe_results)
        logger.debug(f"Citation calculation: {citation_data}")
        
        # 3. 计算排序得分
        ranking_data = RankingScorer.calculate(probe_results)
        logger.debug(f"Ranking calculation: {ranking_data}")
        
        # 4. 计算准确度得分
        accuracy_data = AccuracyScorer.calculate(probe_results)
        logger.debug(f"Accuracy calculation: {accuracy_data}")
        
        # 5. 计算综合得分
        overall_score = (
            som_data["som_score"] * self.weights["som"] +
            citation_data["citation_score"] * self.weights["citation"] +
            ranking_data["ranking_score"] * self.weights["ranking"] +
            accuracy_data["accuracy_score"] * self.weights["accuracy"]
        )
        
        # 限制在 0-100 范围内
        overall_score = max(0.0, min(100.0, overall_score))
        
        # 6. 构建 ScoreBreakdown
        breakdown = ScoreBreakdown(
            som_score=som_data["som_score"],
            som_percentage=som_data["som_percentage"],
            citation_score=citation_data["citation_score"],
            official_citations=citation_data["official_citations"],
            authoritative_citations=citation_data["authoritative_citations"],
            ranking_score=ranking_data["ranking_score"],
            average_ranking=ranking_data["average_ranking"],
            top3_count=ranking_data["top3_count"],
            accuracy_score=accuracy_data["accuracy_score"],
            accuracy_percentage=accuracy_data["accuracy_percentage"],
            hallucination_count=accuracy_data["hallucination_count"]
        )
        
        # 7. 提取测试元数据
        models_tested = list(set(result.model for result in probe_results))
        keywords_tested = list(set(result.keyword for result in probe_results))
        test_count = len(probe_results)
        
        # 8. 构建 GeoScore
        geo_score = GeoScore(
            overall_score=round(overall_score, 2),
            breakdown=breakdown,
            weights=self.weights.copy(),
            confidence_interval=None,  # 简化版本，不计算置信区间
            test_count=test_count,
            models_tested=models_tested,
            keywords_tested=keywords_tested,
            timestamp=datetime.utcnow(),
            metadata={}
        )
        
        logger.info(
            f"GEO Score calculation completed. "
            f"Overall: {overall_score:.2f}, "
            f"SOM: {som_data['som_score']:.2f}, "
            f"Citation: {citation_data['citation_score']:.2f}, "
            f"Ranking: {ranking_data['ranking_score']:.2f}, "
            f"Accuracy: {accuracy_data['accuracy_score']:.2f}"
        )
        
        return geo_score
    
    def _create_zero_score(self, probe_results: List[ProbeResult]) -> GeoScore:
        """
        创建零分 GeoScore（用于空结果）
        
        Args:
            probe_results: 探针结果列表
        
        Returns:
            零分 GeoScore 对象
        """
        breakdown = ScoreBreakdown(
            som_score=0.0,
            som_percentage=0.0,
            citation_score=0.0,
            official_citations=0,
            authoritative_citations=0,
            ranking_score=0.0,
            average_ranking=None,
            top3_count=0,
            accuracy_score=0.0,
            accuracy_percentage=0.0,
            hallucination_count=0
        )
        
        models_tested = list(set(result.model for result in probe_results)) if probe_results else []
        keywords_tested = list(set(result.keyword for result in probe_results)) if probe_results else []
        
        return GeoScore(
            overall_score=0.0,
            breakdown=breakdown,
            weights=self.weights.copy(),
            confidence_interval=None,
            test_count=len(probe_results),
            models_tested=models_tested,
            keywords_tested=keywords_tested,
            timestamp=datetime.utcnow(),
            metadata={}
        )

