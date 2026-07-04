"""
Nexus AI — Agent Core Models
Types defining agent lifecycle, capabilities, requests, and context.
"""
from __future__ import annotations
from enum import Enum
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from uuid import UUID
import datetime

class AgentState(str, Enum):
    IDLE = 'idle'
    READY = 'ready'
    RUNNING = 'running'
    WAITING = 'waiting'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'

class AgentCapability(BaseModel):
    readable_data: List[str]
    writable_data: List[str]
    allowed_tools: List[str]
    approval_level: int
    maximum_scope: str

class AgentMetadata(BaseModel):
    id: UUID
    name: str
    description: str
    version: str
    capabilities: AgentCapability

class AgentHealth(BaseModel):
    status: str
    last_ping: datetime.datetime
    active_tasks: int
    error_rate: float

class AgentContext(BaseModel):
    user_id: Optional[UUID]
    role: str
    organization_id: UUID
    branch_id: Optional[UUID]
    workflow_id: UUID
    session_id: str
    business_context: Dict[str, Any]

class AgentRequest(BaseModel):
    task_id: UUID
    goal: str
    context: AgentContext
    parameters: Dict[str, Any]

class AgentResponse(BaseModel):
    task_id: UUID
    decision: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    reasoning: List[str]
    structured_output: Dict[str, Any]
    tools_executed: List[str]
    metrics: Dict[str, Any]
