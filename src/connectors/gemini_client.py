"""
Google Vertex AI API 连接器
封装 Google Vertex AI API 调用，支持 Gemini 模型
"""

import asyncio
import json
import time
from typing import Dict, Optional, Any, List
import aiohttp
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from config.settings import settings
from utils.logger import logger
from utils.cost_tracker import get_cost_tracker


class GeminiClient:
    """Google Vertex AI (Gemini) API 异步客户端"""
    
    def __init__(
        self,
        project_id: Optional[str] = None,
        location: Optional[str] = None,
        credentials_path: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: int = 1
    ):
        """
        初始化 Gemini 客户端
        
        Args:
            project_id: Google Cloud 项目 ID，如果为 None 则从 settings 读取
            location: 区域，如果为 None 则从 settings 读取
            credentials_path: 服务账号凭证文件路径，如果为 None 则从 settings 读取
            timeout: 请求超时时间（秒），默认 30 秒
            max_retries: 最大重试次数，默认 3 次
            retry_delay: 初始重试延迟（秒），默认 1 秒，采用指数退避
        """
        self.project_id = project_id or settings.google_project_id
        self.location = location or settings.google_location
        self.credentials_path = credentials_path or settings.google_application_credentials
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        if not self.project_id:
            raise ValueError("Google project ID is required. Set GOOGLE_PROJECT_ID in .env file.")
        
        # 初始化认证
        self._credentials = None
        self._access_token = None
        self._token_expiry = None
        
        # API 端点
        self.base_url = f"https://{self.location}-aiplatform.googleapis.com/v1"
    
    def _get_access_token(self) -> str:
        """
        获取访问令牌（同步方法，用于初始化）
        
        Returns:
            访问令牌字符串
        """
        if self._access_token and self._token_expiry and time.time() < self._token_expiry:
            return self._access_token
        
        try:
            if self.credentials_path:
                # 使用服务账号凭证文件
                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_path,
                    scopes=['https://www.googleapis.com/auth/cloud-platform']
                )
            else:
                # 尝试使用默认凭证
                from google.auth import default
                credentials, _ = default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
            
            # 刷新令牌
            credentials.refresh(Request())
            self._credentials = credentials
            self._access_token = credentials.token
            # 令牌有效期通常是 1 小时，提前 5 分钟刷新
            self._token_expiry = time.time() + 3300
            
            return self._access_token
            
        except Exception as e:
            raise ValueError(f"Failed to authenticate with Google Cloud: {str(e)}. "
                           f"Please set GOOGLE_APPLICATION_CREDENTIALS or run 'gcloud auth application-default login'")
    
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
        # 获取访问令牌（在事件循环中运行同步方法）
        access_token = await asyncio.to_thread(self._get_access_token)
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        default_headers = {
            "Authorization": f"Bearer {access_token}",
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
                        elif response.status == 401:
                            # 认证失败，刷新令牌后重试
                            logger.warning("Authentication failed, refreshing token...")
                            access_token = await asyncio.to_thread(self._get_access_token)
                            default_headers["Authorization"] = f"Bearer {access_token}"
                            if attempt < self.max_retries - 1:
                                await asyncio.sleep(self.retry_delay)
                                continue
                            else:
                                raise Exception("Authentication failed after token refresh")
                        elif response.status == 429:
                            # Rate limit 错误
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
                            try:
                                error_data = await response.json()
                                error_msg = error_data.get("error", {}).get("message", f"HTTP {response.status}")
                            except:
                                error_msg = f"HTTP {response.status}"
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
    
    def _convert_messages_to_gemini_format(self, messages: List[Dict]) -> List[Dict]:
        """
        将 OpenAI 格式的消息转换为 Gemini 格式
        
        Args:
            messages: OpenAI 格式的消息列表
        
        Returns:
            Gemini 格式的内容列表
        """
        gemini_contents = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            # Gemini 使用 "user" 和 "model" 角色
            if role == "assistant":
                gemini_role = "model"
            else:
                gemini_role = "user"
            
            gemini_contents.append({
                "role": gemini_role,
                "parts": [{"text": content}]
            })
        
        return gemini_contents
    
    async def chat_completion(
        self,
        messages: list,
        model: str = "gemini-1.5-pro",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        发送聊天完成请求
        
        Args:
            messages: 消息列表，格式：[{"role": "user", "content": "..."}]
            model: 模型名称，默认 "gemini-1.5-pro"
            temperature: 温度参数，默认 0.7
            max_tokens: 最大 token 数，可选（Gemini 使用 maxOutputTokens）
        
        Returns:
            包含 content, model, usage 的字典（与 OpenAI 格式保持一致）
        """
        # 转换消息格式
        gemini_contents = self._convert_messages_to_gemini_format(messages)
        
        # 构建请求数据
        request_data = {
            "contents": gemini_contents,
            "generationConfig": {
                "temperature": temperature
            }
        }
        
        if max_tokens:
            request_data["generationConfig"]["maxOutputTokens"] = max_tokens
        
        # 构建端点 URL（使用 generateContent 端点）
        model_path = f"projects/{self.project_id}/locations/{self.location}/publishers/google/models/{model}"
        endpoint = f"{model_path}:generateContent"
        
        try:
            # 使用 generateContent 端点
            response = await self._make_request(
                method="POST",
                endpoint=endpoint,
                data=request_data
            )
            
            # 解析响应
            candidates = response.get("candidates", [])
            if not candidates:
                raise Exception("No candidates in API response")
            
            candidate = candidates[0]
            content_parts = candidate.get("content", {}).get("parts", [])
            if not content_parts:
                raise Exception("No content parts in API response")
            
            content = content_parts[0].get("text", "")
            
            # 获取 token 使用情况
            usage_metadata = response.get("usageMetadata", {})
            
            result = {
                "content": content,
                "model": model,
                "usage": {
                    "prompt_tokens": usage_metadata.get("promptTokenCount", 0),
                    "completion_tokens": usage_metadata.get("candidatesTokenCount", 0),
                    "total_tokens": usage_metadata.get("totalTokenCount", 0)
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
            
            logger.info(f"Gemini API call successful. Model: {model}, Tokens: {result['usage']['total_tokens']}")
            return result
            
        except Exception as e:
            logger.error(f"Gemini API call failed: {str(e)}")
            raise
    
    async def simple_query(
        self,
        query: str,
        model: str = "gemini-1.5-pro",
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        简单的查询接口（便捷方法）
        
        Args:
            query: 查询文本
            model: 模型名称，默认 "gemini-1.5-pro"
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
_client_instance: Optional[GeminiClient] = None


def get_client() -> GeminiClient:
    """
    获取全局 Gemini 客户端实例（单例模式）
    
    Returns:
        GeminiClient 实例
    """
    global _client_instance
    if _client_instance is None:
        _client_instance = GeminiClient()
    return _client_instance

