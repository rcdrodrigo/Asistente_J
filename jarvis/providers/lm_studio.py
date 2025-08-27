"""
LM Studio provider for JARVIS.

This module provides integration with LM Studio's local LLM server.
"""

import json
import logging
from typing import Dict, List, Optional, Union, AsyncGenerator, Any, Type, TypeVar
import aiohttp
from pydantic import BaseModel, Field, HttpUrl, model_validator

from ..config import JarvisSettings
from .base import LLMProvider, ChatMessage

logger = logging.getLogger(__name__)

class GenerationConfig(BaseModel):
    """Configuration for text generation."""
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2000, ge=1)
    top_p: float = Field(default=0.9, ge=0.0, le=1.0)
    stream: bool = Field(default=False)

class LMStudioConfig(BaseModel):
    """Configuration for LM Studio provider."""
    base_url: HttpUrl = Field(
        default="http://172.24.240.1:1234/v1",
        description="Base URL for LM Studio API (without trailing slash)"
    )
    model: str = Field(
        default="local-model",
        description="Model name to use for completions"
    )
    temperature: float = Field(
        default=0.7,
        description="Sampling temperature (0-2)",
        ge=0.0,
        le=2.0
    )
    max_tokens: int = Field(
        default=2000,
        description="Maximum number of tokens to generate",
        gt=0
    )
    top_p: float = Field(
        default=0.9,
        description="Nucleus sampling parameter (0-1)",
        ge=0.0,
        le=1.0
    )
    timeout: int = Field(
        default=300,
        description="Request timeout in seconds",
        gt=0
    )

    @classmethod
    def from_settings(cls, settings: JarvisSettings) -> 'LMStudioConfig':
        """Create config from global settings."""
        return cls(
            base_url=settings.lm_studio_base_url,
            model=settings.lm_studio_model,
            temperature=settings.lm_studio_temperature,
            max_tokens=settings.lm_studio_max_tokens,
            top_p=settings.lm_studio_top_p,
            timeout=settings.lm_studio_timeout
        )

class LMStudioProvider(LLMProvider):
    """LLM provider for LM Studio's local server."""
    
    def __init__(self, config: Optional[Union[LMStudioConfig, JarvisSettings]] = None):
        if config is None:
            self.config = LMStudioConfig()
        elif isinstance(config, JarvisSettings):
            self.config = LMStudioConfig.from_settings(config)
        else:
            self.config = config
            
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def initialize(self):
        """Initialize the LM Studio provider."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                base_url=str(self.config.base_url),
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
        logger.info(f"LM Studio provider initialized with base_url: {self.config.base_url}")

    @property
    def session(self) -> aiohttp.ClientSession:
        """Return the aiohttp client session."""
        if self._session is None:
            raise RuntimeError("LM Studio session not initialized. Call initialize() first.")
        return self._session
    
    async def cleanup(self) -> None:
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    def _format_messages(self, messages: List[ChatMessage]) -> List[Dict[str, str]]:
        """Format messages for LM Studio API."""
        formatted = []
        for msg in messages:
            formatted.append({"role": msg.role, "content": msg.content})
        return formatted
    
    async def generate(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None,
        **kwargs
    ) -> str:
        """Generate text from a prompt."""
        messages = [ChatMessage(role="user", content=prompt)]
        response = await self.chat_completion(messages, config, **kwargs)
        return response[-1].content if response else ""
    
    async def chat_completion(
        self,
        messages: List[ChatMessage],
        config: Optional[GenerationConfig] = None,
    ) -> List[ChatMessage]:
        """Generate a chat response."""
        config = config or GenerationConfig()
        url = f"{self.config.base_url}/chat/completions"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.config.model,
            "messages": [{"role": msg.role, "content": msg.content} for msg in messages],
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "top_p": config.top_p,
        }
        
        logger.debug(f"Sending request to {url} with payload: {json.dumps(payload, indent=2)}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout)
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    logger.debug(f"Received response: {json.dumps(data, indent=2)}")
                    
                    if "choices" not in data or not data["choices"]:
                        raise ValueError("Invalid response format from LM Studio")
                    
                    return [
                        ChatMessage(
                            role=choice["message"]["role"],
                            content=choice["message"]["content"]
                        )
                        for choice in data["choices"]
                    ]
                    
        except aiohttp.ClientError as e:
            logger.error(f"Error in LM Studio API request: {str(e)}")
            raise
    
    async def stream(
        self,
        messages: List[ChatMessage],
        config: Optional[GenerationConfig] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream chat response."""
        config = config or GenerationConfig()
        url = "/chat/completions"
        
        payload = {
            "model": self.config.model,
            "messages": self._format_messages(messages),
            "temperature": config.temperature or self.config.temperature,
            "max_tokens": config.max_tokens or self.config.max_tokens,
            "top_p": config.top_p or self.config.top_p,
            "stream": True,
            **kwargs
        }
        
        try:
            async with self.session.post(url, json=payload) as response:
                response.raise_for_status()
                
                async for line in response.content:
                    if line.startswith(b'data: '):
                        chunk = line[6:].strip()
                        if chunk == b'[DONE]':
                            break
                            
                        try:
                            data = json.loads(chunk)
                            if "choices" in data and data["choices"]:
                                delta = data["choices"][0].get("delta", {})
                                if "content" in delta:
                                    yield delta["content"]
                        except json.JSONDecodeError:
                            continue
                            
        except aiohttp.ClientError as e:
            logger.error(f"Error streaming from LM Studio: {e}")
            raise

    async def health_check(self):
        """Perform a health check on the LM Studio provider."""
        try:
            models = await self.get_models()
            if models:
                logger.info("LM Studio health check successful. Models available.")
                return True
            else:
                logger.warning("LM Studio health check: No models found.")
                return False
        except Exception as e:
            logger.error(f"LM Studio health check failed: {e}")
            return False

    async def get_models(self) -> List[Dict[str, Any]]:
        """Get available models from LM Studio."""
        url = "/models"
        
        try:
            async with self.session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                return data.get("data", [])
                
        except aiohttp.ClientError as e:
            logger.error(f"Error getting models from LM Studio: {e}")
            raise

# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_lm_studio():
        config = LMStudioConfig(
            base_url="http://172.24.240.1:1234/v1/",
            model="local-model",
            temperature=0.7
        )
        
        provider = LMStudioProvider(config)
        
        try:
            # Test chat completion
            messages = [
                ChatMessage(role="system", content="Eres un asistente útil."),
                ChatMessage(role="user", content="Hola, ¿cómo estás?")
            ]
            
            print("Testing chat completion...")
            response = await provider.chat(messages)
            print(f"Response: {response[-1].content}")
            
            # Test streaming
            print("\nTesting streaming...")
            async for chunk in provider.stream(messages):
                print(chunk, end="", flush=True)
            print("\n")
            
            # List available models
            print("\nAvailable models:")
            models = await provider.get_models()
            for model in models:
                print(f"- {model.get('id')} (owned_by: {model.get('owned_by', 'unknown')})")
                
        finally:
            await provider.close()
    
    asyncio.run(test_lm_studio())
