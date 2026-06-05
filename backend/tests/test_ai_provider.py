"""
Tests for the AI Provider abstraction layer.
"""

import pytest

from app.services.ai.base import (
    AIProvider,
    AIFactory,
    DeepSeekProvider,
    OpenAIProvider,
    AnthropicProvider,
    OllamaProvider,
)


class TestAIFactory:
    """Test suite for AIFactory."""

    def test_create_openai_provider(self):
        """Test creating OpenAI provider."""
        provider = AIFactory.create_provider("openai", api_key="test-key")
        assert isinstance(provider, OpenAIProvider)

    def test_create_deepseek_provider(self):
        """Test creating DeepSeek provider."""
        provider = AIFactory.create_provider("deepseek", api_key="test-key")
        assert isinstance(provider, DeepSeekProvider)

    def test_create_anthropic_provider(self):
        """Test creating Anthropic provider."""
        provider = AIFactory.create_provider("anthropic", api_key="test-key")
        assert isinstance(provider, AnthropicProvider)

    def test_create_ollama_provider(self):
        """Test creating Ollama provider."""
        provider = AIFactory.create_provider("ollama")
        assert isinstance(provider, OllamaProvider)

    def test_create_unknown_provider_fallback(self):
        """Test fallback to OpenAI for unknown provider."""
        provider = AIFactory.create_provider("unknown", api_key="test-key")
        assert isinstance(provider, OpenAIProvider)

    def test_create_provider_without_api_key(self):
        """Test creating provider without API key."""
        provider = AIFactory.create_provider("openai")
        assert isinstance(provider, OpenAIProvider)

    def test_create_provider_with_custom_model(self):
        """Test creating provider with custom model."""
        provider = AIFactory.create_provider(
            "openai",
            api_key="test-key",
            model="gpt-4-turbo",
        )
        assert provider.model == "gpt-4-turbo"

    def test_create_ollama_with_custom_url(self):
        """Test creating Ollama with custom base URL."""
        provider = AIFactory.create_provider(
            "ollama",
            base_url="http://custom:11434",
        )
        assert provider.base_url == "http://custom:11434"


class TestAIProviderInterface:
    """Test suite for AIProvider interface."""

    @pytest.mark.asyncio
    async def test_openai_analyze_text(self):
        """Test OpenAI analyze_text method."""
        provider = OpenAIProvider(api_key="test-key")
        result = await provider.analyze_text("Test text", "Analyze this")
        assert isinstance(result, str)
        assert "OpenAI" in result

    @pytest.mark.asyncio
    async def test_deepseek_analyze_text(self):
        """Test DeepSeek analyze_text method."""
        provider = DeepSeekProvider(api_key="test-key")
        result = await provider.analyze_text("Test text", "Analyze this")
        assert isinstance(result, str)
        assert "DeepSeek" in result

    @pytest.mark.asyncio
    async def test_anthropic_analyze_text(self):
        """Test Anthropic analyze_text method."""
        provider = AnthropicProvider(api_key="test-key")
        result = await provider.analyze_text("Test text", "Analyze this")
        assert isinstance(result, str)
        assert "Anthropic" in result

    @pytest.mark.asyncio
    async def test_ollama_analyze_text(self):
        """Test Ollama analyze_text method."""
        provider = OllamaProvider()
        result = await provider.analyze_text("Test text", "Analyze this")
        assert isinstance(result, str)
        assert "Ollama" in result

    @pytest.mark.asyncio
    async def test_generate_insights(self):
        """Test generate_insights method."""
        provider = OpenAIProvider(api_key="test-key")
        result = await provider.generate_insights(
            {"data": "test"},
            "Test context",
        )
        assert "insights" in result

    @pytest.mark.asyncio
    async def test_classify_content(self):
        """Test classify_content method."""
        provider = OpenAIProvider(api_key="test-key")
        result = await provider.classify_content(
            "Test content",
            ["tech", "music", "sports"],
        )
        assert len(result) == 3
        assert all(0 <= v <= 1 for v in result.values())

    @pytest.mark.asyncio
    async def test_generate_report(self):
        """Test generate_report method."""
        provider = OpenAIProvider(api_key="test-key")
        result = await provider.generate_report(
            {"data": "test"},
            "trend",
        )
        assert isinstance(result, str)
        assert "Report" in result

    @pytest.mark.asyncio
    async def test_extract_entities(self):
        """Test extract_entities method."""
        provider = OpenAIProvider(api_key="test-key")
        result = await provider.extract_entities("Test text")
        assert isinstance(result, list)
