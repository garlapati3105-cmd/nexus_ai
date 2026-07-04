"""
Nexus AI — Communication Layer
Event routing and message passing between Agents and the Kernel (Concrete implementation).
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Callable, Coroutine
from uuid import UUID
from app.ai.models.api import WorkflowEvent

class MessageBusInterface(ABC):
    @abstractmethod
    async def publish(self, event: WorkflowEvent) -> None:
        pass
        
    @abstractmethod
    async def subscribe(self, event_type: str, handler: Callable[[WorkflowEvent], Coroutine[Any, Any, None]]) -> None:
        pass

class InMemoryMessageBus(MessageBusInterface):
    """Simple in-memory pub-sub event bus matching the abstraction contract."""
    
    def __init__(self):
        self._listeners: Dict[str, List[Callable[[WorkflowEvent], Coroutine[Any, Any, None]]]] = {}

    async def publish(self, event: WorkflowEvent) -> None:
        listeners = self._listeners.get(event.event_type, [])
        for handler in listeners:
            await handler(event)

    async def subscribe(self, event_type: str, handler: Callable[[WorkflowEvent], Coroutine[Any, Any, None]]) -> None:
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(handler)

class AgentCommunicationLayer:
    """Manages secure internal message passing."""
    
    def __init__(self, bus: MessageBusInterface):
        self.bus = bus
        self._state_history: List[Dict[str, Any]] = []
        
    async def send_agent_to_agent_message(
        self, 
        source_agent_id: UUID, 
        target_agent_id: UUID, 
        message: Dict[str, Any]
    ) -> None:
        """Point-to-point communication."""
        event = WorkflowEvent(
            event_id=UUID(int=1), # Temporary ID
            workflow_id=UUID(int=1),
            event_type=f"agent_to_agent:{target_agent_id}",
            payload={"source": str(source_agent_id), "message": message},
            timestamp=datetime.datetime.utcnow().isoformat()
        )
        await self.bus.publish(event)
        
    async def broadcast_context_update(self, workflow_id: UUID, new_context: Dict[str, Any]) -> None:
        """Broadcast shared state updates."""
        event = WorkflowEvent(
            event_id=UUID(int=2),
            workflow_id=workflow_id,
            event_type="context_update",
            payload=new_context,
            timestamp=datetime.datetime.utcnow().isoformat()
        )
        self._state_history.append(new_context)
        await self.bus.publish(event)
        
import datetime
