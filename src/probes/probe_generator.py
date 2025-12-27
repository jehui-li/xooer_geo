"""
探针指令集生成器
负责生成三类探针模板并支持多语言
"""

from enum import Enum
from typing import Optional, List, Dict
from ..models.probe import ProbeType


class Language(str, Enum):
    """支持的语言枚举"""
    EN = "en"  # 英文
    ZH = "zh"  # 中文


class ProbeGenerator:
    """探针指令集生成器"""
    
    # 三类探针模板（英文）
    TEMPLATES_EN: Dict[ProbeType, str] = {
        ProbeType.DIRECT_RECOMMENDATION: "What are the best {keyword} currently on the market?",
        ProbeType.ATTRIBUTE_COMPARISON: "Compare the pros and cons of {competitor_brands} and {target_brand}.",
        ProbeType.SOLUTION_BASED: "How to solve {pain_point}? What are some recommended tools or solutions?"
    }
    
    # 三类探针模板（中文）
    TEMPLATES_ZH: Dict[ProbeType, str] = {
        ProbeType.DIRECT_RECOMMENDATION: "目前市场上最好的 {keyword} 有哪些？",
        ProbeType.ATTRIBUTE_COMPARISON: "对比 {competitor_brands} 和 {target_brand} 的优缺点。",
        ProbeType.SOLUTION_BASED: "如何解决 {pain_point}？有哪些推荐的工具或解决方案？"
    }
    
    def __init__(self, default_language: Language = Language.EN):
        """
        初始化探针生成器
        
        Args:
            default_language: 默认语言，默认为英文
        """
        self.default_language = default_language
    
    def generate(
        self,
        keyword: str,
        probe_type: ProbeType,
        language: Optional[Language] = None,
        target_brand: Optional[str] = None,
        competitor_brands: Optional[List[str]] = None,
        pain_point: Optional[str] = None
    ) -> str:
        """
        生成探针查询文本
        
        Args:
            keyword: 关键词（产品类别或行业领域）
            probe_type: 探针类型
            language: 语言，如果为 None 则使用默认语言
            target_brand: 目标品牌名称（用于属性对比类探针）
            competitor_brands: 竞争对手品牌列表（用于属性对比类探针）
            pain_point: 痛点描述（用于解决方案类探针）
        
        Returns:
            生成的探针查询文本
        
        Raises:
            ValueError: 当探针类型需要的参数缺失时
        """
        lang = language or self.default_language
        templates = self.TEMPLATES_EN if lang == Language.EN else self.TEMPLATES_ZH
        
        if probe_type not in templates:
            raise ValueError(f"Unsupported probe type: {probe_type}")
        
        template = templates[probe_type]
        
        # 根据探针类型处理参数
        if probe_type == ProbeType.DIRECT_RECOMMENDATION:
            return template.format(keyword=keyword)
        
        elif probe_type == ProbeType.ATTRIBUTE_COMPARISON:
            if not target_brand:
                raise ValueError("target_brand is required for ATTRIBUTE_COMPARISON probe type")
            
            # 处理竞争对手品牌列表
            if competitor_brands:
                if lang == Language.EN:
                    competitors_str = ", ".join(competitor_brands)
                else:
                    competitors_str = "、".join(competitor_brands)
            else:
                # 如果没有提供竞争对手，使用默认表述
                if lang == Language.EN:
                    competitors_str = "other brands"
                else:
                    competitors_str = "其他品牌"
            
            return template.format(
                competitor_brands=competitors_str,
                target_brand=target_brand
            )
        
        elif probe_type == ProbeType.SOLUTION_BASED:
            # 如果没有提供痛点，使用关键词作为痛点
            actual_pain_point = pain_point or keyword
            return template.format(pain_point=actual_pain_point)
        
        else:
            raise ValueError(f"Unsupported probe type: {probe_type}")
    
    def generate_all_types(
        self,
        keyword: str,
        language: Optional[Language] = None,
        target_brand: Optional[str] = None,
        competitor_brands: Optional[List[str]] = None,
        pain_point: Optional[str] = None
    ) -> Dict[ProbeType, str]:
        """
        为指定关键词生成所有三种类型的探针
        
        Args:
            keyword: 关键词
            language: 语言
            target_brand: 目标品牌名称
            competitor_brands: 竞争对手品牌列表
            pain_point: 痛点描述
        
        Returns:
            字典，键为探针类型，值为生成的查询文本
        """
        result = {}
        for probe_type in ProbeType:
            try:
                result[probe_type] = self.generate(
                    keyword=keyword,
                    probe_type=probe_type,
                    language=language,
                    target_brand=target_brand,
                    competitor_brands=competitor_brands,
                    pain_point=pain_point
                )
            except ValueError as e:
                # 如果某个类型需要的参数缺失，跳过该类型
                continue
        
        return result
    
    def generate_batch(
        self,
        keywords: List[str],
        language: Optional[Language] = None,
        target_brand: Optional[str] = None,
        competitor_brands: Optional[List[str]] = None,
        pain_point: Optional[str] = None,
        probe_types: Optional[List[ProbeType]] = None
    ) -> Dict[str, Dict[ProbeType, str]]:
        """
        批量生成探针查询（多个关键词，每种类型）
        
        Args:
            keywords: 关键词列表
            language: 语言
            target_brand: 目标品牌名称
            competitor_brands: 竞争对手品牌列表
            pain_point: 痛点描述
            probe_types: 要生成的探针类型列表，如果为 None 则生成所有类型
        
        Returns:
            字典，键为关键词，值为 {探针类型: 查询文本} 的字典
        """
        if probe_types is None:
            probe_types = list(ProbeType)
        
        result = {}
        for keyword in keywords:
            keyword_probes = {}
            for probe_type in probe_types:
                try:
                    keyword_probes[probe_type] = self.generate(
                        keyword=keyword,
                        probe_type=probe_type,
                        language=language,
                        target_brand=target_brand,
                        competitor_brands=competitor_brands,
                        pain_point=pain_point
                    )
                except ValueError:
                    continue
            result[keyword] = keyword_probes
        
        return result

