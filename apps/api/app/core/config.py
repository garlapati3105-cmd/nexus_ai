"""
Nexus AI — Application Configuration
Loads environment variables and provides typed access to all settings.
"""
import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Supabase
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str

    # Application
    APP_TITLE: str = "Nexus AI Backend - Enterprise Workflow API"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    # Organization
    ORG_ID: str = "88888888-8888-4888-a888-888888888888"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Cached singleton for settings."""
    return Settings()
