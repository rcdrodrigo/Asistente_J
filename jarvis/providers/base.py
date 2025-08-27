from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class ChatMessage(BaseModel):
    role: str  # "user", "assistant", "system"
    content: str

class LLMProvider(ABC):
    """Base class for all LLM providers."""
    
    @abstractmethod
    async def initialize(self):
        """Initialize the provider."""
        raise NotImplementedError
        
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from a prompt."""
        raise NotImplementedError
        
    @abstractmethod
    async def close(self):
        """Cleanup resources."""
        raise NotImplementedError

    @abstractmethod
    async def health_check(self):
        """Perform a health check on the provider."""
        raise NotImplementedError