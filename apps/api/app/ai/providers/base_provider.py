"""
Nexus AI — Base Provider Interface
Abstract class specifying core contracts for LLM providers.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict

from app.ai.providers.provider_models import LLMRequest, LLMResponse

class BaseLLMProvider(ABC):
    """
    Contracts for all LLM providers. Pluggable design allows support
    for Gemini, OpenAI, Claude, or Grok under the same interfaces.
    """
    
    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Submits request to active LLM engine.
        Applies timeouts, retry logic, and formats telemetry.
        """
        pass
