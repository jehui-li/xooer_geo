"""
SOM（模型占有率）评分模块
计算品牌在多次测试中出现的频率
"""

from typing import List
from src.models.analysis import ProbeResult
from utils.logger import logger


class SOMScorer:
    """SOM（模型占有率）评分器"""
    
    @staticmethod
    def calculate_som_percentage(probe_results: List[ProbeResult]) -> float:
        """
        计算 SOM 百分比（出现频率）
        
        Args:
            probe_results: 探针结果列表
        
        Returns:
            SOM 百分比（0-100），表示品牌被提及的频率
        """
        if not probe_results:
            return 0.0
        
        total_tests = len(probe_results)
        mentioned_count = sum(1 for result in probe_results if result.has_target_brand)
        
        som_percentage = (mentioned_count / total_tests) * 100.0
        
        logger.debug(
            f"SOM calculation: {mentioned_count}/{total_tests} tests mentioned target brand. "
            f"SOM percentage: {som_percentage:.2f}%"
        )
        
        return round(som_percentage, 2)
    
    @staticmethod
    def calculate_som_score(probe_results: List[ProbeResult]) -> float:
        """
        计算 SOM 得分（0-100）
        
        Args:
            probe_results: 探针结果列表
        
        Returns:
            SOM 得分（0-100），等于 SOM 百分比
        """
        som_percentage = SOMScorer.calculate_som_percentage(probe_results)
        # SOM 得分直接等于百分比
        return som_percentage
    
    @staticmethod
    def calculate(probe_results: List[ProbeResult]) -> dict:
        """
        计算 SOM 相关指标
        
        Args:
            probe_results: 探针结果列表
        
        Returns:
            包含 SOM 相关指标的字典：
            {
                "som_percentage": 85.0,  # 百分比
                "som_score": 85.0,       # 得分（0-100）
                "mentioned_count": 42,   # 提及次数
                "total_tests": 50        # 总测试次数
            }
        """
        if not probe_results:
            return {
                "som_percentage": 0.0,
                "som_score": 0.0,
                "mentioned_count": 0,
                "total_tests": 0
            }
        
        total_tests = len(probe_results)
        mentioned_count = sum(1 for result in probe_results if result.has_target_brand)
        som_percentage = (mentioned_count / total_tests) * 100.0
        som_score = som_percentage
        
        return {
            "som_percentage": round(som_percentage, 2),
            "som_score": round(som_score, 2),
            "mentioned_count": mentioned_count,
            "total_tests": total_tests
        }

