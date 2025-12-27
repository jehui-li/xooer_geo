"""
非确定性处理模块
每个关键词测试 3 次，取平均值
"""

import asyncio
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from datetime import datetime

from src.models.probe import ProbeResponse, ProbeType
from utils.logger import logger

if TYPE_CHECKING:
    from src.probes import ParallelQueryEngine


class NonDeterministicHandler:
    """非确定性处理器（多次采样取平均值）"""
    
    def __init__(
        self,
        num_iterations: int = 3,
        parallel_engine: Optional["ParallelQueryEngine"] = None
    ):
        """
        初始化非确定性处理器
        
        Args:
            num_iterations: 每个关键词测试的次数，默认 3 次
            parallel_engine: 并行查询引擎实例，如果为 None 则创建新实例
        """
        if parallel_engine is None:
            # 延迟导入以避免循环导入
            from src.probes import ParallelQueryEngine
            parallel_engine = ParallelQueryEngine()
        
        self.num_iterations = num_iterations
        self.parallel_engine = parallel_engine
        logger.info(f"Non-deterministic handler initialized with {num_iterations} iterations")
    
    async def test_keyword_multiple_times(
        self,
        query: str,
        probe_type: ProbeType,
        keyword: str,
        temperature: float = 0.7,
        save_to_db: bool = True
    ) -> List[ProbeResponse]:
        """
        对单个查询进行多次测试
        
        Args:
            query: 查询文本
            probe_type: 探针类型
            keyword: 关键词
            temperature: Temperature 参数
            save_to_db: 是否保存到 MongoDB
        
        Returns:
            ProbeResponse 列表（多次测试的结果）
        """
        logger.info(
            f"Testing keyword '{keyword}' {self.num_iterations} times "
            f"with query: {query[:50]}..."
        )
        
        results = []
        for i in range(self.num_iterations):
            logger.debug(f"Iteration {i+1}/{self.num_iterations} for keyword: {keyword}")
            
            result = await self.parallel_engine.query_all_models(
                query=query,
                probe_type=probe_type,
                keyword=keyword,
                temperature=temperature,
                probe_id_prefix=f"{keyword}_{i+1}",
                save_to_db=save_to_db
            )
            
            # 收集所有成功的响应
            results.extend(result["success"])
            
            # 避免 API rate limit，在迭代之间稍微延迟
            if i < self.num_iterations - 1:
                await asyncio.sleep(0.5)
        
        logger.info(
            f"Completed {self.num_iterations} iterations for keyword '{keyword}'. "
            f"Total responses: {len(results)}"
        )
        
        return results
    
    async def process_keyword_with_multiple_tests(
        self,
        query: str,
        probe_type: ProbeType,
        keyword: str,
        temperature: float = 0.7,
        save_to_db: bool = True
    ) -> Dict[str, Any]:
        """
        处理单个关键词（多次测试）
        
        Args:
            query: 查询文本
            probe_type: 探针类型
            keyword: 关键词
            temperature: Temperature 参数
            save_to_db: 是否保存到 MongoDB
        
        Returns:
            处理结果字典，包含多次测试的响应和统计信息
        """
        # 进行多次测试
        probe_responses = await self.test_keyword_multiple_times(
            query=query,
            probe_type=probe_type,
            keyword=keyword,
            temperature=temperature,
            save_to_db=save_to_db
        )
        
        # 统计信息
        total_responses = len(probe_responses)
        unique_models = list(set(response.model for response in probe_responses))
        
        return {
            "keyword": keyword,
            "query": query,
            "num_iterations": self.num_iterations,
            "total_responses": total_responses,
            "unique_models": unique_models,
            "probe_responses": probe_responses,
            "timestamp": datetime.utcnow()
        }
    
    async def process_multiple_keywords(
        self,
        queries: List[str],
        probe_type: ProbeType,
        keywords: List[str],
        temperature: float = 0.7,
        save_to_db: bool = True
    ) -> Dict[str, Dict[str, Any]]:
        """
        处理多个关键词（每个关键词测试多次）
        
        Args:
            queries: 查询文本列表（应该与 keywords 一一对应）
            probe_type: 探针类型
            keywords: 关键词列表
            temperature: Temperature 参数
            save_to_db: 是否保存到 MongoDB
        
        Returns:
            字典，键为关键词，值为处理结果
        """
        if len(queries) != len(keywords):
            raise ValueError("queries and keywords must have the same length")
        
        results = {}
        
        for query, keyword in zip(queries, keywords):
            result = await self.process_keyword_with_multiple_tests(
                query=query,
                probe_type=probe_type,
                keyword=keyword,
                temperature=temperature,
                save_to_db=save_to_db
            )
            results[keyword] = result
        
        return results

