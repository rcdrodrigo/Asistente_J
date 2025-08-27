# -*- coding: utf-8 -*-
"""
providers/openai.py — Cliente mínimo para OpenAI-compatible.
"""
from typing import List, Dict, Optional
import os
import json
import urllib.request
import logging
import aiohttp
from pydantic import BaseModel, Field
from .base import LLMProvider

logger = logging.getLogger(__name__)

class OpenAIConfig(BaseModel):
    api_key: str
    model: str
    timeout: int = Field(default=60, gt=0)

class OpenAIProvider(LLMProvider):
    def __init__(self, config: OpenAIConfig):
        self.config = config
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self._session: Optional[aiohttp.ClientSession] = None

    async def initialize(self):
        """Initialize the OpenAI provider."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                base_url=self.base_url,
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
        logger.info(f"OpenAI provider initialized with base_url: {self.base_url}")

    async def health_check(self):
        """Perform a health check on the OpenAI provider."""
        try:
            if self._session is None or self._session.closed:
                await self.initialize()
            
            # Attempt to make a small request to verify connectivity
            async with self._session.get(f"{self.base_url}/models") as response:
                response.raise_for_status()
                data = await response.json()
                if data and "data" in data:
                    logger.info("OpenAI health check successful.")
                    return True
                else:
                    logger.warning("OpenAI health check: No models found or unexpected response.")
                    return False
        except Exception as e:
            logger.error(f"OpenAI health check failed: {e}")
            return False

    async def generate(self, prompt: str, **kwargs) -> str:
        messages = [{"role": "user", "content": prompt}]
        response = await self.chat(messages, **kwargs)
        return response

    async def chat(self, messages: List[Dict[str,str]]) -> str:
        url = f"{self.base_url}/chat/completions"
        payload = {"model": self.config.model, "messages": messages, "temperature": 0.2}
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}"
        }
        
        try:
            async with self._session.post(url, json=payload, headers=headers, timeout=self.config.timeout) as response:
                response.raise_for_status()
                data = await response.json()
                return data.get("choices", [{"message": {"content": ""}}])[0]["message"]["content"].strip()
        except aiohttp.ClientError as e:
            logger.error(f"Error in OpenAI API request: {str(e)}")
            raise

    async def close(self):
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
