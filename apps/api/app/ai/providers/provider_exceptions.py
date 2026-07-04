"""
Nexus AI — Provider Exceptions
Custom errors for provider-level API calls.
"""
from __future__ import annotations

class ProviderException(Exception):
    """Base exception for all LLM provider errors."""
    pass

class ProviderTimeout(ProviderException):
    """Raised when the LLM provider fails to respond in time."""
    pass

class ProviderRateLimit(ProviderException):
    """Raised when API rate limits are hit."""
    pass

class ProviderMalformedJSON(ProviderException):
    """Raised when structured parser fails to extract valid JSON."""
    pass
