"""
Nexus AI — Sales AI Agent
Validates orders, checks rules (prescriptions/stock), recommends generic alternatives or transfers.
"""
from __future__ import annotations
from typing import Any, Dict, List
import datetime

from app.ai.agents.base.agent import BaseAgent
from app.ai.agents.sales.models import SalesAIResponse, SalesScores, AlternativeMatch, AvailabilityDetails

class SalesAIAgent(BaseAgent):
    """
    Sales AI concrete agent class extending the core BaseAgent template structure.
    Validates medicines, checks local/network availability, handles prescription gates, 
    and determines alternative substitutions deterministically.
    """
    
    async def select_tools(self, context: Dict[str, Any], goal: str) -> List[Dict[str, Any]]:
        """Identify corresponding tool invocations based on task goals."""
        tools = [
            {"name": "check_local_inventory", "params": {"branch_id": context.get("branch_id"), "medicine_id": context.get("medicine_id")}},
            {"name": "check_network_inventory", "params": {"medicine_id": context.get("medicine_id")}},
            {"name": "retrieve_medicine_information", "params": {"medicine_id": context.get("medicine_id")}}
        ]
        return tools

    async def execute_tools(self, tool_configs: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Simulates tools returning data from catalog lookup and inventory queries."""
        results = {}
        for tc in tool_configs:
            tool_name = tc["name"]
            med_id = tc["params"].get("medicine_id", "M-111")
            
            if tool_name == "check_local_inventory":
                # Simulated local stock check. 0 means local stockout for custom logic checks
                stock = 0 if med_id == "M-STOCKOUT" else 15
                results[tool_name] = {"available": stock > 0, "quantity": stock}
                
            elif tool_name == "check_network_inventory":
                results[tool_name] = {
                    "branches": [
                        {"branch_id": "BRANCH-2", "stock": 50, "distance_km": 4.5, "transfer_cost": 15.00}
                    ]
                }
                
            elif tool_name == "retrieve_medicine_information":
                # Let's say M-RESTRICTED requires a prescription
                requires_rx = (med_id == "M-RESTRICTED")
                results[tool_name] = {
                    "id": med_id,
                    "name": "Panadol" if med_id != "M-RESTRICTED" else "Amoxicillin",
                    "requires_prescription": requires_rx,
                    "generic_name": "Paracetamol" if med_id != "M-RESTRICTED" else "Amoxicillin Trihydrate",
                    "price": 5.50
                }
        return results

    async def generate_response(self, context: Dict[str, Any], tool_results: Dict[str, Any]) -> tuple[str, float, List[str], Dict[str, Any]]:
        """
        Executes sales validation rules:
        - Check local stock. If not found, check network.
        - Validate prescription limits.
        - Recommend generic alternatives.
        """
        params = context.get("parameters", {})
        medicine_id = params.get("medicine_id", "M-111")
        has_prescription = params.get("has_prescription", False)
        
        reasoning = ["Initiated checkout validation pipeline."]
        validation_status = "APPROVED"
        alternatives = []
        availability = []
        escalations = []
        confidence = 0.98
        
        # 1. Fetch medicine properties
        med_info = tool_results.get("retrieve_medicine_information", {})
        requires_rx = med_info.get("requires_prescription", False)
        
        # Rule check: Prescription-only restriction
        if requires_rx and not has_prescription:
            validation_status = "REJECTED_PRESCRIPTION"
            reasoning.append("Blocked sale: Medicine requires prescription, but none was provided.")
            alternatives.append(
                AlternativeMatch(
                    original_medicine_id=medicine_id,
                    recommended_medicine_id="M-OTC-GENERIC",
                    generic_name="OTC Paracetamol Blend",
                    price_difference=-1.20,
                    reason="Target medicine is restricted. Recommend over-the-counter equivalent.",
                    evidence="Amoxicillin requires doctor signature. OTC Paracetamol is unrestricted.",
                    confidence=0.90,
                    expected_outcome="Patient receives symptom relief safely without delays."
                )
            )
            availability.append(
                AvailabilityDetails(
                    medicine_id=medicine_id,
                    available=False,
                    local_stock=0
                )
            )
        else:
            # 2. Inventory check
            local_stock = tool_results.get("check_local_inventory", {}).get("quantity", 0)
            if local_stock > 0:
                reasoning.append(f"Confirmed local stock availability ({local_stock} units).")
                availability.append(
                    AvailabilityDetails(
                        medicine_id=medicine_id,
                        available=True,
                        local_stock=local_stock
                    )
                )
            else:
                # Stockout path
                reasoning.append("Local stockout detected. Checking network branches...")
                network_branches = tool_results.get("check_network_inventory", {}).get("branches", [])
                
                if network_branches:
                    nearest = network_branches[0]
                    validation_status = "REDIRECT_TRANSFER"
                    reasoning.append(f"Found branch {nearest['branch_id']} with {nearest['stock']} units.")
                    availability.append(
                        AvailabilityDetails(
                            medicine_id=medicine_id,
                            available=False,
                            local_stock=0,
                            nearest_branch_id=nearest["branch_id"],
                            nearest_branch_stock=nearest["stock"],
                            transfer_recommended=True
                        )
                    )
                else:
                    validation_status = "BACKORDER"
                    reasoning.append("Medicine totally out of stock network-wide.")
                    availability.append(
                        AvailabilityDetails(
                            medicine_id=medicine_id,
                            available=False,
                            local_stock=0,
                            transfer_recommended=False
                        )
                    )

        # Map Response
        structured = SalesAIResponse(
            agent="SalesAI",
            timestamp=datetime.datetime.utcnow().isoformat(),
            order_id=params.get("order_id"),
            validation_status=validation_status,
            scores=SalesScores(
                order_validation=1.0 if validation_status == "APPROVED" else 0.0,
                medicine_availability=1.0 if any(a.available for a in availability) else 0.0,
                customer_satisfaction=0.95 if validation_status == "APPROVED" else 0.60,
                sales_efficiency=0.98,
                recommendation_confidence=confidence
            ),
            availability=availability,
            alternatives=alternatives,
            business_impact={
                "margin_recovered": 5.50 if validation_status == "APPROVED" else 0.00,
                "workflow_action": "Billing" if validation_status == "APPROVED" else "Review"
            },
            customer_notification={
                "send_sms": True,
                "message": (
                    "Your order is verified and ready for payment."
                    if validation_status == "APPROVED"
                    else "Order requires a valid prescription to proceed."
                )
            }
        )
        
        decision = f"Order status resolved to {validation_status}"
        return decision, confidence, reasoning, structured.model_dump()
