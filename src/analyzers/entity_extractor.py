"""
实体识别模块
使用大模型 JSON Mode 从 LLM 响应中提取结构化数据
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.connectors import get_openai_client
from src.models.probe import ProbeResponse, Citation
from src.models.analysis import ProbeResult, BrandMention, Sentiment
from src.models.utils import model_to_dict
from src.analyzers.citation_analyzer import CitationAnalyzer
from src.analyzers.accuracy_checker import AccuracyChecker
from utils.logger import logger


class EntityExtractor:
    """实体识别器，使用大模型 JSON Mode 提取结构化数据"""
    
    # 提取提示词模板
    EXTRACTION_PROMPT_TEMPLATE = """你是一个专业的数据提取助手。请从以下 AI 模型的回答中提取品牌提及信息。

原始查询：{query}
目标品牌：{target_brand}
关键词：{keyword}

AI 模型的回答：
{content}

请提取以下信息，并以 JSON 格式返回：
1. 提取所有提到的品牌名称
2. 对于每个品牌，判断是否为目标品牌（品牌名称可能略有不同，需要智能匹配）
3. 如果提到了目标品牌，记录其在推荐列表中的排名（1-10），如果不在列表中则标记为 null
4. 分析目标品牌的情感倾向（positive/neutral/negative）
5. 提取目标品牌的提及文本片段
6. 提取目标品牌的产品属性（价格、功能特点等，如果有的话）

返回的 JSON 格式必须严格遵循以下结构：
{{
  "target_brand": {{
    "is_mentioned": true/false,
    "ranking": 1-10 或 null,
    "sentiment": "positive"/"neutral"/"negative" 或 null,
    "mention_text": "提及的文本片段" 或 null,
    "attributes": {{"key": "value"}} 或 {{}}
  }},
  "all_brands": [
    {{
      "brand_name": "品牌名称",
      "ranking": 1-10 或 null,
      "sentiment": "positive"/"neutral"/"negative",
      "mention_text": "提及的文本片段"
    }}
  ],
  "total_brands_count": 数字
}}

