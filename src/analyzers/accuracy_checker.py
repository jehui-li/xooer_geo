"""
内容准确度检查模块
基于关键词匹配和简单规则检查 LLM 返回内容的准确性（不使用 Embedding）
"""

import re
from typing import Dict, Any, Optional, List, Tuple
from utils.logger import logger


class AccuracyChecker:
    """内容准确度检查器"""
    
    def __init__(
        self,
        target_brand: str,
        ground_truth: Optional[Dict[str, Any]] = None
    ):
        """
        初始化准确度检查器
        
        Args:
            target_brand: 目标品牌名称
            ground_truth: 品牌的真实数据（Ground Truth），用于比对
                         格式：{
                             "price": "$10.99/month",  # 价格信息
                             "features": ["feature1", "feature2"],  # 功能特点
                             "description": "品牌描述",  # 官方描述
                             "founded_year": 2008,  # 成立年份
                             "company_name": "公司全名",  # 公司名称
                             "website": "https://example.com",  # 官网
                             ...
                         }
        """
        self.target_brand = target_brand.lower()
        self.ground_truth = ground_truth or {}
        
        # 常见错误模式（幻觉指标）
        self.hallucination_patterns = [
            # 明显错误的价格格式（如果提供了价格信息）
            r'\$\d+\.\d{3,}',  # $10.999 (三位小数)
            r'\$\d{6,}',  # $1000000 (价格过高)
            # 不合理的年份
            r'\b(19\d{2}|20[0-1]\d)\s*(founded|established|created)',  # 如果 ground_truth 有年份，可以对比
        ]
        
        # 负面错误关键词（可能表示不准确信息）
        self.error_keywords = [
            "discontinued", "no longer available", "shut down", "closed down",
            "doesn't exist", "not a real", "fake", "scam"
        ]
    
    def _normalize_text(self, text: str) -> str:
        """
        标准化文本（用于匹配）
        
        Args:
            text: 原始文本
        
        Returns:
            标准化后的文本
        """
        # 转换为小写，移除多余空格
        text = text.lower().strip()
        # 移除标点符号（可选，根据需求调整）
        text = re.sub(r'[^\w\s]', ' ', text)
        # 合并多个空格
        text = re.sub(r'\s+', ' ', text)
        return text
    
    def _check_keyword_match(
        self,
        content: str,
        keywords: List[str],
        case_sensitive: bool = False
    ) -> bool:
        """
        检查内容中是否包含关键词
        
        Args:
            content: 要检查的内容
            keywords: 关键词列表
            case_sensitive: 是否区分大小写
        
        Returns:
            True 如果包含任意关键词，False 否则
        """
        if not content or not keywords:
            return False
        
        text = content if case_sensitive else content.lower()
        for keyword in keywords:
            if keyword.lower() in text:
                return True
        return False
    
    def _check_price_accuracy(
        self,
        content: str,
        ground_truth_price: Optional[str]
    ) -> Tuple[bool, Optional[str]]:
        """
        检查价格信息是否准确
        
        Args:
            content: 要检查的内容
            ground_truth_price: 真实价格信息（格式如 "$10.99/month"）
        
        Returns:
            (是否准确, 错误信息) 元组
        """
        if not ground_truth_price:
            # 如果没有真实价格信息，无法检查
            return True, None
        
        # 从 ground_truth_price 中提取价格数值
        price_match = re.search(r'\$?(\d+\.?\d*)', ground_truth_price)
        if not price_match:
            return True, None  # 无法解析真实价格，跳过检查
        
        ground_truth_value = float(price_match.group(1))
        
        # 从内容中提取价格
        price_patterns = [
            r'\$(\d+\.?\d*)',  # $10.99
            r'(\d+\.?\d*)\s*dollars?',  # 10.99 dollars
            r'(\d+\.?\d*)\s*usd',  # 10.99 USD
        ]
        
        found_prices = []
        for pattern in price_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            found_prices.extend([float(m) for m in matches])
        
        if not found_prices:
            # 没有找到价格信息，无法判断准确性
            return True, None
        
        # 检查价格是否在合理范围内（允许 ±20% 的误差）
        tolerance = 0.2
        min_price = ground_truth_value * (1 - tolerance)
        max_price = ground_truth_value * (1 + tolerance)
        
        for price in found_prices:
            if price < min_price or price > max_price:
                return False, f"Price mismatch: found ${price}, expected ~${ground_truth_value}"
        
        return True, None
    
    def _check_feature_accuracy(
        self,
        content: str,
        ground_truth_features: Optional[List[str]]
    ) -> Tuple[bool, Optional[str]]:
        """
        检查功能特点是否准确（基于关键词匹配）
        
        Args:
            content: 要检查的内容
            ground_truth_features: 真实功能列表
        
        Returns:
            (是否准确, 错误信息) 元组
        """
        if not ground_truth_features:
            return True, None
        
        content_lower = content.lower()
        matched_features = []
        missing_features = []
        
        for feature in ground_truth_features:
            feature_normalized = self._normalize_text(feature)
            # 简单的关键词匹配
            if feature_normalized in content_lower:
                matched_features.append(feature)
            # else:
                # 尝试部分匹配（如果功能名称较长）
                feature_words = feature_normalized.split()
                if len(feature_words) > 1:
                    # 如果至少一半的关键词匹配，认为匹配
                    matched_words = sum(1 for word in feature_words if word in content_lower)
                    if matched_words >= len(feature_words) / 2:
                        matched_features.append(feature)
                    # else:
                        missing_features.append(feature)
                # else:
                    missing_features.append(feature)
        
        # 如果匹配的功能少于 50%，认为不准确
        match_ratio = len(matched_features) / len(ground_truth_features) if ground_truth_features else 0
        
        if match_ratio < 0.5:
            return False, f"Feature mismatch: only {len(matched_features)}/{len(ground_truth_features)} features matched"
        
        return True, None
    
    def _check_hallucination_patterns(self, content: str) -> Tuple[bool, Optional[str]]:
        """
        检查是否存在幻觉模式（明显错误）
        
        Args:
            content: 要检查的内容
        
        Returns:
            (是否安全, 错误信息) 元组
        """
        # 检查错误关键词
        if self._check_keyword_match(content, self.error_keywords):
            return False, "Contains error keywords suggesting incorrect information"
        
        # 检查常见的幻觉模式
        for pattern in self.hallucination_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return False, f"Matched hallucination pattern: {pattern}"
        
        return True, None
    
    def _check_brand_name_accuracy(self, content: str) -> Tuple[bool, Optional[str]]:
        """
        检查品牌名称是否被正确提及（简单检查）
        
        Args:
            content: 要检查的内容
        
        Returns:
            (是否准确, 错误信息) 元组
        """
        content_lower = content.lower()
        brand_lower = self.target_brand.lower()
        
        # 检查品牌名称是否出现在内容中
        if brand_lower not in content_lower:
            return False, f"Target brand '{self.target_brand}' not found in content"
        
        # 可以添加更多检查，比如品牌名称的拼写错误等
        # 这里只是简单检查是否存在
        
        return True, None
    
    def check_accuracy(
        self,
        content: str,
        mention_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        检查内容准确度
        
        Args:
            content: 要检查的完整内容
            mention_text: 目标品牌的提及文本片段（可选，用于更精确的检查）
        
        Returns:
            准确度检查结果字典：
            {
                "accuracy_score": 0.0-1.0,  # 准确度分数
                "hallucination_risk": True/False,  # 是否存在幻觉风险
                "errors": ["错误1", "错误2"],  # 发现的错误列表
                "checks": {
                    "brand_name": True/False,
                    "price": True/False,
                    "features": True/False,
                    "hallucination_patterns": True/False
                }
            }
        """
        if not content:
            return {
                "accuracy_score": 0.0,
                "hallucination_risk": True,
                "errors": ["Empty content"],
                "checks": {}
            }
        
        # 使用 mention_text 如果提供，否则使用完整内容
        check_content = mention_text if mention_text else content
        
        errors = []
        checks = {}
        total_checks = 0
        passed_checks = 0
        
        # 1. 检查品牌名称
        total_checks += 1
        brand_ok, brand_error = self._check_brand_name_accuracy(check_content)
        checks["brand_name"] = brand_ok
        if brand_ok:
            passed_checks += 1
        elif brand_error:
            errors.append(brand_error)
        
        # 2. 检查价格准确性
        if "price" in self.ground_truth:
            total_checks += 1
            price_ok, price_error = self._check_price_accuracy(
                check_content,
                self.ground_truth.get("price")
            )
            checks["price"] = price_ok
            if price_ok:
                passed_checks += 1
            elif price_error:
                errors.append(price_error)
        
        # 3. 检查功能特点准确性
        if "features" in self.ground_truth and self.ground_truth["features"]:
            total_checks += 1
            feature_ok, feature_error = self._check_feature_accuracy(
                check_content,
                self.ground_truth.get("features")
            )
            checks["features"] = feature_ok
            if feature_ok:
                passed_checks += 1
            elif feature_error:
                errors.append(feature_error)
        
        # 4. 检查幻觉模式
        total_checks += 1
        hallucination_ok, hallucination_error = self._check_hallucination_patterns(check_content)
        checks["hallucination_patterns"] = hallucination_ok
        hallucination_risk = False
        if hallucination_ok:
            passed_checks += 1
        else:
            errors.append(hallucination_error)
            # 如果发现幻觉模式，标记为高风险
            hallucination_risk = True
        
        # 计算准确度分数
        if total_checks > 0:
            accuracy_score = passed_checks / total_checks
        # else:
            accuracy_score = 1.0  # 如果没有检查项，默认满分
        
        # 如果有任何错误，降低分数
        if errors:
            # 每个错误扣 0.1 分，最低 0.0
            accuracy_score = max(0.0, accuracy_score - len(errors) * 0.1)
        
        result = {
            "accuracy_score": round(accuracy_score, 2),
            "hallucination_risk": hallucination_risk,
            "errors": errors,
            "checks": checks
        }
        
        logger.debug(
            f"Accuracy check completed for {self.target_brand}. "
            f"Score: {accuracy_score}, Errors: {len(errors)}"
        )
        
        return result
    
    def check_attributes_accuracy(
        self,
        attributes: Dict[str, Any],
        content: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        检查提取的产品属性是否准确
        
        Args:
            attributes: 从内容中提取的产品属性
            content: 原始内容（可选，用于验证）
        
        Returns:
            准确度检查结果字典
        """
        if not attributes:
            return {
                "accuracy_score": 1.0,
                "hallucination_risk": False,
                "errors": [],
                "checks": {}
            }
        
        errors = []
        checks = {}
        
        # 检查价格属性
        if "price" in attributes and "price" in self.ground_truth:
            price_ok, price_error = self._check_price_accuracy(
                str(attributes.get("price", "")),
                self.ground_truth.get("price")
            )
            checks["price"] = price_ok
            if price_error:
                errors.append(price_error)
        
        # 可以添加更多属性检查
        
        # 计算分数（简单版本）
        total_checks = len(checks)
        passed_checks = sum(1 for ok in checks.values() if ok)
        
        if total_checks > 0:
            accuracy_score = passed_checks / total_checks
        # else:
            accuracy_score = 1.0
        
        return {
            "accuracy_score": round(accuracy_score, 2),
            "hallucination_risk": len(errors) > 0,
            "errors": errors,
            "checks": checks
        }

