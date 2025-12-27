"""
GEO Agent 工作流编排
使用 LangGraph 实现简单的链式流程
"""

from typing import Dict, Any, List, Optional, TypedDict
from datetime import datetime

from langgraph.graph import StateGraph, END

from src.probes import ProbeGenerator, ParallelQueryEngine
from src.probes.probe_generator import Language
from src.models.probe import ProbeType
from src.analyzers import EntityExtractor
from src.scorers import GeoScorer
from src.strategists import StrategyAgent
from src.models.utils import generate_audit_id
from src.database.mongodb_pool import get_pool
from utils.logger import logger


class WorkflowState(TypedDict):
    """工作流状态"""
    audit_id: str
    brand_name: str
    target_brand: str
    keywords: List[str]
    probe_queries: Dict[str, List[str]]  # keyword -> queries
    probe_responses: List[Any]  # ProbeResponse 列表
    probe_results: List[Any]  # ProbeResult 列表
    geo_score: Optional[Any]  # GeoScore
    strategy: Optional[Any]  # Strategy
    error: Optional[str]
    metadata: Dict[str, Any]


class GeoWorkflow:
    """GEO Agent 工作流"""
    
    def __init__(
        self,
        target_website: Optional[str] = None,
        ground_truth: Optional[Dict[str, Any]] = None
    ):
        """
        初始化工作流
        
        Args:
            target_website: 目标品牌官网 URL（用于引用链接分析）
            ground_truth: 品牌的真实数据（用于准确度检查）
        """
        self.probe_generator = ProbeGenerator(default_language=Language.EN)
        self.parallel_engine = ParallelQueryEngine(use_cache=True)
        self.entity_extractor = EntityExtractor(
            target_website=target_website,
            ground_truth=ground_truth
        )
        self.geo_scorer = GeoScorer()
        self.strategy_agent = StrategyAgent()
        self.target_website = target_website
        self.ground_truth = ground_truth
    
    async def generate_probes(
        self,
        state: WorkflowState
    ) -> WorkflowState:
        """
        步骤1：生成探针查询
        
        Args:
            state: 工作流状态
        
        Returns:
            更新后的状态
        """
        logger.info(f"Step 1: Generating probes for keywords: {state['keywords']}")
        
        try:
            probe_queries = {}
            for keyword in state["keywords"]:
                # 生成三类探针
                queries = self.probe_generator.generate_all_types(
                    keyword=keyword,
                    target_brand=state["target_brand"]
                )
                probe_queries[keyword] = list(queries.values())
            
            state["probe_queries"] = probe_queries
            logger.info(f"Generated {sum(len(q) for q in probe_queries.values())} probe queries")
            
        except Exception as e:
            logger.error(f"Failed to generate probes: {str(e)}")
            state["error"] = f"Failed to generate probes: {str(e)}"
        
        return state
    
    async def query_models(
        self,
        state: WorkflowState
    ) -> WorkflowState:
        """
        步骤2：并行查询模型
        
        Args:
            state: 工作流状态
        
        Returns:
            更新后的状态
        """
        logger.info("Step 2: Querying models in parallel")
        
        if state.get("error"):
            return state
        
        try:
            probe_responses = []
            
            for keyword, queries in state["probe_queries"].items():
                for query in queries:
                    # 确定探针类型
                    probe_type = ProbeType.DIRECT_RECOMMENDATION
                    if "compare" in query.lower() or "对比" in query:
                        probe_type = ProbeType.ATTRIBUTE_COMPARISON
                    elif "how to" in query.lower() or "如何" in query:
                        probe_type = ProbeType.SOLUTION_BASED
                    
                    # 并行查询所有模型
                    result = await self.parallel_engine.query_all_models(
                        query=query,
                        probe_type=probe_type,
                        keyword=keyword,
                        temperature=0.7,
                        save_to_db=True
                    )
                    probe_responses.extend(result["success"])
            
            state["probe_responses"] = probe_responses
            logger.info(f"Retrieved {len(probe_responses)} probe responses")
            
            # 诊断日志：检查查询结果
            if not probe_responses:
                logger.warning("No probe responses retrieved - check query_models step!")
            else:
                logger.info(f"Probe responses sample: first response has content length {len(probe_responses[0].content) if hasattr(probe_responses[0], 'content') else 0}")
            
        except Exception as e:
            logger.error(f"Failed to query models: {str(e)}")
            state["error"] = f"Failed to query models: {str(e)}"
        
        return state
    
    async def extract_entities(
        self,
        state: WorkflowState
    ) -> WorkflowState:
        """
        步骤3：提取实体
        
        Args:
            state: 工作流状态
        
        Returns:
            更新后的状态
        """
        logger.info("Step 3: Extracting entities")
        
        if state.get("error"):
            return state
        
        try:
            probe_results = []
            
            for probe_response in state["probe_responses"]:
                result = await self.entity_extractor.extract_from_probe_response(
                    probe_response=probe_response,
                    target_brand=state["target_brand"]
                )
                probe_results.append(result)
            
            state["probe_results"] = probe_results
            logger.info(f"Extracted entities from {len(probe_results)} probe responses")
            
            # 诊断日志：检查提取的结果
            if probe_results:
                mentioned_count = sum(1 for r in probe_results if r.has_target_brand)
                logger.info(
                    f"Entity extraction summary: "
                    f"Total results: {len(probe_results)}, "
                    f"Target brand mentioned: {mentioned_count}/{len(probe_results)}"
                )
            else:
                logger.warning("No probe results extracted - this will result in zero GEO Score!")
            
        except Exception as e:
            logger.error(f"Failed to extract entities: {str(e)}")
            state["error"] = f"Failed to extract entities: {str(e)}"
        
        return state
    
    async def calculate_score(
        self,
        state: WorkflowState
    ) -> WorkflowState:
        """
        步骤4：计算 GEO Score™
        
        Args:
            state: 工作流状态
        
        Returns:
            更新后的状态
        """
        logger.info("Step 4: Calculating GEO Score™")
        
        if state.get("error"):
            return state
        
        try:
            geo_score = self.geo_scorer.calculate_geo_score(state["probe_results"])
            state["geo_score"] = geo_score
            logger.info(f"GEO Score™ calculated: {geo_score.overall_score}")
            
        except Exception as e:
            logger.error(f"Failed to calculate GEO Score™: {str(e)}")
            state["error"] = f"Failed to calculate GEO Score™: {str(e)}"
        
        return state
    
    async def generate_strategy(
        self,
        state: WorkflowState
    ) -> WorkflowState:
        """
        步骤5：生成策略
        
        Args:
            state: 工作流状态
        
        Returns:
            更新后的状态
        """
        logger.info("Step 5: Generating strategy")
        
        if state.get("error") or not state.get("geo_score"):
            return state
        
        try:
            strategy = await self.strategy_agent.generate_strategy(
                geo_score=state["geo_score"],
                brand_name=state["brand_name"],
                audit_id=state["audit_id"]
            )
            state["strategy"] = strategy
            logger.info(f"Strategy generated with {len(strategy.recommendations)} recommendations")
            
        except Exception as e:
            logger.error(f"Failed to generate strategy: {str(e)}")
            state["error"] = f"Failed to generate strategy: {str(e)}"
        
        return state
    
    def build_graph(self) -> StateGraph:
        """
        构建工作流图（简单链式流程）
        
        Returns:
            StateGraph 实例
        """
        workflow = StateGraph(WorkflowState)
        
        # 添加节点（按顺序）
        workflow.add_node("generate_probes", self.generate_probes)
        workflow.add_node("query_models", self.query_models)
        workflow.add_node("extract_entities", self.extract_entities)
        workflow.add_node("calculate_score", self.calculate_score)
        workflow.add_node("generate_strategy", self.generate_strategy)
        
        # 定义流程（简单链式）
        workflow.set_entry_point("generate_probes")
        workflow.add_edge("generate_probes", "query_models")
        workflow.add_edge("query_models", "extract_entities")
        workflow.add_edge("extract_entities", "calculate_score")
        workflow.add_edge("calculate_score", "generate_strategy")
        workflow.add_edge("generate_strategy", END)
        
        return workflow.compile()
    
    async def run(
        self,
        brand_name: str,
        target_brand: str,
        keywords: List[str],
        audit_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        运行完整工作流
        
        Args:
            brand_name: 品牌名称
            target_brand: 目标品牌名称
            keywords: 关键词列表
            audit_id: 审计 ID（可选，如果不提供则自动生成）
        
        Returns:
            工作流执行结果
        """
        # 初始化状态
        if audit_id is None:
            audit_id = generate_audit_id(brand_name)
        
        initial_state: WorkflowState = {
            "audit_id": audit_id,
            "brand_name": brand_name,
            "target_brand": target_brand,
            "keywords": keywords,
            "probe_queries": {},
            "probe_responses": [],
            "probe_results": [],
            "geo_score": None,
            "strategy": None,
            "error": None,
            "metadata": {}
        }
        
        # 确保 MongoDB 连接
        await get_pool()
        
        # 构建并运行工作流
        graph = self.build_graph()
        final_state = await graph.ainvoke(initial_state)
        
        return final_state

