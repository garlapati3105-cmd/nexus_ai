"""
Nexus AI — Inventory AI Models
Strict schemas for inventory reporting, scoring, and optimized recommendations.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class InventoryScores(BaseModel):
    inventory_health: float = Field(ge=0.0, le=1.0)
    medicine_criticality: float = Field(ge=0.0, le=1.0)
    expiry_risk: float = Field(ge=0.0, le=1.0)
    transfer_priority: float = Field(ge=0.0, le=1.0)
    reorder_priority: float = Field(ge=0.0, le=1.0)

class InventoryRecommendation(BaseModel):
    action_type: str
    target_item: str
    target_branch: Optional[str]
    source_branch: Optional[str]
    quantity: int
    reason: str
    evidence: str
    confidence: float
    business_impact: str
    expected_savings: float
    alternative_actions: List[str]

class InventoryAIResponse(BaseModel):
    agent: str = "InventoryAI"
    timestamp: str
    target_scope: str # E.g., "Network", "Branch-XYZ"
    scores: InventoryScores
    low_stock_items: List[str]
    dead_stock_items: List[str]
    expiring_soon_items: List[str]
    recommendations: List[InventoryRecommendation]
