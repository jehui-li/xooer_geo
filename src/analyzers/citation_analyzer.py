"""
引用链接分析模块
从 Perplexity 响应中提取引用链接，并判断链接类型（官网、权威来源、第三方等）
"""

from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

from src.models.probe import Citation
from utils.logger import logger


class CitationAnalyzer:
    """引用链接分析器"""
    
    # 权威来源域名关键词（简单判断规则）
    AUTHORITATIVE_DOMAINS = [
        ".gov",
        ".edu",
        "wikipedia.org",
        "scholar.google.com",
        "researchgate.net",
        "ieee.org",
        "acm.org",
        "nature.com",
        "science.org"
    ]
    
    def __init__(self, target_brand: Optional[str] = None, target_website: Optional[str] = None):
        """
        初始化引用链接分析器
        
        Args:
            target_brand: 目标品牌名称（用于判断官网链接）
            target_website: 目标品牌官网 URL（用于精确匹配官网链接）
        """
        self.target_brand = target_brand.lower() if target_brand else None
        self.target_website = target_website.lower().strip("/") if target_website else None
        
        # 如果提供了官网 URL，提取域名用于匹配
        self.target_domain = None
        if self.target_website:
            try:
                parsed = urlparse(self.target_website)
                self.target_domain = parsed.netloc.lower()
                # 移除 www. 前缀以便匹配
                if self.target_domain.startswith("www."):
                    self.target_domain = self.target_domain[4:]
            except Exception as e:
                logger.warning(f"Failed to parse target website URL: {str(e)}")
    
    def _extract_domain(self, url: str) -> Optional[str]:
        """
        从 URL 中提取域名
        
        Args:
            url: 完整的 URL
        
        Returns:
            域名（不含 www. 前缀），如果解析失败则返回 None
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            # 移除 www. 前缀
            if domain.startswith("www."):
                domain = domain[4:]
            return domain
        except Exception as e:
            logger.debug(f"Failed to parse URL {url}: {str(e)}")
            return None
    
    def _is_official_website(self, url: str) -> bool:
        """
        判断是否为官网链接
        
        Args:
            url: 链接 URL
        
        Returns:
            True 如果是官网链接，False 否则
        """
        url_lower = url.lower()
        
        # 方法1: 精确匹配目标域名
        if self.target_domain:
            url_domain = self._extract_domain(url)
            if url_domain and url_domain == self.target_domain:
                return True
        
        # 方法2: URL 中包含目标品牌名称（简单启发式规则）
        if self.target_brand:
            # 提取域名，检查是否包含品牌名称
            url_domain = self._extract_domain(url)
            if url_domain and self.target_brand in url_domain:
                # 排除常见的第三方平台
                if not any(platform in url_domain for platform in [
                    "amazon", "walmart", "target", "shopify", "etsy",
                    "facebook", "twitter", "linkedin", "instagram",
                    "youtube", "tiktok", "reddit", "medium", "wordpress"
                ]):
                    return True
        
        return False
    
    def _is_authoritative_source(self, url: str) -> bool:
        """
        判断是否为权威来源
        
        Args:
            url: 链接 URL
        
        Returns:
            True 如果是权威来源，False 否则
        """
        url_lower = url.lower()
        
        # 检查是否包含权威域名关键词
        for domain in self.AUTHORITATIVE_DOMAINS:
            if domain in url_lower:
                return True
        
        return False
    
    def classify_citation_type(self, url: str) -> str:
        """
        分类引用链接类型
        
        Args:
            url: 链接 URL
        
        Returns:
            引用类型：official, authoritative, third_party, unknown
        """
        if not url or not url.strip():
            return "unknown"
        
        url = url.strip()
        
        # 1. 判断是否为官网
        if self._is_official_website(url):
            return "official"
        
        # 2. 判断是否为权威来源
        if self._is_authoritative_source(url):
            return "authoritative"
        
        # 3. 默认为第三方
        return "third_party"
    
    def analyze_citations(
        self,
        citations_data: List[Dict[str, Any]]
    ) -> List[Citation]:
        """
        分析并分类引用链接列表
        
        Args:
            citations_data: 原始引用链接数据，格式：[{"url": "...", "title": "...", "text": "..."}]
        
        Returns:
            Citation 对象列表，已分类
        """
        analyzed_citations = []
        
        for cit_data in citations_data:
            url = cit_data.get("url", "")
            if not url:
                continue
            
            # 分类链接类型
            citation_type = self.classify_citation_type(url)
            
            citation = Citation(
                url=url,
                title=cit_data.get("title"),
                text=cit_data.get("text"),
                citation_type=citation_type
            )
            
            analyzed_citations.append(citation)
            
            logger.debug(
                f"Analyzed citation: {url[:50]}... -> {citation_type}"
            )
        
        return analyzed_citations
    
    def extract_from_perplexity_response(
        self,
        perplexity_response: Dict[str, Any]
    ) -> List[Citation]:
        """
        从 Perplexity API 响应中提取并分析引用链接
        
        Args:
            perplexity_response: Perplexity API 的完整响应
        
        Returns:
            已分类的 Citation 对象列表
        """
        citations_data = []
        
        # Perplexity 的引用可能在多个地方
        # 1. 在 choices[0].message.citations 中
        choices = perplexity_response.get("choices", [])
        if choices:
            message = choices[0].get("message", {})
            citations_data.extend(message.get("citations", []))
        
        # 2. 在响应的 citations 字段中
        if not citations_data:
            citations_data = perplexity_response.get("citations", [])
        
        # 标准化数据格式
        normalized_citations = []
        for citation in citations_data:
            if isinstance(citation, dict):
                normalized_citations.append({
                    "url": citation.get("url", ""),
                    "title": citation.get("title", ""),
                    "text": citation.get("text", "")
                })
            elif isinstance(citation, str):
                # 如果 citations 是字符串列表（URL）
                normalized_citations.append({
                    "url": citation,
                    "title": "",
                    "text": ""
                })
        
        # 分析和分类
        return self.analyze_citations(normalized_citations)
    
    def count_citations_by_type(self, citations: List[Citation]) -> Dict[str, int]:
        """
        按类型统计引用链接数量
        
        Args:
            citations: Citation 对象列表
        
        Returns:
            统计结果字典：{"official": 1, "authoritative": 2, "third_party": 3, "unknown": 0}
        """
        counts = {
            "official": 0,
            "authoritative": 0,
            "third_party": 0,
            "unknown": 0
        }
        
        for citation in citations:
            citation_type = citation.citation_type
            if citation_type in counts:
                counts[citation_type] += 1
            else:
                counts["unknown"] += 1
        
        return counts
    
    def get_official_citations_count(self, citations: List[Citation]) -> int:
        """
        获取官网引用数量
        
        Args:
            citations: Citation 对象列表
        
        Returns:
            官网引用数量
        """
        return sum(1 for cit in citations if cit.citation_type == "official")
    
    def get_authoritative_citations_count(self, citations: List[Citation]) -> int:
        """
        获取权威来源引用数量
        
        Args:
            citations: Citation 对象列表
        
        Returns:
            权威来源引用数量
        """
        return sum(1 for cit in citations if cit.citation_type == "authoritative")

