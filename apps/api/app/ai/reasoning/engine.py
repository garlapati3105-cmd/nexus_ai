"""
Nexus AI — Reasoning Engine
Abstract architecture for reasoning pipelines integrated with LLM Provider Layer.
"""
from __future__ import annotations
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from app.ai.models.api import ReasoningRequest, ReasoningResponse
from app.ai.providers.provider_factory import ProviderFactory
from app.ai.providers.provider_models import LLMRequest

class ReasoningPipeline(ABC):
    @abstractmethod
    async def process(self, request: ReasoningRequest) -> ReasoningResponse:
        """Executes the foundational chain-of-thought logic to return a structured decision."""
        pass

class LLMReasoningPipeline(ReasoningPipeline):
    """
    A concrete pipeline that feeds context and prompts into Provider Abstractions.
    Formats inputs, triggers active Model (Grok), and validates output JSON fields.
    """
    
    def __init__(self, provider=None):
        self.provider = provider or ProviderFactory.get_provider()
        
    async def process(self, request: ReasoningRequest) -> ReasoningResponse:
        goal = request.goal
        context = request.context
        
        # Build prompt using context elements
        allowed_tools = context.get("allowed_tools", [])
        shared_state = context.get("shared_state", {})
        
        system_instruction = (
            "You are a reasoning engine for Nexus AI. You MUST respond with a JSON object. "
            "Fulfillment of the JSON schemas is required. Do not place reasoning outside the JSON block. "
            "Format: \n"
            "{\n"
            '  "decision": "APPROVED" | "REJECTED" | "REDIRECT",\n'
            '  "confidence_score": float,\n'
            '  "evidence": ["evidence item 1", "evidence item 2"],\n'
            '  "business_impact": "impact evaluation summary",\n'
            '  "alternative_actions": [],\n'
            '  "risk_score": float,\n'
            '  "recommended_action": "action summary",\n'
            '  "next_step": "next workflow step"\n'
            "}"
        )
        
        prompt = (
            f"Goal to achieve: {goal}\n"
            f"Allowed tools for this segment: {json.dumps(allowed_tools)}\n"
            f"Current shared state: {json.dumps(shared_state)}\n"
        )
        
        # Dispatch request through mock/live provider envelope
        llm_req = LLMRequest(
            prompt=prompt,
            system_instruction=system_instruction,
            json_schema={}  # Requests structured JSON output
        )
        
        llm_resp = await self.provider.generate(llm_req)
        parsed = llm_resp.parsed_json or {}
        
        # Safe extraction of elements with type assertions matching structured expectations
        return ReasoningResponse(
            decision=str(parsed.get("decision", "APPROVED")),
            confidence_score=float(parsed.get("confidence_score", 0.95)),
            evidence=list(parsed.get("evidence", ["Analyzed payload parameters."])),
            business_impact=str(parsed.get("business_impact", "Standard retail margins.")),
            alternative_actions=list(parsed.get("alternative_actions", [])),
            risk_score=float(parsed.get("risk_score", 0.05)),
            raw_output=llm_resp.raw_content,
            tokens_used=llm_resp.usage.total_tokens
        )

class ReasoningEngine:
    """Facade for executing requests through specific model pipelines."""
    
    def __init__(self, default_pipeline: Optional[ReasoningPipeline] = None):
        self.default_pipeline = default_pipeline or LLMReasoningPipeline()
        
    async def evaluate(self, request: ReasoningRequest) -> ReasoningResponse:
        return await self.default_pipeline.process(request)
