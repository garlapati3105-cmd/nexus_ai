"""
Nexus AI — Provider Configuration
Settings configuration module utilizing Pydantic settings.
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

class ProviderSettings(BaseSettings):
    provider_name: str = Field("grok", env="LLM_PROVIDER")
    
    # xAI Grok settings
    grok_api_key: str = Field("xai-mock-key-12345", env="GROK_API_KEY")
    grok_model: str = Field("grok-2-1212", env="GROK_MODEL")
    grok_api_url: str = Field("https://api.x.ai/v1/chat/completions", env="GROK_API_URL")
    
    # Standard thresholds
    api_timeout_seconds: float = 15.0
    max_retries: int = 3
    retry_backoff_factor: float = 2.0
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = ProviderSettings()
