"""
Nexus AI — Agent Interfaces
Contracts for metrics, hooks, and observers (Observer & Factory Patterns).
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List
from uuid import UUID

from app.ai.agents.models.core import AgentContext, AgentState, AgentRequest, AgentResponse

class AgentMemoryHooks(ABC):
    @abstractmethod
    async def load_short_term(self, context: AgentContext) -> Dict[str, Any]: pass
    
    @abstractmethod
    async def load_long_term(self, context: AgentContext) -> Dict[str, Any]: pass
    
    @abstractmethod
    async def commit_workflow_memory(self, workflow_id: UUID, data: Any) -> None: pass

class AgentLoggingHooks(ABC):
    @abstractmethod
    def log_execution_start(self, agent_id: UUID, request: AgentRequest) -> None: pass
    
    @abstractmethod
    def log_tool_usage(self, agent_id: UUID, tool_name: str, success: bool) -> None: pass
    
    @abstractmethod
    def log_execution_complete(self, agent_id: UUID, response: AgentResponse, duration_ms: float) -> None: pass
    
class AgentMetricsTracker(ABC):
    @abstractmethod
    def increment_execution(self, agent_id: UUID, success: bool) -> None: pass
    
    @abstractmethod
    def record_runtime(self, agent_id: UUID, ms: float) -> None: pass
    
    @abstractmethod
    def record_confidence(self, agent_id: UUID, score: float) -> None: pass
    
class AgentLifecycleObserver(ABC):
    @abstractmethod
    def on_state_change(self, agent_id: UUID, old_state: AgentState, new_state: AgentState) -> None: pass
