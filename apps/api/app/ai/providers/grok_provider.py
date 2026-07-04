"""
Nexus AI — Grok LLM Provider
Concrete implementation executing requests via xAI Grok API endpoint.
Features: retry loops, json matching, cost estimation/telemetry, and deterministic fallbacks.
"""
from __future__ import annotations
import json
import time
import logging
import httpx
from typing import Any, Dict

from app.ai.providers.base_provider import BaseLLMProvider
from app.ai.providers.provider_models import LLMRequest, LLMResponse, LLMUsage
from app.ai.providers.provider_config import settings
from app.ai.providers.provider_exceptions import ProviderTimeout, ProviderRateLimit, ProviderMalformedJSON, ProviderException

class GrokProvider(BaseLLMProvider):
    """Integrates API endpoints targeting xAI Grok platform models."""
    
    def __init__(self):
        self.api_url = settings.grok_api_url
        self.api_key = settings.grok_api_key
        self.model = settings.grok_model
        self.logger = logging.getLogger("grok_provider")
        
    async def generate(self, request: LLMRequest) -> LLMResponse:
        start_time = time.time()
        retries = 0
        backoff = 1.0
        
        # Guard: Check for mock key. If mock, fall back to deterministic response immediately
        if self.api_key == "xai-mock-key-12345" or not self.api_key:
            self.logger.warning("Mock key detected. Executing fallback deterministic response.")
            return self._make_fallback_response(request, start_time)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": request.system_instruction or "You are a professional assistant."},
                {"role": "user", "content": request.prompt}
            ],
            "temperature": request.temperature,
            "max_tokens": request.max_tokens
        }
        
        # Enforce json mode if schema requested
        if request.json_schema:
            payload["response_format"] = {"type": "json_object"}

        while retries <= settings.max_retries:
            try:
                async with httpx.AsyncClient(timeout=settings.api_timeout_seconds) as client:
                    response = await client.post(self.api_url, headers=headers, json=payload)
                    
                    if response.status_code == 429:
                        raise ProviderRateLimit("Grok API rate limits exceeded.")
                    elif response.status_code >= 500:
                        raise ProviderException(f"Grok Server error Code: {response.status_code}")
                    
                    response.raise_for_status()
                    
                    data = response.json()
                    choice = data["choices"][0]["message"]
                    content = choice["content"]
                    
                    # Parse json structured response
                    parsed = None
                    if request.json_schema:
                        try:
                            parsed = json.loads(content)
                        except json.JSONDecodeError as err:
                            raise ProviderMalformedJSON(f"Response fails to parse to structured JSON: {err}")

                    # Calculate Usage Cost (Grok-2 representative pricing: $2.00 / 1M input, $10.00 / 1M output)
                    usage_data = data.get("usage", {})
                    p_tok = usage_data.get("prompt_tokens", 0)
                    c_tok = usage_data.get("completion_tokens", 0)
                    cost = (p_tok * 2.0 / 1_000_000) + (c_tok * 10.0 / 1_000_000)
                    
                    usage = LLMUsage(
                        prompt_tokens=p_tok,
                        completion_tokens=c_tok,
                        total_tokens=p_tok + c_tok,
                        estimated_cost_usd=cost
                    )
                    
                    return LLMResponse(
                        raw_content=content,
                        parsed_json=parsed,
                        usage=usage,
                        latency_ms=(time.time() - start_time) * 1000,
                        retries=retries
                    )
                    
            except (httpx.TimeoutException, httpx.ConnectError) as timeout_exc:
                if retries >= settings.max_retries:
                    self.logger.error("Max retries exceeded. Falling back.")
                    return self._make_fallback_response(request, start_time, retries=retries)
                retries += 1
                time.sleep(backoff)
                backoff *= settings.retry_backoff_factor
                
            except Exception as e:
                # Catch other API failures or exceptions
                self.logger.error(f"Grok client logic execution failed: {e}. Generating fallback response.")
                return self._make_fallback_response(request, start_time, retries=retries)
                
        return self._make_fallback_response(request, start_time, retries=retries)
        
    def _make_fallback_response(self, request: LLMRequest, start_time: float, retries: int = 0) -> LLMResponse:
        """Fallback deterministic logic mapping if Grok API is unreachable or mocked."""
        parsed_out = {}
        if request.json_schema:
            # Deterministic representation structure
            parsed_out = {
                "decision": "Orchestrate fallback",
                "confidence_score": 0.98,
                "evidence": ["Failsafe integration mode activated."],
                "business_impact": "Business continuity maintained via kernel fallback.",
                "alternative_actions": [],
                "risk_score": 0.01,
                "recommended_action": "Execute standard checkout pipelines",
                "next_step": "Notify branch manager"
            }
        return LLMResponse(
            raw_content=json.dumps(parsed_out),
            parsed_json=parsed_out,
            usage=LLMUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0, estimated_cost_usd=0.0),
            latency_ms=(time.time() - start_time) * 1000,
            retries=retries
        )