注意：
- 如果目标品牌没有被提及，target_brand.is_mentioned 为 false，其他字段为 null
- ranking 表示在推荐列表中的位置，1 表示第一名，2 表示第二名，以此类推
- 如果回答中没有明确的列表顺序，ranking 可以为 null
- sentiment 必须从文本内容中判断，如果没有明确的情感倾向，使用 "neutral"
- mention_text 应该是包含目标品牌名称的关键句子或段落
"""
    
    def __init__(
        self,
        model: str = "gpt-4o",
        temperature: float = 0.0,
        target_brand: Optional[str] = None,
        target_website: Optional[str] = None,
        ground_truth: Optional[Dict[str, Any]] = None
    ):
        """
        初始化实体识别器
        
        Args:
            model: 用于提取的模型名称，默认 "gpt-4o"
            temperature: Temperature 参数，默认 0.0（确保输出稳定）
            target_brand: 目标品牌名称（用于引用链接分析和准确度检查）
            target_website: 目标品牌官网 URL（用于引用链接分析）
            ground_truth: 品牌的真实数据（Ground Truth），用于准确度检查
        """
        self.model = model
        self.temperature = temperature
        self.client = get_openai_client()
        self.citation_analyzer = CitationAnalyzer(
            target_brand=target_brand,
            target_website=target_website
        )
        self.accuracy_checker = AccuracyChecker(
            target_brand=target_brand or "",
            ground_truth=ground_truth
        ) if target_brand else None
    
    def _build_extraction_prompt(
        self,
        query: str,
        content: str,
        target_brand: str,
        keyword: str
    ) -> str:
        """
        构建提取提示词
        
        Args:
            query: 原始查询
            content: AI 模型的回答内容
            target_brand: 目标品牌名称
            keyword: 关键词
        
        Returns:
            完整的提示词
        """
        return self.EXTRACTION_PROMPT_TEMPLATE.format(
            query=query,
            content=content,
            target_brand=target_brand,
            keyword=keyword
        )
    
    async def _extract_with_llm(
        self,
        query: str,
        content: str,
        target_brand: str,
        keyword: str
    ) -> Dict[str, Any]:
        """
        使用 LLM 提取实体信息
        
        Args:
            query: 原始查询
            content: AI 模型的回答内容
            target_brand: 目标品牌名称
            keyword: 关键词
        
        Returns:
            提取的结构化数据（字典）
        
        Raises:
            Exception: 如果提取失败或返回的 JSON 格式不正确
        """
        prompt = self._build_extraction_prompt(query, content, target_brand, keyword)
        
        messages = [
            {
                "role": "system",
                "content": "You are a professional data extraction assistant. Always respond with valid JSON only, no additional text."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        json_content = ""
        try:
            # 调用 OpenAI API，使用 JSON Mode
            response = await self.client.chat_completion(
                messages=messages,
                model=self.model,
                temperature=self.temperature,
                response_format={"type": "json_object"}  # JSON Mode
            )
            
            # 解析 JSON 响应
            json_content = response.get("content", "").strip()
            
            # 尝试解析 JSON（可能包含 markdown 代码块）
            if json_content.startswith("```json"):
                # 移除 markdown 代码块标记
                json_content = json_content.replace("```json", "").replace("```", "").strip()
            elif json_content.startswith("```"):
                json_content = json_content.replace("```", "").strip()
            
            extracted_data = json.loads(json_content)
            
            logger.debug(f"Successfully extracted entities for target brand: {target_brand}")
            return extracted_data
            
        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse JSON from LLM response: {str(e)}"
            logger.error(error_msg)
            if json_content:
                logger.error(f"Response content (first 500 chars): {json_content[:500]}...")
            raise Exception(f"Invalid JSON response from LLM: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to extract entities: {str(e)}")
            raise
    
    def _parse_extracted_data(
        self,
        extracted_data: Dict[str, Any],
        target_brand: str,
        citations: List[Citation]
    ) -> Dict[str, Any]:
        """
        解析提取的数据并返回结构化信息
        
        Args:
            extracted_data: 从 LLM 提取的原始数据
            target_brand: 目标品牌名称
            citations: 引用链接列表
        
        Returns:
            包含解析后数据的字典
        """
        target_info = extracted_data.get("target_brand", {})
        all_brands_data = extracted_data.get("all_brands", [])
        total_count = extracted_data.get("total_brands_count", len(all_brands_data))
        
        # 构建品牌提及列表
        brand_mentions = []
        for brand_data in all_brands_data:
            brand_name = brand_data.get("brand_name", "")
            if not brand_name:
                continue
            
            # 判断情感
            sentiment_str = brand_data.get("sentiment", "neutral")
            try:
                sentiment = Sentiment(sentiment_str.lower())
            except ValueError:
                sentiment = Sentiment.NEUTRAL
            
            brand_mention = BrandMention(
                brand_name=brand_name,
                is_mentioned=True,
                ranking=brand_data.get("ranking"),
                sentiment=sentiment,
                mention_text=brand_data.get("mention_text"),
                citations=[],
                attributes={},
                accuracy_score=None,
                hallucination_risk=False
            )
            brand_mentions.append(brand_mention)
        
        # 提取目标品牌信息
        is_target_mentioned = target_info.get("is_mentioned", False)
        target_ranking = target_info.get("ranking") if is_target_mentioned else None
        
        # 提取目标品牌情感
        target_sentiment_str = target_info.get("sentiment")
        target_sentiment = None
        if target_sentiment_str:
            try:
                target_sentiment = Sentiment(target_sentiment_str.lower())
            except ValueError:
                target_sentiment = Sentiment.NEUTRAL
        
        # 统计引用链接（官网和权威来源）
        # 如果引用链接还未分类，使用 CitationAnalyzer 进行分析
        # 注意：如果 target_brand 与初始化时不同，需要使用传入的 target_brand
        # 这里使用传入的 target_brand 创建临时的 analyzer（如果初始化时没有指定）
        analyzer = self.citation_analyzer
        if not analyzer.target_brand and target_brand:
            # 如果初始化时没有指定 target_brand，创建一个临时的 analyzer
            analyzer = CitationAnalyzer(target_brand=target_brand)
        
        analyzed_citations = []
        for citation in citations:
            if citation.citation_type == "unknown":
                # 重新分类
                citation_type = analyzer.classify_citation_type(citation.url)
                citation.citation_type = citation_type
            analyzed_citations.append(citation)
        
        # 使用 CitationAnalyzer 统计
        official_citations_count = analyzer.get_official_citations_count(analyzed_citations)
        authoritative_citations_count = analyzer.get_authoritative_citations_count(analyzed_citations)
        
        return {
            "brand_mentions": brand_mentions,
            "total_mentions": total_count,
            "has_target_brand": is_target_mentioned,
            "target_brand_ranking": target_ranking,
            "target_brand_sentiment": target_sentiment,
            "official_citations_count": official_citations_count,
            "authoritative_citations_count": authoritative_citations_count,
            "target_brand_mention_text": target_info.get("mention_text"),
            "target_brand_attributes": target_info.get("attributes", {})
        }
    
    async def extract_from_probe_response(
        self,
        probe_response: ProbeResponse,
        target_brand: str
    ) -> ProbeResult:
        """
        从 ProbeResponse 中提取实体信息
        
        Args:
            probe_response: 探针响应对象
            target_brand: 目标品牌名称
        
        Returns:
            ProbeResult 对象
        """
        logger.info(f"Extracting entities from probe response: {probe_response.probe_id}")
        
        try:
            # 使用 LLM 提取实体
            extracted_data = await self._extract_with_llm(
                query=probe_response.query,
                content=probe_response.content,
                target_brand=target_brand,
                keyword=probe_response.keyword
            )
            
            # 解析提取的数据
            parsed_data = self._parse_extracted_data(
                extracted_data=extracted_data,
                target_brand=target_brand,
                citations=probe_response.citations
            )
            
            # 构建完整的 ProbeResult
            probe_result = ProbeResult(
                probe_id=probe_response.probe_id,
                probe_type=probe_response.probe_type.value,
                keyword=probe_response.keyword,
                model=probe_response.model,
                temperature=probe_response.temperature,
                brand_mentions=parsed_data["brand_mentions"],
                total_mentions=parsed_data["total_mentions"],
                has_target_brand=parsed_data["has_target_brand"],
                target_brand_ranking=parsed_data["target_brand_ranking"],
                target_brand_sentiment=parsed_data["target_brand_sentiment"],
                official_citations_count=parsed_data["official_citations_count"],
                authoritative_citations_count=parsed_data["authoritative_citations_count"],
                timestamp=datetime.utcnow()
            )
            
            # 如果目标品牌被提及，更新其品牌提及信息，并进行准确度检查
            if parsed_data["has_target_brand"]:
                target_brand_mention = None
                for brand_mention in probe_result.brand_mentions:
                    if brand_mention.brand_name.lower() == target_brand.lower():
                        target_brand_mention = brand_mention
                        # 更新目标品牌的提及文本和属性
                        if parsed_data.get("target_brand_mention_text"):
                            brand_mention.mention_text = parsed_data["target_brand_mention_text"]
                        if parsed_data.get("target_brand_attributes"):
                            brand_mention.attributes = parsed_data["target_brand_attributes"]
                        break
                
                if not target_brand_mention:
                    # 如果目标品牌没有在 all_brands 中找到，创建一个新的 BrandMention
                    target_brand_mention = BrandMention(
                        brand_name=target_brand,
                        is_mentioned=True,
                        ranking=parsed_data["target_brand_ranking"],
                        sentiment=parsed_data["target_brand_sentiment"] or Sentiment.NEUTRAL,
                        mention_text=parsed_data.get("target_brand_mention_text"),
                        citations=probe_response.citations,
                        attributes=parsed_data.get("target_brand_attributes", {}),
                        accuracy_score=None,
                        hallucination_risk=False
                    )
                    probe_result.brand_mentions.append(target_brand_mention)
                
                # 进行内容准确度检查
                if self.accuracy_checker and target_brand_mention:
                    accuracy_result = self.accuracy_checker.check_accuracy(
                        content=probe_response.content,
                        mention_text=target_brand_mention.mention_text
                    )
                    target_brand_mention.accuracy_score = accuracy_result["accuracy_score"]
                    target_brand_mention.hallucination_risk = accuracy_result["hallucination_risk"]
                    
                    # 如果提供了属性，也检查属性的准确度
                    if target_brand_mention.attributes:
                        attributes_result = self.accuracy_checker.check_attributes_accuracy(
                            attributes=target_brand_mention.attributes,
                            content=target_brand_mention.mention_text
                        )
                        # 可以合并属性检查的结果（这里简化处理，使用内容检查的结果）
                        if attributes_result["accuracy_score"] < accuracy_result["accuracy_score"]:
                            target_brand_mention.accuracy_score = attributes_result["accuracy_score"]
                        if attributes_result["hallucination_risk"]:
                            target_brand_mention.hallucination_risk = True
            
            logger.info(
                f"Entity extraction completed. "
                f"Target brand mentioned: {probe_result.has_target_brand}, "
                f"Ranking: {probe_result.target_brand_ranking}, "
                f"Total brands: {probe_result.total_mentions}"
            )
            
            return probe_result
            
        except Exception as e:
            logger.error(f"Failed to extract entities from probe response {probe_response.probe_id}: {str(e)}")
            # 返回一个基础的 ProbeResult，标记为失败
            return ProbeResult(
                probe_id=probe_response.probe_id,
                probe_type=probe_response.probe_type.value,
                keyword=probe_response.keyword,
                model=probe_response.model,
                temperature=probe_response.temperature,
                brand_mentions=[],
                total_mentions=0,
                has_target_brand=False,
                target_brand_ranking=None,
                target_brand_sentiment=None,
                official_citations_count=0,
                authoritative_citations_count=0,
                timestamp=datetime.utcnow()
            )
    
    async def extract_batch(
        self,
        probe_responses: List[ProbeResponse],
        target_brand: str
    ) -> List[ProbeResult]:
        """
        批量提取实体信息
        
        Args:
            probe_responses: 探针响应列表
            target_brand: 目标品牌名称
        
        Returns:
            ProbeResult 列表
        """
        results = []
        for probe_response in probe_responses:
            result = await self.extract_from_probe_response(probe_response, target_brand)
            results.append(result)
        return results

