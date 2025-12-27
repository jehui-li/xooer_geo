"""
内容准确度评分模块
计算内容准确度得分，考虑幻觉风险
"""

from typing import List, Optional
from src.models.analysis import ProbeResult
from utils.logger import logger


class AccuracyScorer:
    """内容准确度评分器"""
    
    @staticmethod
    def calculate_accuracy_score(probe_results: List[ProbeResult]) -> float:
        """
        计算内容准确度得分（0-100）
        
        评分逻辑：
        - 从每个 ProbeResult 中的 BrandMention 获取 accuracy_score（0-1）
        - 转换为 0-100 分制
        - 如果存在幻觉风险，扣减分数
        - 计算平均值
        
        Args:
            probe_results: 探针结果列表
        
        Returns:
            准确度得分（0-100）
        """
        if not probe_results:
            return 0.0
        
        accuracy_scores = []
        hallucination_count = 0
        
        for result in probe_results:
            if not result.has_target_brand:
                continue
            
            # 查找目标品牌的提及信息
            has_hallucination_in_result = False
            for brand_mention in result.brand_mentions:
                if brand_mention.accuracy_score is not None:
                    # 转换为 0-100 分制
                    score = brand_mention.accuracy_score * 100.0
                    accuracy_scores.append(score)
                    
                    # 如果存在幻觉风险，记录（每个结果只计数一次）
                    if brand_mention.hallucination_risk and not has_hallucination_in_result:
                        hallucination_count += 1
                        has_hallucination_in_result = True
        
        if not accuracy_scores:
            return 0.0
        
        # 计算平均得分
        average_score = sum(accuracy_scores) / len(accuracy_scores)
        
        # 应用幻觉惩罚（每个幻觉风险扣 10 分，平均分摊）
        if hallucination_count > 0:
            penalty_per_score = (hallucination_count * 10.0) / len(accuracy_scores)
            average_score = max(0.0, average_score - penalty_per_score)
        
        logger.debug(
            f"Accuracy score calculation: {len(accuracy_scores)} scores, "
            f"Average: {average_score:.2f}, Hallucination count: {hallucination_count}"
        )
        
        return round(average_score, 2)
    
    @staticmethod
    def calculate_accuracy_percentage(probe_results: List[ProbeResult]) -> float:
        """
        计算准确度百分比（0-100）
        
        等同于 accuracy_score
        
        Args:
            probe_results: 探针结果列表
        
        Returns:
            准确度百分比（0-100）
        """
        return AccuracyScorer.calculate_accuracy_score(probe_results)
    
    @staticmethod
    def calculate_hallucination_count(probe_results: List[ProbeResult]) -> int:
        """
        计算幻觉风险数量
        
        Args:
            probe_results: 探针结果列表
        
        Returns:
            存在幻觉风险的测试次数
        """
        if not probe_results:
            return 0
        
        hallucination_count = 0
        for result in probe_results:
            if not result.has_target_brand:
                continue
            
            for brand_mention in result.brand_mentions:
                if brand_mention.hallucination_risk:
                    hallucination_count += 1
                    break  # 每个结果只计数一次
        
        return hallucination_count
    
    @staticmethod
    def calculate(probe_results: List[ProbeResult]) -> dict:
        """
        计算准确度相关指标
        
        Args:
            probe_results: 探针结果列表
        
        Returns:
            包含准确度相关指标的字典：
            {
                "accuracy_score": 90.0,        # 准确度得分（0-100）
                "accuracy_percentage": 90.0,   # 准确度百分比
                "hallucination_count": 1,      # 幻觉风险数量
                "total_checked": 10            # 检查的测试次数
            }
        """
        if not probe_results:
            return {
                "accuracy_score": 0.0,
                "accuracy_percentage": 0.0,
                "hallucination_count": 0,
                "total_checked": 0
            }
        
        accuracy_scores = []
        hallucination_count = 0
        
        for result in probe_results:
            if not result.has_target_brand:
                continue
            
            has_hallucination = False
            for brand_mention in result.brand_mentions:
                if brand_mention.accuracy_score is not None:
                    score = brand_mention.accuracy_score * 100.0
                    accuracy_scores.append(score)
                
                if brand_mention.hallucination_risk and not has_hallucination:
                    hallucination_count += 1
                    has_hallucination = True
        
        if not accuracy_scores:
            return {
                "accuracy_score": 0.0,
                "accuracy_percentage": 0.0,
                "hallucination_count": hallucination_count,
                "total_checked": 0
            }
        
        # 计算平均得分并应用幻觉惩罚
        average_score = sum(accuracy_scores) / len(accuracy_scores)
        if hallucination_count > 0:
            average_score = max(0.0, average_score - (hallucination_count * 10.0 / len(accuracy_scores)))
        
        return {
            "accuracy_score": round(average_score, 2),
            "accuracy_percentage": round(average_score, 2),
            "hallucination_count": hallucination_count,
            "total_checked": len(accuracy_scores)
        }

