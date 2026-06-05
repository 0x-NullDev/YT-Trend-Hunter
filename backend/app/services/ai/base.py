"""
YT Trend Hunter - AI Provider Abstraction Layer
Supports interchangeable AI providers: DeepSeek, OpenAI, Anthropic, Ollama, etc.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from loguru import logger


class AIProvider(ABC):
    """
    Abstract base class for AI providers.
    All providers must implement these methods.
    """

    @abstractmethod
    async def analyze_text(
        self,
        text: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """Analyze text using AI."""
        pass

    @abstractmethod
    async def generate_insights(
        self,
        data: Dict[str, Any],
        context: str,
    ) -> Dict[str, Any]:
        """Generate insights from data."""
        pass

    @abstractmethod
    async def classify_content(
        self,
        text: str,
        categories: List[str],
    ) -> Dict[str, float]:
        """Classify content into categories."""
        pass

    @abstractmethod
    async def generate_report(
        self,
        data: Dict[str, Any],
        report_type: str,
    ) -> str:
        """Generate a report using AI."""
        pass

    @abstractmethod
    async def extract_entities(
        self,
        text: str,
    ) -> List[Dict[str, str]]:
        """Extract entities from text."""
        pass


class DeepSeekProvider(AIProvider):
    """DeepSeek AI provider implementation."""

    def __init__(self, api_key: str, model: str = "deepseek-chat"):
        self.api_key = api_key
        self.model = model
        self.logger = logger.bind(provider="deepseek")

    async def analyze_text(self, text: str, prompt: str, temperature: float = 0.7, max_tokens: int = 2000) -> str:
        # TODO: Implement DeepSeek API call
        self.logger.info(f"DeepSeek analyze_text called (text length: {len(text)})")
        return f"DeepSeek analysis of: {text[:100]}..."

    async def generate_insights(self, data: Dict[str, Any], context: str) -> Dict[str, Any]:
        self.logger.info(f"DeepSeek generate_insights called (context: {context})")
        return {"insights": ["AI-powered insight generation pending"]}

    async def classify_content(self, text: str, categories: List[str]) -> Dict[str, float]:
        return {cat: 0.5 for cat in categories}

    async def generate_report(self, data: Dict[str, Any], report_type: str) -> str:
        return f"# {report_type.title()} Report\n\nAI-generated report pending."

    async def extract_entities(self, text: str) -> List[Dict[str, str]]:
        return []


class OpenAIProvider(AIProvider):
    """OpenAI provider implementation."""

    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.api_key = api_key
        self.model = model
        self.logger = logger.bind(provider="openai")

    async def analyze_text(self, text: str, prompt: str, temperature: float = 0.7, max_tokens: int = 2000) -> str:
        self.logger.info(f"OpenAI analyze_text called (text length: {len(text)})")
        return f"OpenAI analysis of: {text[:100]}..."

    async def generate_insights(self, data: Dict[str, Any], context: str) -> Dict[str, Any]:
        self.logger.info(f"OpenAI generate_insights called (context: {context})")
        return {"insights": ["AI-powered insight generation pending"]}

    async def classify_content(self, text: str, categories: List[str]) -> Dict[str, float]:
        return {cat: 0.5 for cat in categories}

    async def generate_report(self, data: Dict[str, Any], report_type: str) -> str:
        return f"# {report_type.title()} Report\n\nAI-generated report pending."

    async def extract_entities(self, text: str) -> List[Dict[str, str]]:
        return []


class AnthropicProvider(AIProvider):
    """Anthropic Claude provider implementation."""

    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229"):
        self.api_key = api_key
        self.model = model
        self.logger = logger.bind(provider="anthropic")

    async def analyze_text(self, text: str, prompt: str, temperature: float = 0.7, max_tokens: int = 2000) -> str:
        self.logger.info(f"Anthropic analyze_text called (text length: {len(text)})")
        return f"Anthropic analysis of: {text[:100]}..."

    async def generate_insights(self, data: Dict[str, Any], context: str) -> Dict[str, Any]:
        self.logger.info(f"Anthropic generate_insights called (context: {context})")
        return {"insights": ["AI-powered insight generation pending"]}

    async def classify_content(self, text: str, categories: List[str]) -> Dict[str, float]:
        return {cat: 0.5 for cat in categories}

    async def generate_report(self, data: Dict[str, Any], report_type: str) -> str:
        return f"# {report_type.title()} Report\n\nAI-generated report pending."

    async def extract_entities(self, text: str) -> List[Dict[str, str]]:
        return []


class OllamaProvider(AIProvider):
    """Ollama (local) provider implementation."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        self.base_url = base_url
        self.model = model
        self.logger = logger.bind(provider="ollama")

    async def analyze_text(self, text: str, prompt: str, temperature: float = 0.7, max_tokens: int = 2000) -> str:
        self.logger.info(f"Ollama analyze_text called (text length: {len(text)})")
        return f"Ollama analysis of: {text[:100]}..."

    async def generate_insights(self, data: Dict[str, Any], context: str) -> Dict[str, Any]:
        self.logger.info(f"Ollama generate_insights called (context: {context})")
        return {"insights": ["AI-powered insight generation pending"]}

    async def classify_content(self, text: str, categories: List[str]) -> Dict[str, float]:
        return {cat: 0.5 for cat in categories}

    async def generate_report(self, data: Dict[str, Any], report_type: str) -> str:
        return f"# {report_type.title()} Report\n\nAI-generated report pending."

    async def extract_entities(self, text: str) -> List[Dict[str, str]]:
        return []


