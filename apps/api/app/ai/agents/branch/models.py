"""
Nexus AI — Branch AI Models
Strict schemas for the Daily Report, Status, and Actions.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class BranchHealthScores(BaseModel):
    overall: float = Field(ge=0.0, le=1.0)
    inventory_health: float = Field(ge=0.0, le=1.0)
    order_efficiency: float = Field(ge=0.0, le=1.0)
    customer_service: float = Field(ge=0.0, le=1.0)
    staff_productivity: float = Field(ge=0.0, le=1.0)

class BranchRecommendation(BaseModel):
    action_type: str
    target_item: str
    reason: str
    evidence: str
    confidence: float
    business_impact: str
    alternative_actions: List[str]

class BranchAIResponse(BaseModel):
    agent: str = "BranchAI"
    branch_id: str
    timestamp: str
    health_scores: BranchHealthScores
    daily_revenue: float
    orders_completed: int
    pending_orders: int
    low_stock_items: List[str]
    expiring_medicines: List[str]
    transfer_requests_sent: int
    recommendations: List[BranchRecommendation]
    escalations_to_regional: List[str]
