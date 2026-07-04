"""
Nexus AI — AI Kernel Models
Shared pydantic models for the AI Engine.
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from uuid import UUID

class ReasoningRequest(BaseModel):
    task_id: UUID
    agent_id: UUID
    goal: str
    context: Dict[str, Any]

class ReasoningResponse(BaseModel):
    decision: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    evidence: List[str]
    business_impact: str
    alternative_actions: List[str]
    risk_score: float = Field(ge=0.0, le=1.0)
    raw_output: Optional[str] = None
    tokens_used: int = 0

class AgentIdentity(BaseModel):
    id: UUID
    name: str
    description: str
    role: str
    capabilities: List[str]
    status: str
    version: str
    health: str

class WorkflowEvent(BaseModel):
    event_id: UUID
    workflow_id: UUID
    event_type: str
    payload: Dict[str, Any]
    timestamp: str
