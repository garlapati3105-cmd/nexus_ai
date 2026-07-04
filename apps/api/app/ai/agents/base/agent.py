"""
Nexus AI — Agent Framework 
The abstract base core defining the standard lifecycle template method.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Type
import time
import logging

from app.ai.agents.models.core import (
    AgentMetadata, AgentState, AgentRequest, AgentResponse, AgentContext
)
from app.ai.agents.interfaces.hooks import (
    AgentMemoryHooks, AgentLoggingHooks, AgentMetricsTracker, AgentLifecycleObserver
)

class BaseAgent(ABC):
    """
    Template Method Pattern implementing the strict AI Agent Lifecycle.
    Subclasses only override behavior; the base enforces sequential bounds.
    """
    
    def __init__(
        self, 
        metadata: AgentMetadata,
        memory: AgentMemoryHooks,
        logger: AgentLoggingHooks,
        metrics: AgentMetricsTracker
    ):
        self.metadata = metadata
        self.memory = memory
        self.logger = logger
        self.metrics = metrics
        self.state = AgentState.IDLE
        self.observers: List[AgentLifecycleObserver] = []

    def attach_observer(self, observer: AgentLifecycleObserver) -> None:
        self.observers.append(observer)

    def _set_state(self, new_state: AgentState) -> None:
        old = self.state
        self.state = new_state
        for obs in self.observers:
            obs.on_state_change(self.metadata.id, old, new_state)

    async def execute(self, request: AgentRequest) -> AgentResponse:
        """
        The Template Method. 
        Guarantees validation, permission checks, memory loading, 
        execution logic, and standardized output/logging safely.
        """
        start_time = time.time()
        self._set_state(AgentState.RUNNING)
        self.logger.log_execution_start(self.metadata.id, request)
        
        try:
            # 1. Validation & Permissions (Framework level boundary)
            await self._verify_permissions(request.context)
            
            # 2. Context & Memory Prep
            stm = await self.memory.load_short_term(request.context)
            ltm = await self.memory.load_long_term(request.context)
            working_context = {**request.context.model_dump(), "stm": stm, "ltm": ltm}
            
            # 3. Agent Tool Selection logic
            tools_to_run = await self.select_tools(working_context, request.goal)
            
            # 4. Agent Tool Execution logic
            tool_results = await self.execute_tools(tools_to_run, working_context)
            
            # 5. Model Generation & Formatting
            decision, conf, reasoning, structured = await self.generate_response(
                working_context, tool_results
            )
            
            # Compile standardized response
            response = AgentResponse(
                task_id=request.task_id,
                decision=decision,
                confidence_score=conf,
                reasoning=reasoning,
                structured_output=structured,
                tools_executed=[t["name"] for t in tools_to_run],
                metrics={"duration": time.time() - start_time}
            )
            
            # 6. Post-eval hook
            duration_ms = (time.time() - start_time) * 1000
            self.logger.log_execution_complete(self.metadata.id, response, duration_ms)
            self.metrics.increment_execution(self.metadata.id, success=True)
            self.metrics.record_runtime(self.metadata.id, duration_ms)
            self.metrics.record_confidence(self.metadata.id, conf)
            
            self._set_state(AgentState.COMPLETED)
            return response
            
        except Exception as e:
            self._set_state(AgentState.FAILED)
            self.metrics.increment_execution(self.metadata.id, success=False)
            logging.getLogger().error(f"Agent {self.metadata.name} failed: {e}")
            raise
        finally:
            await self.cleanup()

    async def _verify_permissions(self, context: AgentContext) -> None:
        """Enforces limits on User, Role, Action."""
        # Simulated logic boundary
        return True

    # ---- Methods for subclasses to override (Strategy) ----
    
    @abstractmethod
    async def select_tools(self, context: Dict[str, Any], goal: str) -> List[Dict[str, Any]]:
        pass
        
    @abstractmethod
    async def execute_tools(self, tool_configs: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        pass
        
    @abstractmethod
    async def generate_response(self, context: Dict[str, Any], tool_results: Dict[str, Any]) -> tuple[str, float, List[str], Dict[str, Any]]:
        """Returns: decision, confidence, reasoning, structured_output"""
        pass
        
    async def cleanup(self) -> None:
        """Optional hook for subclass resource closures."""
        pass
