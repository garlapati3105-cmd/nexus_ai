"""
Nexus AI — Finance AI Models
Strict schemas for transfer cost estimation, profitability analysis, and KPI values.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class FinanceScores(BaseModel):
    financial_health: float = Field(ge=0.0, le=1.0)
    branch_profitability: float = Field(ge=0.0, le=1.0)
    transfer_cost_score: float = Field(ge=0.0, le=1.0)
    savings_score: float = Field(ge=0.0, le=1.0)
    roi_score: float = Field(ge=0.0, le=1.0)
    recommendation_confidence: float = Field(ge=0.0, le=1.0)

class CostComparisonResult(BaseModel):
    item_id: str
    supplier_purchase_cost: float
    branch_transfer_cost: float
    cheapest_option: str # "SUPPLIER" or "TRANSFER"
    estimated_savings: float
    roi_percentage: float
    reason: str
    evidence: str
    confidence: float
    expected_savings: float
    alternative_options: List[str]

class FinanceAIResponse(BaseModel):
    agent: str = "FinanceAI"
    timestamp: str
    scores: FinanceScores
    cost_comparison: Optional[CostComparisonResult] = None
    daily_revenue: float
    weekly_revenue: float
    monthly_revenue: float
    branch_profitability: Dict[str, float]
    expense_breakdown: Dict[str, float]
    transfer_savings_total: float
    executive_financial_brief: str
