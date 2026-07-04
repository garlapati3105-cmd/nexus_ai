"""
Nexus AI — Provider Models
Schemas for LLM inputs, structured outputs, metrics, and token costs.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class LLMUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0

class LLMRequest(BaseModel):
    prompt: str
    system_instruction: Optional[str] = None
    temperature: float = 0.1
    max_tokens: int = 2048
    json_schema: Optional[Dict[str, Any]] = None

class LLMResponse(BaseModel):
    raw_content: str
    parsed_json: Optional[Dict[str, Any]] = None
    usage: LLMUsage = Field(default_factory=LLMUsage)
    latency_ms: float = 0.0
    retries: int = 0
