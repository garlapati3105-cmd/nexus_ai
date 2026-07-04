"""
Nexus AI — Memory Manager
Interfaces for short/long-term and semantic memory.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List

class AIMemoryProvider(ABC):
    @abstractmethod
    async def save_interaction(self, session_id: str, role: str, content: str) -> None:
        pass
        
    @abstractmethod
    async def get_history(self, session_id: str, limit: int = 10) -> List[Dict[str, str]]:
        pass
        
    @abstractmethod
    async def semantic_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        pass

class MemoryManager:
    """Facade wrapping different memory providers."""
    def __init__(self, provider: AIMemoryProvider):
        self.provider = provider
        
    async def store_session_state(self, session_id: str, state: Dict[str, Any]):
        """Store transient workflow state."""
        pass
        
    async def load_session_state(self, session_id: str) -> Dict[str, Any]:
        """Load transient workflow state."""
        return {}
