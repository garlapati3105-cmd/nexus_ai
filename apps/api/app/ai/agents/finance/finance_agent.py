"""
Nexus AI — Finance AI Agent
Performs cost estimations, profit analysis, and reports financial KPIs.
"""
from __future__ import annotations
from typing import Any, Dict, List
import datetime

from app.ai.agents.base.agent import BaseAgent
from app.ai.agents.finance.models import FinanceAIResponse, FinanceScores, CostComparisonResult

class FinanceAIAgent(BaseAgent):
    """
    Finance AI concrete class extending BaseAgent.
    Performs cost comparisons between inter-branch transfers vs supplier purchases.
    Calculates branch profitability reports and details financial performance metrics.
    """
    
    async def select_tools(self, context: Dict[str, Any], goal: str) -> List[Dict[str, Any]]:
        """Maps incoming financial optimization queries to active tool boundaries."""
        tools = [
            {"name": "calculate_transfer_cost", "params": {"medicine_id": context.get("medicine_id")}},
            {"name": "get_dashboard_kpis", "params": {"branch_id": context.get("branch_id")}},
            {"name": "retrieve_medicine_information", "params": {"medicine_id": context.get("medicine_id")}}
        ]
        return tools

    async def execute_tools(self, tool_configs: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Runs designated tools via simulated execution bounds."""
        results = {}
        for tc in tool_configs:
            tool_name = tc["name"]
            med_id = tc["params"].get("medicine_id", "M-111")
            
            if tool_name == "calculate_transfer_cost":
                results[tool_name] = {"transfer_freight": 25.00}
            elif tool_name == "get_dashboard_kpis":
                results[tool_name] = {
                    "daily_rev": 1200.00,
                    "weekly_rev": 8400.00,
                    "monthly_rev": 36000.00,
                    "expenses": {"salary": 1500.00, "utilities": 300.00, "inventory_waste": 150.00}
                }
            elif tool_name == "retrieve_medicine_information":
                # Supplier price is $50.00 vs local cost
                results[tool_name] = {
                    "id": med_id,
                    "supplier_price": 45.00,
                    "local_cost": 20.00
                }
        return results

    async def generate_response(self, context: Dict[str, Any], tool_results: Dict[str, Any]) -> tuple[str, float, List[str], Dict[str, Any]]:
        """
        Calculates deterministic financial logic:
        - Total Supplier cost = quantity * supplier price
        - Total Transfer cost = quantity * local cost + transfer freight
        - Proposes cheaper option.
        """
        params = context.get("parameters", {})
        medicine_id = params.get("medicine_id", "M-111")
        quantity = params.get("quantity", 10)
        
        reasoning = ["Initiated financial optimization check."]
        confidence = 0.97
        
        # Pull tool metrics
        med_info = tool_results.get("retrieve_medicine_information", {})
        supplier_item_price = med_info.get("supplier_price", 45.00)
        local_cost = med_info.get("local_cost", 20.00)
        
        freight_cost = tool_results.get("calculate_transfer_cost", {}).get("transfer_freight", 25.00)
        
        # Calculate comparison
        total_supplier_cost = quantity * supplier_item_price
        total_transfer_cost = (quantity * local_cost) + freight_cost
        
        cheapest = "TRANSFER" if total_transfer_cost < total_supplier_cost else "SUPPLIER"
        savings = abs(total_supplier_cost - total_transfer_cost)
        roi_percentage = (savings / max(total_transfer_cost, 1.0)) * 100.0
        
        reasoning.append(f"supplier cost: ${total_supplier_cost:.2f} vs transfer cost: ${total_transfer_cost:.2f}.")
        reasoning.append(f"Recommended channel: {cheapest}")
        
        comparison = CostComparisonResult(
            item_id=medicine_id,
            supplier_purchase_cost=total_supplier_cost,
            branch_transfer_cost=total_transfer_cost,
            cheapest_option=cheapest,
            estimated_savings=savings,
            roi_percentage=roi_percentage,
            reason=f"Inter-branch transfer is cheaper due to high margin retention.",
            evidence=f"Local cost: ${local_cost}/unit. Supplier cost: ${supplier_item_price}/unit. Freight: ${freight_cost}.",
            confidence=confidence,
            expected_savings=savings,
            alternative_options=["Supplier procurement with bulk discount."]
        )
        
        dashboard_metrics = tool_results.get("get_dashboard_kpis", {})
        daily_revenue = dashboard_metrics.get("daily_rev", 1200.00)
        weekly_revenue = dashboard_metrics.get("weekly_rev", 8400.00)
        monthly_revenue = dashboard_metrics.get("monthly_rev", 36000.00)
        expenses_dict = dashboard_metrics.get("expenses", {})
        
        total_expenses = sum(expenses_dict.values())
        net_profitability = daily_revenue - (total_expenses / 30.0) # Daily proportional cost estimation
        
        structured = FinanceAIResponse(
            agent="FinanceAI",
            timestamp=datetime.datetime.utcnow().isoformat(),
            scores=FinanceScores(
                financial_health=0.85,
                branch_profitability=0.90 if net_profitability > 0 else 0.40,
                transfer_cost_score=0.92,
                savings_score=0.88,
                roi_score=0.95,
                recommendation_confidence=confidence
            ),
            cost_comparison=comparison,
            daily_revenue=daily_revenue,
            weekly_revenue=weekly_revenue,
            monthly_revenue=monthly_revenue,
            branch_profitability={"BRANCH-1": net_profitability},
            expense_breakdown=expenses_dict,
            transfer_savings_total=savings if cheapest == "TRANSFER" else 0.00,
            executive_financial_brief=(
                f"Financial standing is strong. Branch productivity matches baseline. "
                f"Recommending {cheapest} for medicine {medicine_id} with estimated savings of ${savings:.2f}."
            )
        )
        
        decision = f"Procurement recommended: {cheapest}"
        return decision, confidence, reasoning, structured.model_dump()
