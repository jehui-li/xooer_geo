"""
API 成本追踪模块
记录 API 调用成本（只记录，不做复杂预算控制）
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, date
from collections import defaultdict

from utils.logger import logger


class CostTracker:
    """API 成本追踪器"""
    
    # 模型价格（每 1000 tokens，美元）
    # 注意：这是示例价格，实际价格可能有所不同
    MODEL_PRICING = {
        "gpt-4o": {
            "prompt": 0.0025,  # $2.50 per 1M tokens
            "completion": 0.010  # $10.00 per 1M tokens
        },
        "gpt-4": {
            "prompt": 0.03,
            "completion": 0.06
        },
        "gpt-3.5-turbo": {
            "prompt": 0.0005,
            "completion": 0.0015
        },
        "gemini-1.5-pro": {
            "prompt": 0.00125,  # $1.25 per 1M tokens
            "completion": 0.005  # $5.00 per 1M tokens
        },
        "llama-3.1-sonar-large-128k-online": {
            "prompt": 0.0007,  # Perplexity 价格
            "completion": 0.0007
        },
        "grok-beta": {
            "prompt": 0.01,  # 示例价格
            "completion": 0.01
        }
    }
    
    def __init__(self):
        """初始化成本追踪器"""
        # 按日期存储成本记录
        self._daily_costs: Dict[date, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        # 按模型存储总成本
        self._model_costs: Dict[str, float] = defaultdict(float)
        # 总成本
        self._total_cost: float = 0.0
        # 调用次数统计
        self._call_counts: Dict[str, int] = defaultdict(int)
        
        logger.info("Cost tracker initialized")
    
    def _get_model_key(self, model_name: str) -> str:
        """
        获取模型的标准化名称（用于价格查找）
        
        Args:
            model_name: 模型名称
        
        Returns:
            标准化的模型名称
        """
        # 尝试直接匹配
        if model_name in self.MODEL_PRICING:
            return model_name
        
        # 尝试部分匹配
        for key in self.MODEL_PRICING.keys():
            if key in model_name or model_name in key:
                return key
        
        # 默认使用第一个模型的价格（如果找不到）
        logger.warning(f"Unknown model pricing for {model_name}, using default")
        return list(self.MODEL_PRICING.keys())[0]
    
    def _calculate_cost(
        self,
        model_name: str,
        prompt_tokens: int,
        completion_tokens: int
    ) -> float:
        """
        计算 API 调用成本
        
        Args:
            model_name: 模型名称
            prompt_tokens: Prompt tokens 数量
            completion_tokens: Completion tokens 数量
        
        Returns:
            成本（美元）
        """
        model_key = self._get_model_key(model_name)
        
        if model_key not in self.MODEL_PRICING:
            logger.warning(f"No pricing for model {model_key}, cost set to 0")
            return 0.0
        
        pricing = self.MODEL_PRICING[model_key]
        prompt_cost = (prompt_tokens / 1000.0) * pricing["prompt"]
        completion_cost = (completion_tokens / 1000.0) * pricing["completion"]
        
        total_cost = prompt_cost + completion_cost
        return round(total_cost, 6)
    
    def record_cost(
        self,
        model_name: str,
        prompt_tokens: int,
        completion_tokens: int,
        cost_date: Optional[date] = None
    ) -> float:
        """
        记录 API 调用成本
        
        Args:
            model_name: 模型名称
            prompt_tokens: Prompt tokens 数量
            completion_tokens: Completion tokens 数量
            cost_date: 成本日期，如果为 None 则使用当前日期
        
        Returns:
            本次调用的成本（美元）
        """
        if cost_date is None:
            cost_date = date.today()
        
        # 计算成本
        cost = self._calculate_cost(model_name, prompt_tokens, completion_tokens)
        
        # 记录成本
        self._daily_costs[cost_date][model_name] += cost
        self._model_costs[model_name] += cost
        self._total_cost += cost
        self._call_counts[model_name] += 1
        
        logger.debug(
            f"Cost recorded: {model_name}, "
            f"Tokens: {prompt_tokens}+{completion_tokens}, "
            f"Cost: ${cost:.6f}"
        )
        
        return cost
    
    def get_daily_cost(self, cost_date: Optional[date] = None) -> float:
        """
        获取指定日期的总成本
        
        Args:
            cost_date: 日期，如果为 None 则使用当前日期
        
        Returns:
            总成本（美元）
        """
        if cost_date is None:
            cost_date = date.today()
        
        return sum(self._daily_costs[cost_date].values())
    
    def get_model_cost(self, model_name: str) -> float:
        """
        获取指定模型的总成本
        
        Args:
            model_name: 模型名称
        
        Returns:
            总成本（美元）
        """
        return self._model_costs.get(model_name, 0.0)
    
    def get_total_cost(self) -> float:
        """
        获取总成本
        
        Returns:
            总成本（美元）
        """
        return self._total_cost
    
    def get_cost_summary(self) -> Dict[str, Any]:
        """
        获取成本汇总
        
        Returns:
            成本汇总字典
        """
        today_cost = self.get_daily_cost()
        
        return {
            "total_cost": round(self._total_cost, 2),
            "today_cost": round(today_cost, 2),
            "model_costs": {
                model: round(cost, 2)
                for model, cost in self._model_costs.items()
            },
            "call_counts": dict(self._call_counts),
            "daily_costs": {
                str(d): round(sum(costs.values()), 2)
                for d, costs in self._daily_costs.items()
            }
        }
    
    def reset_daily_cost(self, cost_date: Optional[date] = None):
        """
        重置指定日期的成本记录
        
        Args:
            cost_date: 日期，如果为 None 则使用当前日期
        """
        if cost_date is None:
            cost_date = date.today()
        
        if cost_date in self._daily_costs:
            # 从总成本中减去该日期的成本
            daily_total = sum(self._daily_costs[cost_date].values())
            self._total_cost -= daily_total
            
            # 从模型成本中减去
            for model, cost in self._daily_costs[cost_date].items():
                self._model_costs[model] -= cost
            
            del self._daily_costs[cost_date]
            logger.info(f"Daily cost reset for {cost_date}")


# 全局成本追踪器实例
_global_cost_tracker: Optional[CostTracker] = None


def get_cost_tracker() -> CostTracker:
    """
    获取全局成本追踪器实例（单例模式）
    
    Returns:
        CostTracker 实例
    """
    global _global_cost_tracker
    if _global_cost_tracker is None:
        _global_cost_tracker = CostTracker()
    return _global_cost_tracker

