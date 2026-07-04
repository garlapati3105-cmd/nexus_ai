"""
Nexus AI — Agent Registry
Maintains a registry of all specialized AI agents in the system.
"""
from __future__ import annotations
from typing import Dict, List, Optional
from uuid import UUID
from app.ai.models.api import AgentIdentity
from app.ai.exceptions.errors import RegistryException

class AgentRegistry:
    """Registry maintaining metadata and references for all agents."""
    
    def __init__(self):
        self._agents: Dict[UUID, AgentIdentity] = {}
        
    def register_agent(self, agent: AgentIdentity) -> None:
        if agent.id in self._agents:
            raise RegistryException(f"Agent ID {agent.id} already exists.")
        self._agents[agent.id] = agent
        
    def get_agent(self, agent_id: UUID) -> AgentIdentity:
        if agent_id not in self._agents:
            raise RegistryException(f"Agent ID {agent_id} not found.")
        return self._agents[agent_id]
        
    def find_agents_by_role(self, role: str) -> List[AgentIdentity]:
        return [a for a in self._agents.values() if a.role == role]
        
    def list_all(self) -> List[AgentIdentity]:
        return list(self._agents.values())
