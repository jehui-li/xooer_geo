"""
策略生成 Agent
使用 GPT-4o 根据 GEO Score™ 生成优化策略建议
"""

import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from src.connectors import get_openai_client
from src.models.scoring import GeoScore, ScoreBreakdown
from src.models.strategy import Strategy, StrategyRecommendation
from src.models.utils import generate_strategy_id
from utils.logger import logger


class StrategyAgent:
    """策略生成 Agent"""
    
    # 策略提示词模板
    STRATEGY_PROMPT_TEMPLATE = """你是一个专业的 GEO（生成式引擎优化）策略顾问。基于提供的 GEO Score™ 评分结果，为品牌生成具体的优化策略建议。

当前 GEO Score™ 评分：
- 总体得分：{overall_score}/100
- SOM（模型占有率）：{som_score}/100 (权重 40%)
- 权威引文比：{citation_score}/100 (权重 30%)
- 排序权重：{ranking_score}/100 (权重 20%)
- 内容准确度：{accuracy_score}/100 (权重 10%)

评分明细：
- SOM 百分比：{som_percentage}% (提及 {mentioned_count}/{total_tests} 次)
- 官网引用：{official_citations} 个
- 权威来源引用：{authoritative_citations} 个
- 平均排名：{average_ranking}
- 进入前三名次数：{top3_count} 次
- 幻觉风险数量：{hallucination_count} 次

品牌信息：
- 品牌名称：{brand_name}
- 测试模型：{models_tested}
- 测试关键词：{keywords_tested}

请根据以上评分结果，生成优化策略建议。重点关注得分较低的维度，提供具体、可执行的建议。

策略建议规则：
1. **SOM（模型占有率）低（<60%）**：
   - 建议增加在权威第三方媒体（Reddit, Wikipedia, 行业 Blog）的软文曝光
   - 建议在相关论坛和社区建立品牌存在感
   - 建议发布高质量的内容营销文章

2. **权威引文比低（<50%）**：
   - 建议优化网站的 Schema Markup 标记
   - 建议添加结构化数据（JSON-LD）
   - 建议在官方网站上提供清晰的产品信息
   - 建议建立权威的第三方引用（如 Wikipedia 条目）

3. **排序权重低（<60%）**：
   - 建议提升品牌在行业中的知名度
   - 建议优化产品描述和关键词使用
   - 建议建立更多高质量的外部链接

4. **内容准确度低（<70%）或有幻觉风险**：
   - 建议启动「防御性 GEO」，发布更强的事实性文档供 AI 抓取
   - 建议在官网明确标注产品信息（价格、功能等）
   - 建议创建 FAQ 页面和产品文档
   - 建议使用 Schema.org 标记确保信息准确性

请以 JSON 格式返回策略建议，格式如下：
{{
  "summary": "策略摘要（1-2 句话）",
  "focus_areas": ["som", "citation", "ranking", "accuracy"]（重点关注领域，最多 3 个）,
  "recommendations": [
    {{
      "category": "som"/"citation"/"ranking"/"accuracy"/"general",
      "priority": "high"/"medium"/"low",
      "title": "建议标题",
      "description": "详细描述（2-3 句话）",
      "action_items": ["行动项1", "行动项2", "行动项3"],
      "expected_impact": "预期影响描述（如：提高 20-30% 的 SOM 得分）",
      "implementation_difficulty": "easy"/"medium"/"hard",
      "estimated_time": "预计实施时间（如：1-2 周）",
      "code_examples": {{}}（可选，如果有代码示例）,
      "resources": ["资源链接1", "资源链接2"]（可选）
    }}
  ]
}}

要求：
- 生成 3-5 个策略建议
- 根据得分情况确定优先级（得分越低的维度，优先级越高）
- 提供具体、可执行的行动项
- 评估实施难度和预期时间
- 如果涉及技术实现（如 Schema Markup），可以提供代码示例
"""
    
    def __init__(self, model: str = "gpt-4o", temperature: float = 0.7):
        """
        初始化策略 Agent
        
        Args:
            model: 使用的模型名称，默认 "gpt-4o"
            temperature: Temperature 参数，默认 0.7
        """
        self.model = model
        self.temperature = temperature
        self.client = get_openai_client()
    
    def _build_strategy_prompt(self, geo_score: GeoScore, brand_name: str) -> str:
        """
        构建策略生成提示词
        
        Args:
            geo_score: GEO Score™ 评分结果
            brand_name: 品牌名称
        
        Returns:
            完整的提示词
        """
        breakdown = geo_score.breakdown
        
        # 提取提及次数和总测试次数（从 SOM 数据推断）
        mentioned_count = int(breakdown.som_percentage * geo_score.test_count / 100)
        total_tests = geo_score.test_count
        
        # 格式化模型和关键词列表
        models_tested = ", ".join(geo_score.models_tested) if geo_score.models_tested else "N/A"
        keywords_tested = ", ".join(geo_score.keywords_tested) if geo_score.keywords_tested else "N/A"
        
        # 处理平均排名
        average_ranking_str = f"{breakdown.average_ranking}" if breakdown.average_ranking else "N/A"
        
        return self.STRATEGY_PROMPT_TEMPLATE.format(
            overall_score=geo_score.overall_score,
            som_score=breakdown.som_score,
            citation_score=breakdown.citation_score,
            ranking_score=breakdown.ranking_score,
            accuracy_score=breakdown.accuracy_score,
            som_percentage=breakdown.som_percentage,
            mentioned_count=mentioned_count,
            total_tests=total_tests,
            official_citations=breakdown.official_citations,
            authoritative_citations=breakdown.authoritative_citations,
            average_ranking=average_ranking_str,
            top3_count=breakdown.top3_count,
            hallucination_count=breakdown.hallucination_count,
            brand_name=brand_name,
            models_tested=models_tested,
            keywords_tested=keywords_tested
        )
    
    async def _generate_strategy_with_llm(
        self,
        geo_score: GeoScore,
        brand_name: str
    ) -> Dict[str, Any]:
        """
        使用 LLM 生成策略建议
        
        Args:
            geo_score: GEO Score™ 评分结果
            brand_name: 品牌名称
        
        Returns:
            策略建议数据（字典）
        
        Raises:
            Exception: 如果生成失败或返回的 JSON 格式不正确
        """
        prompt = self._build_strategy_prompt(geo_score, brand_name)
        
        messages = [
            {
                "role": "system",
                "content": "You are a professional GEO (Generative Engine Optimization) strategy consultant. Always respond with valid JSON only, no additional text."
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
                json_content = json_content.replace("```json", "").replace("```", "").strip()
            elif json_content.startswith("```"):
                json_content = json_content.replace("```", "").strip()
            
            strategy_data = json.loads(json_content)
            
            logger.debug(f"Successfully generated strategy for brand: {brand_name}")
            return strategy_data
            
        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse JSON from LLM response: {str(e)}"
            logger.error(error_msg)
            if json_content:
                logger.error(f"Response content (first 500 chars): {json_content[:500]}...")
            raise Exception(f"Invalid JSON response from LLM: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to generate strategy: {str(e)}")
            raise
    
    def _parse_strategy_data(
        self,
        strategy_data: Dict[str, Any]
    ) -> Tuple[str, List[str], List[StrategyRecommendation]]:
        """
        解析策略数据
        
        Args:
            strategy_data: LLM 返回的策略数据
        
        Returns:
            (summary, focus_areas, recommendations) 元组
        """
        summary = strategy_data.get("summary", "基于 GEO Score™ 分析生成的优化策略建议")
        focus_areas = strategy_data.get("focus_areas", [])
        recommendations_data = strategy_data.get("recommendations", [])
        
        recommendations = []
        for rec_data in recommendations_data:
            try:
                recommendation = StrategyRecommendation(
                    category=rec_data.get("category", "general"),
                    priority=rec_data.get("priority", "medium"),
                    title=rec_data.get("title", ""),
                    description=rec_data.get("description", ""),
                    action_items=rec_data.get("action_items", []),
                    expected_impact=rec_data.get("expected_impact", ""),
                    implementation_difficulty=rec_data.get("implementation_difficulty", "medium"),
                    estimated_time=rec_data.get("estimated_time"),
                    code_examples=rec_data.get("code_examples"),
                    resources=rec_data.get("resources", [])
                )
                recommendations.append(recommendation)
            except Exception as e:
                logger.warning(f"Failed to parse recommendation: {str(e)}")
                continue
        
        return summary, focus_areas, recommendations
    
    async def generate_strategy(
        self,
        geo_score: GeoScore,
        brand_name: str,
        audit_id: str,
        target_score: Optional[float] = None,
        strategy_id: Optional[str] = None
    ) -> Strategy:
        """
        生成策略建议
        
        Args:
            geo_score: GEO Score™ 评分结果
            brand_name: 品牌名称
            audit_id: 关联的审计 ID
            target_score: 目标 GEO Score™（可选）
            strategy_id: 策略 ID（可选，如果不提供则自动生成）
        
        Returns:
            Strategy 对象
        """
        logger.info(f"Generating strategy for brand: {brand_name}, GEO Score: {geo_score.overall_score}")
        
        try:
            # 使用 LLM 生成策略
            strategy_data = await self._generate_strategy_with_llm(geo_score, brand_name)
            
            # 解析策略数据
            summary, focus_areas, recommendations = self._parse_strategy_data(strategy_data)
            
            # 生成策略 ID
            if not strategy_id:
                strategy_id = generate_strategy_id(audit_id)
            
            # 构建 Strategy 对象
            strategy = Strategy(
                strategy_id=strategy_id,
                audit_id=audit_id,
                brand_name=brand_name,
                geo_score=geo_score.overall_score,
                target_score=target_score,
                recommendations=recommendations,
                summary=summary,
                focus_areas=focus_areas[:3],  # 最多 3 个重点关注领域
                generated_at=datetime.utcnow(),
                model_used=self.model,
                metadata={}
            )
            
            logger.info(
                f"Strategy generation completed. "
                f"Generated {len(recommendations)} recommendations, "
                f"Focus areas: {focus_areas}"
            )
            
            return strategy
            
        except Exception as e:
            logger.error(f"Failed to generate strategy: {str(e)}")
            # 返回一个基础的策略对象
            return Strategy(
                strategy_id=strategy_id or generate_strategy_id(audit_id),
                audit_id=audit_id,
                brand_name=brand_name,
                geo_score=geo_score.overall_score,
                target_score=target_score,
                recommendations=[],
                summary=f"策略生成失败：{str(e)}",
                focus_areas=[],
                generated_at=datetime.utcnow(),
                model_used=self.model,
                metadata={"error": str(e)}
            )

