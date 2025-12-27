"""
GEO Agent 配置管理模块
负责读取和管理环境变量配置
"""

import os
from pathlib import Path
from typing import List, Optional
from pydantic import Field
from dotenv import load_dotenv
from pydantic_settings import BaseSettings


# 加载 .env 文件
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    """应用配置类"""
    
    # ==================== API 密钥 ====================
    openai_api_key: str = ""
    google_project_id: str = ""
    google_location: str = "us-central1"
    google_application_credentials: Optional[str] = None
    perplexity_api_key: str = ""
    x_api_key: str = ""
    x_api_secret_key: str = ""
    x_access_token: str = ""
    x_access_token_secret: str = ""
    x_bearer_token: str = ""
    
    # ==================== 数据库配置 ====================
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_database: str = "geo_agent"
    mongodb_collection_audit_results: str = "audit_results"
    mongodb_collection_historical_trends: str = "historical_trends"
    
    # ==================== 应用配置 ====================
    log_level: str = "INFO"
    log_file_path: str = "logs/geo_agent.log"
    app_env: str = "development"
    
    # ==================== GEO Agent 配置 ====================
    default_test_iterations: int = 5
    default_temperatures: str = "0.3,0.7,1.0"
    api_timeout: int = 60
    api_max_retries: int = 3
    api_retry_delay: int = 1
    cache_expiry_hours: int = 24
    
    # ==================== 成本控制 ====================
    daily_cost_budget: float = 100.0
    monthly_cost_budget: float = 3000.0
    
    # ==================== GEO Score 权重配置 ====================
    geo_weight_som: float = 0.4
    geo_weight_citation: float = 0.3
    geo_weight_ranking: float = 0.2
    geo_weight_accuracy: float = 0.1
    
    # ==================== API 配置 ====================
    api_key: Optional[str] = Field(None, description="API Key for authentication")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @property
    def temperature_list(self) -> List[float]:
        """解析 Temperature 字符串为列表"""
        return [float(t.strip()) for t in self.default_temperatures.split(",")]
    
    @property
    def is_development(self) -> bool:
        """判断是否为开发环境"""
        return self.app_env.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """判断是否为生产环境"""
        return self.app_env.lower() == "production"
    
    def validate_api_keys(self) -> dict:
        """
        验证必需的 API 密钥是否已配置
        返回缺失的密钥列表
        """
        missing_keys = {}
        
        if not self.openai_api_key:
            missing_keys["openai"] = "OPENAI_API_KEY"
        if not self.perplexity_api_key:
            missing_keys["perplexity"] = "PERPLEXITY_API_KEY"
        if not self.x_api_key or not self.x_bearer_token:
            missing_keys["x"] = "X_API_KEY or X_BEARER_TOKEN"
        if not self.google_project_id:
            missing_keys["google"] = "GOOGLE_PROJECT_ID"
        
        return missing_keys


# 创建全局配置实例
settings = Settings()

