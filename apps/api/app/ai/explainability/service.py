"""
Nexus AI — Explainability Service
Implements calculators for confidence, impact parameters, reasoning formats, and timelines.
"""
from __future__ import annotations
import datetime
from uuid import uuid4
from typing import Any, Dict, List, Optional

from app.ai.explainability.models import ExplanationProfile, DecisionRecord, ExplainabilityTimeline

class ConfidenceCalculator:
    """Computes trust metrics and normalize confidence values."""
    @staticmethod
    def calculate(parameters: Dict[str, Any]) -> float:
        # Simple weighted confidence based on input factors
        base = 0.85
        if parameters.get("stock_ratio", 1.0) < 0.5:
            base -= 0.15 # lower confidence if stock ratio is low
        if parameters.get("has_prescription", False) is False and parameters.get("requires_prescription", False):
            base -= 0.30 # major confidence drop without prescription
        return max(0.10, min(1.0, base))

class BusinessImpactCalculator:
    """Calculates financial savings, ROI margins, and risk matrices."""
    @staticmethod
    def calculate(parameters: Dict[str, Any]) -> Dict[str, Any]:
        qty = parameters.get("quantity", 1)
        unit_price = parameters.get("unit_price", 10.00)
        freight = parameters.get("estimated_freight_cost", 0.0)
        
        procure_price = parameters.get("procurement_price", 7.50)
        procure_total = qty * procure_price
        
        local_total = qty * unit_price
        
        # Savings = standard local checkout cost vs optimization / transfer offsets
        savings = max(0.00, local_total - (procure_total + freight))
        
        risk = "LOW"
        if freight > local_total * 0.5:
            risk = "HIGH"
        elif freight > local_total * 0.2:
            risk = "MEDIUM"
            
        return {
            "estimated_savings": savings,
            "risk_level": risk,
            "expected_outcome": f"Delivery completed with optimized local vs branch transfer pricing margins."
        }

class AlternativeActionGenerator:
    """Generates standard alternative execution paths in the workflow."""
    @staticmethod
    def generate(parameters: Dict[str, Any]) -> List[str]:
        alts = []
        if parameters.get("is_stockout", False):
            alts.append("Procure from external wholesale pharmaceutical supplier.")
            alts.append("Substitute with equivalent generic molecular formulation.")
        else:
            alts.append("Hold order for customer pickup at a scheduled later date.")
        return alts

class ExplainabilityService:
    """Central engine collecting evidences, calculating impacts, and recording timelines."""
    
    def __init__(self):
        self._timelines: Dict[str, List[DecisionRecord]] = {}

    def log_decision(
        self,
        workflow_id: str,
        agent_name: str,
        action_taken: str,
        parameters: Dict[str, Any],
        reasoning: str,
        evidence: List[str],
        knowledge_sources: List[str],
        state_mutations: Optional[Dict[str, Any]] = None
    ) -> DecisionRecord:
        """Assembles explanation profiles and saves decision records to chronological timelines."""
        # Run calculators
        confidence = ConfidenceCalculator.calculate(parameters)
        impact = BusinessImpactCalculator.calculate(parameters)
        alternatives = AlternativeActionGenerator.generate(parameters)
        
        timestamp = datetime.datetime.utcnow().isoformat()
        
        profile = ExplanationProfile(
            reasoning=reasoning,
            evidence_used=evidence,
            knowledge_sources=knowledge_sources,
            confidence_score=confidence,
            business_impact=f"Estimated savings: ${impact['estimated_savings']:.2f}. Risk Profile: {impact['risk_level']}.",
            alternative_recommendations=alternatives,
            estimated_savings=impact["estimated_savings"],
            expected_outcome=impact["expected_outcome"],
            risk_level=impact["risk_level"],
            timestamp=timestamp,
            responsible_agent=agent_name,
            workflow_id=workflow_id
        )
        
        record = DecisionRecord(
            decision_id=f"dec-{uuid4().hex[:8].upper()}",
            workflow_id=workflow_id,
            agent_name=agent_name,
            action_taken=action_taken,
            explanation=profile,
            state_mutations=state_mutations or {},
            timestamp=timestamp
        )
        
        if workflow_id not in self._timelines:
            self._timelines[workflow_id] = []
        self._timelines[workflow_id].append(record)
        return record

    def get_timeline(self, workflow_id: str) -> ExplainabilityTimeline:
        """Retrieves history trace of all actions execution records for a workflow ID."""
        records = self._timelines.get(workflow_id, [])
        return ExplainabilityTimeline(
            workflow_id=workflow_id,
            history=sorted(records, key=lambda x: x.timestamp),
            duration_ms=0.0
        )
