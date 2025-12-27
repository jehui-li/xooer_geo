"""
排序权重评分模块
计算品牌在推荐列表中的排名得分（前三名权重更高）
"""

from typing import List, Optional
from src.models.analysis import ProbeResult
from utils.logger import logger


class RankingScorer:
    """排序权重评分器"""
    
    @staticmethod
    def _calculate_ranking_score(ranking: Optional[int]) -> float:
        """
        根据排名计算单个得分
        
        评分逻辑（0-100分）：
        - 第1名：100分
        - 第2名：90分
        - 第3名：80分
        - 第4-5名：60分
        - 第6-10名：40分
        - 未提及或排名>10：0分
        
        Args:
            ranking: 排名（1-10）或 None
        
        Returns:
            排名得分（0-100）
        """
        if ranking is None:
            return 0.0
        
        if ranking == 1:
            return 100.0
        elif ranking == 2:
            return 90.0
        elif ranking == 3:
            return 80.0
        elif ranking <= 5:
            return 60.0
        elif ranking <= 10:
            return 40.0
        else:
            return 0.0
    
    @staticmethod
    def calculate_ranking_score(probe_results: List[ProbeResult]) -> float:
        """
        计算平均排序权重得分（0-100）
        
        Args:
            probe_results: 探针结果列表
        
        Returns:
            平均排序得分（0-100）
        """
        if not probe_results:
            return 0.0
        
        rankings = [result.target_brand_ranking for result in probe_results if result.has_target_brand]
        
        if not rankings:
            return 0.0
        
        # 计算每个排名的得分，然后取平均值
        scores = [RankingScorer._calculate_ranking_score(ranking) for ranking in rankings]
        average_score = sum(scores) / len(scores)
        
        logger.debug(
            f"Ranking score calculation: {len(rankings)} rankings, "
            f"Average score: {average_score:.2f}"
        )
        
        return round(average_score, 2)
    
    @staticmethod
    def calculate_average_ranking(probe_results: List[ProbeResult]) -> Optional[float]:
        """
        计算平均排名
        
        Args:
            probe_results: 探针结果列表
        
        Returns:
            平均排名（浮点数）或 None（如果从未被提及）
        """
        if not probe_results:
            return None
        
        rankings = [
            result.target_brand_ranking 
            for result in probe_results 
            if result.has_target_brand and result.target_brand_ranking is not None
        ]
        
        if not rankings:
            return None
        
        average = sum(rankings) / len(rankings)
        return round(average, 2)
    
    @staticmethod
    def calculate_top3_count(probe_results: List[ProbeResult]) -> int:
        """
        计算进入前三名的次数
        
        Args:
            probe_results: 探针结果列表
        
        Returns:
            进入前三名的次数
        """
        if not probe_results:
            return 0
        
        top3_count = sum(
            1 for result in probe_results
            if result.has_target_brand 
            and result.target_brand_ranking is not None 
            and result.target_brand_ranking <= 3
        )
        
        return top3_count
    
    @staticmethod
    def calculate(probe_results: List[ProbeResult]) -> dict:
        """
        计算排序相关指标
        
        Args:
            probe_results: 探针结果列表
        
        Returns:
            包含排序相关指标的字典：
            {
                "ranking_score": 80.0,      # 排序得分（0-100）
                "average_ranking": 2.5,     # 平均排名
                "top3_count": 8,            # 进入前三名的次数
                "total_rankings": 10        # 有排名的测试次数
            }
        """
        if not probe_results:
            return {
                "ranking_score": 0.0,
                "average_ranking": None,
                "top3_count": 0,
                "total_rankings": 0
            }
        
        rankings = [
            result.target_brand_ranking 
            for result in probe_results 
            if result.has_target_brand and result.target_brand_ranking is not None
        ]
        
        if not rankings:
            return {
                "ranking_score": 0.0,
                "average_ranking": None,
                "top3_count": 0,
                "total_rankings": 0
            }
        
        # 计算得分
        scores = [RankingScorer._calculate_ranking_score(ranking) for ranking in rankings]
        ranking_score = sum(scores) / len(scores)
        
        # 计算平均排名
        average_ranking = sum(rankings) / len(rankings)
        
        # 计算前三名次数
        top3_count = sum(1 for ranking in rankings if ranking <= 3)
        
        return {
            "ranking_score": round(ranking_score, 2),
            "average_ranking": round(average_ranking, 2),
            "top3_count": top3_count,
            "total_rankings": len(rankings)
        }

