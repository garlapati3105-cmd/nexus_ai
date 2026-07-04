"""
Nexus AI — Regional AI Models
Strict structures emitted and parsed by the Regional AI.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class BusinessImpact(BaseModel):
    category: str
    expected_savings: float
    description: str
    risk_score: float = Field(ge=0.0, le=1.0)

class TransferRecommendation(BaseModel):
    from_branch: str
    to_branch: str
    medicine: str
    quantity: int
    freight_cost: float
    net_benefit: float

class RegionalAIResponse(BaseModel):
    agent: str = "RegionalAI"
    status: str
    confidence: float
    reasoning: List[str]
    recommendations: List[TransferRecommendation]
    businessImpact: BusinessImpact
    requiredApprovals: List[str]
    nextActions: List[str]
    timestamp: str
