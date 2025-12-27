"""
并行查询引擎
使用 asyncio 并发调用多个模型 API，并将响应存储到 MongoDB
"""

import asyncio
import time
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from src.connectors import (
    get_openai_client,
    get_gemini_client,
    get_perplexity_client,
    get_grok_client
)
from src.models.probe import ProbeResponse, ProbeType, Citation
from src.models.utils import model_to_dict, generate_probe_id
from src.database.db_operations import insert_one
from src.database.mongodb_pool import get_pool
from utils.logger import logger
from utils.cache_manager import get_cache_manager


class ParallelQueryEngine:
    """并行查询引擎，同时向多个模型发送查询"""
    
    # 模型配置映射
    MODEL_CONFIGS = {
        "openai": {
            "client_getter": get_openai_client,
            "model_name": "gpt-4o",
            "method": "simple_query"
        },
        "gemini": {
            "client_getter": get_gemini_client,
            "model_name": "gemini-1.5-pro",
            "method": "simple_query"
        },
        "perplexity": {
            "client_getter": get_perplexity_client,
            "model_name": "llama-3.1-sonar-large-128k-online",
            "method": "simple_query"
        },
        "grok": {
            "client_getter": get_grok_client,
            "model_name": "grok-beta",
            "method": "simple_query"
        }
    }
    
    # MongoDB 集合名称
    COLLECTION_NAME = "probe_responses"
    
    def __init__(self, models: Optional[List[str]] = None, use_cache: bool = True):
        """
        初始化并行查询引擎
        
        Args:
            models: 要使用的模型列表，如果为 None 则使用所有模型
                   可选值：["openai", "gemini", "perplexity", "grok"]
            use_cache: 是否使用缓存，默认 True
        """
        if models is None:
            self.models = list(self.MODEL_CONFIGS.keys())
        else:
            # 验证模型名称
            invalid_models = [m for m in models if m not in self.MODEL_CONFIGS]
            if invalid_models:
                raise ValueError(f"Invalid model names: {invalid_models}. "
                               f"Valid models: {list(self.MODEL_CONFIGS.keys())}")
            self.models = models
        
        self.use_cache = use_cache
        self.cache_manager = get_cache_manager() if use_cache else None
    
    async def _query_single_model(
        self,
        model_name: str,
        query: str,
        temperature: float = 0.7,
        probe_id: str = "",
        probe_type: ProbeType = ProbeType.DIRECT_RECOMMENDATION,
        keyword: str = ""
    ) -> Tuple[Optional[ProbeResponse], Optional[str]]:
        """
        查询单个模型
        
        Args:
            model_name: 模型名称（openai, gemini, perplexity, grok）
            query: 查询文本
            temperature: Temperature 参数
            probe_id: 探针 ID
            probe_type: 探针类型
            keyword: 关键词
        
        Returns:
            (ProbeResponse, error_message) 元组，如果成功则返回响应和 None，失败则返回 None 和错误信息
        """
        config = self.MODEL_CONFIGS[model_name]
        model_full_name = config["model_name"]
        start_time = time.time()
        
        # 检查缓存
        if self.use_cache and self.cache_manager:
            cached_response = self.cache_manager.get(query, model_full_name)
            if cached_response:
                logger.debug(f"Cache hit for {model_name}: {query[:50]}...")
                # 从缓存创建 ProbeResponse
                # 处理 citations
                cached_citations = []
                for cit_data in cached_response.citations:
                    if isinstance(cit_data, dict):
                        cached_citations.append(Citation(**cit_data))
                    elif isinstance(cit_data, Citation):
                        cached_citations.append(cit_data)
                
                probe_response = ProbeResponse(
                    probe_id=probe_id or generate_probe_id(keyword, probe_type.value, 0),
                    probe_type=probe_type,
                    keyword=keyword,
                    model=model_full_name,
                    query=query,
                    temperature=cached_response.temperature,  # 使用缓存的 temperature
                    content=cached_response.content,
                    citations=cached_citations,
                    usage=cached_response.usage,
                    response_time_ms=0,  # 缓存响应时间设为 0
                    timestamp=datetime.utcnow(),
                    metadata={"cached": True, "original_cached_at": str(cached_response.cached_at)}
                )
                return probe_response, None
        
        try:
            # 获取客户端
            client = config["client_getter"]()
            
            # 调用 API
            method = getattr(client, config["method"])
            if model_name == "perplexity":
                # Perplexity 需要 return_citations 参数
                result = await method(
                    query=query,
                    model=config["model_name"],
                    temperature=temperature,
                    return_citations=True
                )
            else:
                result = await method(
                    query=query,
                    model=config["model_name"],
                    temperature=temperature
                )
            
            # 计算响应时间
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # 提取内容
            content = result.get("content", "")
            
            # 提取引用链接（Perplexity 特有）
            citations = []
            if model_name == "perplexity" and "citations" in result:
                # 从 Perplexity 响应中提取原始引用数据
                for cit in result.get("citations", []):
                    # 创建 Citation 对象，类型暂时设为 unknown
                    # 后续可以通过 CitationAnalyzer 进行分类
                    citations.append(Citation(
                        url=cit.get("url", ""),
                        title=cit.get("title", ""),
                        text=cit.get("text", ""),
                        citation_type="unknown"  # 后续可通过 CitationAnalyzer 分析
                    ))
            
            # 提取 usage 信息
            usage = result.get("usage", {})
            
            # 构建 ProbeResponse
            probe_response = ProbeResponse(
                probe_id=probe_id or generate_probe_id(keyword, probe_type.value, 0),
                probe_type=probe_type,
                keyword=keyword,
                model=model_full_name,
                query=query,
                temperature=temperature,
                content=content,
                citations=citations,
                usage=usage,
                response_time_ms=response_time_ms,
                timestamp=datetime.utcnow(),
                metadata={"model_client": model_name}
            )
            
            # 保存到缓存
            if self.use_cache and self.cache_manager:
                try:
                    # 将 Citation 对象转换为字典格式
                    citations_data = []
                    if citations:
                        for cit in citations:
                            if isinstance(cit, Citation):
                                citations_data.append({
                                    "url": cit.url,
                                    "title": cit.title,
                                    "text": cit.text,
                                    "citation_type": cit.citation_type
                                })
                            else:
                                citations_data.append(cit)
                    
                    self.cache_manager.set(
                        query=query,
                        model=model_full_name,
                        temperature=temperature,
                        content=content,
                        citations=citations_data,
                        usage=usage
                    )
                except Exception as e:
                    logger.warning(f"Failed to cache response: {str(e)}")
            
            logger.info(
                f"Successfully queried {model_name} ({model_full_name}). "
                f"Response time: {response_time_ms}ms, Tokens: {usage.get('total_tokens', 0)}"
            )
            
            return probe_response, None
            
        except Exception as e:
            error_msg = f"Error querying {model_name}: {str(e)}"
            logger.error(error_msg)
            return None, error_msg
    
    async def query_all_models(
        self,
        query: str,
        probe_type: ProbeType = ProbeType.DIRECT_RECOMMENDATION,
        keyword: str = "",
        temperature: float = 0.7,
        probe_id_prefix: Optional[str] = None,
        save_to_db: bool = True
    ) -> Dict[str, Any]:
        """
        并行查询所有模型
        
        Args:
            query: 查询文本
            probe_type: 探针类型
            keyword: 关键词
            temperature: Temperature 参数
            probe_id_prefix: 探针 ID 前缀，如果为 None 则自动生成
            save_to_db: 是否保存到 MongoDB，默认 True
        
        Returns:
            包含成功和失败结果的字典：
            {
                "success": [ProbeResponse, ...],
                "failed": [{"model": "openai", "error": "..."}, ...],
                "probe_id": "probe_xxx"
            }
        """
        # 确保 MongoDB 连接池已初始化
        await get_pool()
        
        # 生成探针 ID
        if probe_id_prefix:
            probe_id = probe_id_prefix
        else:
            probe_id = generate_probe_id(keyword, probe_type.value, 0)
        
        logger.info(f"Starting parallel query for probe_id: {probe_id}, query: {query[:50]}...")
        
        # 创建所有模型的查询任务
        tasks = []
        for model_name in self.models:
            task = self._query_single_model(
                model_name=model_name,
                query=query,
                temperature=temperature,
                probe_id=f"{probe_id}_{model_name}",
                probe_type=probe_type,
                keyword=keyword
            )
            tasks.append((model_name, task))
        
        # 并发执行所有查询
        # 注意：不需要 return_exceptions=True，因为 _query_single_model 已经捕获了所有异常
        results = await asyncio.gather(*[task for _, task in tasks])
        
        # 处理结果
        success_responses = []
        failed_models = []
        
        for (model_name, _), result in zip(tasks, results):
            probe_response, error_msg = result
            if probe_response is not None:
                # 保存到 MongoDB
                if save_to_db:
                    try:
                        response_dict = model_to_dict(probe_response)
                        await insert_one(
                            collection_name=self.COLLECTION_NAME,
                            document=response_dict,
                            add_timestamp=False  # ProbeResponse 已经有 timestamp
                        )
                        logger.debug(f"Saved probe response to MongoDB: {probe_response.probe_id}")
                    except Exception as e:
                        logger.error(f"Failed to save probe response to MongoDB: {str(e)}")
                
                success_responses.append(probe_response)
            elif error_msg:
                failed_models.append({
                    "model": model_name,
                    "error": error_msg
                })
        
        logger.info(
            f"Parallel query completed. "
            f"Success: {len(success_responses)}/{len(self.models)}, "
            f"Failed: {len(failed_models)}"
        )
        
        return {
            "success": success_responses,
            "failed": failed_models,
            "probe_id": probe_id,
            "total_models": len(self.models),
            "success_count": len(success_responses),
            "failed_count": len(failed_models)
        }
    
    async def query_multiple_queries(
        self,
        queries: List[str],
        probe_type: ProbeType = ProbeType.DIRECT_RECOMMENDATION,
        keyword: str = "",
        temperature: float = 0.7,
        save_to_db: bool = True
    ) -> List[Dict[str, Any]]:
        """
        批量查询多个问题（串行执行，每个问题并行查询所有模型）
        
        Args:
            queries: 查询文本列表
            probe_type: 探针类型
            keyword: 关键词
            temperature: Temperature 参数
            save_to_db: 是否保存到 MongoDB
        
        Returns:
            每个查询的结果列表
        """
        results = []
        for i, query in enumerate(queries):
            probe_id = generate_probe_id(keyword, probe_type.value, i)
            result = await self.query_all_models(
                query=query,
                probe_type=probe_type,
                keyword=keyword,
                temperature=temperature,
                probe_id_prefix=probe_id,
                save_to_db=save_to_db
            )
            results.append(result)
            
            # 避免 API rate limit，每个查询之间稍微延迟
            if i < len(queries) - 1:
                await asyncio.sleep(0.5)
        
        return results

