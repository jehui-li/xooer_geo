"""
OpenAI API 连接器
封装 OpenAI API 调用，支持 GPT-4o 模型
"""

import asyncio
import json
from typing import Dict, Optional, Any
import aiohttp
from config.settings import settings
from utils.logger import logger
from utils.cost_tracker import get_cost_tracker


class OpenAIClient:
    """OpenAI API 异步客户端"""
    
    BASE_URL = "https://api.openai.com/v1"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: int = 1
    ):
        """
        初始化 OpenAI 客户端
        
        Args:
            api_key: OpenAI API 密钥，如果为 None 则从 settings 读取
            timeout: 请求超时时间（秒），默认 30 秒
            max_retries: 最大重试次数，默认 3 次
            retry_delay: 初始重试延迟（秒），默认 1 秒，采用指数退避
        """
        self.api_key = api_key or settings.openai_api_key
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY in .env file.")
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        发送 HTTP 请求（带重试机制）
        
        Args:
            method: HTTP 方法（GET, POST 等）
            endpoint: API 端点路径
            data: 请求体数据
            headers: 请求头
        
        Returns:
            API 响应数据
        
        Raises:
            Exception: 请求失败时抛出异常
        """
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        
        default_headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        if headers:
            default_headers.update(headers)
        
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                async with aiohttp.ClientSession(timeout=self.timeout) as session:
                    async with session.request(
                        method=method,
                        url=url,
                        headers=default_headers,
                        json=data if data else None
                    ) as response:
                        # 检查 HTTP 状态码
                        if response.status == 200:
                            result = await response.json()
                            return result
                        elif response.status == 429:
                            # Rate limit 错误，需要等待
                            error_data = await response.json()
                            retry_after = int(response.headers.get("Retry-After", self.retry_delay * (2 ** attempt)))
                            error_msg = error_data.get("error", {}).get("message", "Rate limit exceeded")
                            logger.warning(f"Rate limit hit, waiting {retry_after} seconds: {error_msg}")
                            if attempt < self.max_retries - 1:
                                await asyncio.sleep(retry_after)
                                continue
                            else:
                                raise Exception(f"Rate limit exceeded after {self.max_retries} attempts: {error_msg}")
                        else:
                            # 其他 HTTP 错误
                            error_data = await response.json()
                            error_msg = error_data.get("error", {}).get("message", f"HTTP {response.status}")
                            raise Exception(f"API error (HTTP {response.status}): {error_msg}")
                            
            except asyncio.TimeoutError:
                last_exception = Exception(f"Request timeout after {self.timeout} seconds")
                logger.warning(f"Request timeout (attempt {attempt + 1}/{self.max_retries})")
                
            except aiohttp.ClientError as e:
                last_exception = Exception(f"Network error: {str(e)}")
                logger.warning(f"Network error (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                
            except Exception as e:
                # 其他异常（如 API 错误）直接抛出，不重试
                raise e
            
            # 如果不是最后一次尝试，等待后重试（指数退避）
            if attempt < self.max_retries - 1:
                delay = self.retry_delay * (2 ** attempt)  # 1s, 2s, 4s
                logger.info(f"Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
        
        # 所有重试都失败
        if last_exception:
            raise last_exception
        else:
            raise Exception(f"Request failed after {self.max_retries} attempts")
    
    async def chat_completion(
        self,
        messages: list,
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        发送聊天完成请求
        
        Args:
            messages: 消息列表，格式：[{"role": "user", "content": "..."}]
            model: 模型名称，默认 "gpt-4o"
            temperature: 温度参数，默认 0.7
            max_tokens: 最大 token 数，可选
            response_format: 响应格式，可选，例如 {"type": "json_object"} 用于 JSON Mode
        
        Returns:
            包含 content, model, usage 的字典
        """
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }
        
        if max_tokens:
            data["max_tokens"] = max_tokens
        
        if response_format:
            data["response_format"] = response_format
        
        try:
            response = await self._make_request(
                method="POST",
                endpoint="/chat/completions",
                data=data
            )
            
            # 解析响应
            choices = response.get("choices", [])
            if not choices:
                raise Exception("No choices in API response")
            
            choice = choices[0]
            content = choice.get("message", {}).get("content", "")
            usage = response.get("usage", {})
            
            result = {
                "content": content,
                "model": model,
                "usage": {
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0)
                }
            }
            
            # 记录 API 成本
            try:
                cost_tracker = get_cost_tracker()
                cost_tracker.record_cost(
                    model_name=model,
                    prompt_tokens=result["usage"]["prompt_tokens"],
                    completion_tokens=result["usage"]["completion_tokens"]
                )
            except Exception as e:
                logger.warning(f"Failed to record cost: {str(e)}")
            
            logger.info(f"OpenAI API call successful. Model: {model}, Tokens: {result['usage']['total_tokens']}")
            return result
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
            raise
    
    async def simple_query(
        self,
        query: str,
        model: str = "gpt-4o",
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        简单的查询接口（便捷方法）
        
        Args:
            query: 查询文本
            model: 模型名称，默认 "gpt-4o"
            temperature: 温度参数，默认 0.7
        
        Returns:
            包含 content, model, usage 的字典
        """
        messages = [
            {"role": "user", "content": query}
        ]
        
        return await self.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature
        )


# 创建全局客户端实例（延迟初始化）
_client_instance: Optional[OpenAIClient] = None


def get_client() -> OpenAIClient:
    """
    获取全局 OpenAI 客户端实例（单例模式）
    
    Returns:
        OpenAIClient 实例
    """
    global _client_instance
    if _client_instance is None:
        _client_instance = OpenAIClient()
    return _client_instance

