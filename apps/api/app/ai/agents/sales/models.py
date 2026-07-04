"""
Nexus AI — Sales AI Models
Strict schemas for Sales AI inputs, outputs, and KPI metrics.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class SalesScores(BaseModel):
    order_validation: float = Field(ge=0.0, le=1.0)
    medicine_availability: float = Field(ge=0.0, le=1.0)
    customer_satisfaction: float = Field(ge=0.0, le=1.0)
    sales_efficiency: float = Field(ge=0.0, le=1.0)
    recommendation_confidence: float = Field(ge=0.0, le=1.0)

class AlternativeMatch(BaseModel):
    original_medicine_id: str
    recommended_medicine_id: str
    generic_name: str
    price_difference: float
    reason: str
    evidence: str
    confidence: float
    expected_outcome: str

class AvailabilityDetails(BaseModel):
    medicine_id: str
    available: bool
    local_stock: int
    nearest_branch_id: Optional[str] = None
    nearest_branch_stock: Optional[int] = None
    transfer_recommended: Optional[bool] = None

class SalesAIResponse(BaseModel):
    agent: str = "SalesAI"
    timestamp: str
    order_id: Optional[str] = None
    validation_status: str # "APPROVED", "REJECTED_PRESCRIPTION", "REDIRECT_TRANSFER", "BACKORDER"
    scores: SalesScores
    availability: List[AvailabilityDetails]
    alternatives: List[AlternativeMatch]
    business_impact: Dict[str, Any]
    customer_notification: Dict[str, Any]
