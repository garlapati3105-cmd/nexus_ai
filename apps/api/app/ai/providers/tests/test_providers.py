import pytest
from unittest.mock import AsyncMock, MagicMock

from app.ai.providers.provider_factory import ProviderFactory
from app.ai.providers.base_provider import BaseLLMProvider
from app.ai.providers.provider_models import LLMRequest

@pytest.mark.asyncio
async def test_provider_factory_grok_resolution():
    """Verify that factory correctly instantiates GrokProvider by default."""
    provider = ProviderFactory.get_provider("grok")
    assert provider is not None

@pytest.mark.asyncio
async def test_grok_mock_key_fallback():
    """Verify that mock keys trigger the deterministic fallback safety payload."""
    provider = ProviderFactory.get_provider("grok")
    response = await provider.generate(LLMRequest(prompt="test", system_instruction="system"))
    assert response.parsed_json is not None
    assert response.parsed_json["decision"] == "Orchestrate fallback"