class AIFactory:
    """
    Factory for creating AI provider instances.
    Supports DeepSeek, OpenAI, Anthropic, Ollama, and future providers.
    """

    providers = {
        "deepseek": DeepSeekProvider,
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "ollama": OllamaProvider,
    }

    @classmethod
    def create_provider(
        cls,
        provider_name: str = "openai",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> AIProvider:
        """
        Create an AI provider instance.
        
        Args:
            provider_name: Name of the provider (deepseek, openai, anthropic, ollama)
            api_key: API key for the provider
            model: Model name to use
            base_url: Base URL (for Ollama)
            
        Returns:
            AIProvider instance
        """
        provider_class = cls.providers.get(provider_name.lower())

        if not provider_class:
            logger.warning(f"Unknown provider '{provider_name}', falling back to OpenAI")
            provider_class = OpenAIProvider

        if provider_name.lower() == "ollama":
            return provider_class(base_url=base_url or "http://localhost:11434")
        else:
            return provider_class(api_key=api_key or "", model=model)


# Global AI provider instance (configured via settings)
from app.core.config import settings

# Map provider name to actual settings
_PROVIDER_API_KEY_MAP = {
    "deepseek": settings.DEEPSEEK_API_KEY,
    "openai": settings.OPENAI_API_KEY,
    "anthropic": settings.ANTHROPIC_API_KEY,
    "ollama": "",
}

_PROVIDER_MODEL_MAP = {
    "deepseek": settings.DEEPSEEK_MODEL,
    "openai": settings.OPENAI_MODEL,
    "anthropic": settings.ANTHROPIC_MODEL,
    "ollama": settings.OLLAMA_MODEL,
}

_PROVIDER_BASE_URL_MAP = {
    "deepseek": settings.DEEPSEEK_API_BASE,
    "openai": "",
    "anthropic": "",
    "ollama": settings.OLLAMA_API_BASE,
}

_default_provider = settings.AI_DEFAULT_PROVIDER.value

ai_provider = AIFactory.create_provider(
    provider_name=_default_provider,
    api_key=_PROVIDER_API_KEY_MAP.get(_default_provider, ""),
    model=_PROVIDER_MODEL_MAP.get(_default_provider, ""),
    base_url=_PROVIDER_BASE_URL_MAP.get(_default_provider, ""),
)
