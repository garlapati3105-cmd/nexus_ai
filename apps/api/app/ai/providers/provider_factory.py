"""
Nexus AI — Provider Factory
Resolves the active LLM provider instance dynamically at runtime.
"""
from __future__ import annotations
from typing import Dict, Type

from app.ai.providers.base_provider import BaseLLMProvider
from app.ai.providers.grok_provider import GrokProvider
from app.ai.providers.provider_config import settings

class ProviderFactory:
    """Dynamic resolution container. Supports multi-model pluggability."""
    
    _providers: Dict[str, Type[BaseLLMProvider]] = {
        "grok": GrokProvider
    }
    
    @classmethod
    def register_provider(cls, name: str, provider_cls: Type[BaseLLMProvider]) -> None:
        cls._providers[name.lower()] = provider_cls
        
    @classmethod
    def get_provider(cls, name: str = None) -> BaseLLMProvider:
        provider_name = (name or settings.provider_name).lower()
        if provider_name not in cls._providers:
            raise ValueError(f"LLM Provider {provider_name} not registered in factory.")
        return cls._providers[provider_name]()
