"""
Nexus AI — Finance Service
Calculates transfer costs and financial metrics.
AI reasoning is mocked; calculations use real data.
"""
from __future__ import annotations
from app.core.logging import get_logger

logger = get_logger("service.finance")

# Transfer cost constants (these would eventually be AI-driven)
BASE_TRANSFER_COST = 50.0  # Base INR per transfer
PER_UNIT_COST = 2.5        # INR per unit transferred
URGENCY_MULTIPLIER = 1.5   # Multiplier for urgent transfers


class FinanceService:
    def calculate_transfer_cost(
        self,
        from_branch_id: str,
        to_branch_id: str,
        quantity: int,
        urgent: bool = False,
    ) -> dict:
        """
        Calculate the estimated cost of an inter-branch transfer.
        Returns a cost breakdown dict.
        """
        base = BASE_TRANSFER_COST
        unit_cost = PER_UNIT_COST * quantity
        subtotal = base + unit_cost

        if urgent:
            subtotal *= URGENCY_MULTIPLIER

        gst = subtotal * 0.18
        total = subtotal + gst

        result = {
            "base_cost": round(base, 2),
            "unit_cost": round(unit_cost, 2),
            "subtotal": round(subtotal, 2),
            "gst": round(gst, 2),
            "total": round(total, 2),
            "currency": "INR",
            "urgent": urgent,
            "ai_recommendation": "Transfer is cost-effective based on margin analysis.",
        }

        logger.info(
            f"Transfer cost calculated: {from_branch_id} → {to_branch_id}, "
            f"qty={quantity}, total=₹{result['total']}"
        )
        return result
