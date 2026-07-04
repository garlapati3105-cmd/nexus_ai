"""
Nexus AI — Explainability Models
Defines schema constraints for Explanation profiles, reasoning metrics, and timeline items.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class ExplanationProfile(BaseModel):
    reasoning: str
    evidence_used: List[str] = Field(default_factory=list)
    knowledge_sources: List[str] = Field(default_factory=list)
    confidence_score: float = Field(ge=0.0, le=1.0)
    business_impact: str
    alternative_recommendations: List[str] = Field(default_factory=list)
    estimated_savings: float = Field(default=0.0)
    expected_outcome: str
    risk_level: str # "LOW" | "MEDIUM" | "HIGH"
    timestamp: str
    responsible_agent: str
    workflow_id: str

class DecisionRecord(BaseModel):
    decision_id: str
    workflow_id: str
    agent_name: str
    action_taken: str
    explanation: ExplanationProfile
    state_mutations: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str

class ExplainabilityTimeline(BaseModel):
    workflow_id: str
    history: List[DecisionRecord] = Field(default_factory=list)
    duration_ms: float = 0.0
