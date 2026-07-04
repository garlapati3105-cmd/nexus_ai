"""
Nexus AI — Decision Composer
Aggregates independent agent decisions (Sales, Inventory, Finance) into a single explainable verdict.
"""
from __future__ import annotations
from typing import Any, Dict, List
import datetime

class DecisionComposer:
    
    @staticmethod
    def compose(
        sales_resp: Dict[str, Any],
        inventory_resp: Dict[str, Any],
        finance_resp: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Regional AI merges Sales, Inventory, and Finance telemetry.
        Generates Explainability details: Reason, Evidence, Confidence, Business Impact, alternative options.
        """
        reasoning = ["Regional AI combined workspace metrics."]
        evidence = []
        confidence = 0.95
        
        status = sales_resp.get("validation_status", "APPROVED")
        recommendations = []
        net_financial_savings = 0.0
        risk_score = 0.05
        
        # 1. Parse Sales Status
        if status == "REJECTED_PRESCRIPTION":
            reasoning.append("Order rejected by Sales AI prescription restriction rules.")
            evidence.append("Unrestricted generic OTC paracetamol recommended.")
            recommendations.append({
                "action": "Offer Alternative OTC Generic",
                "reason": "Controlled medicine requires signed prescription."
            })
            confidence = 0.90
            
        elif status == "REDIRECT_TRANSFER":
            reasoning.append("Local stockout detected. Initializing inter-branch transfer optimization.")
            if finance_resp:
                cost_comp = finance_resp.get("cost_comparison", {})
                cheapest_path = cost_comp.get("cheapest_option", "TRANSFER")
                net_savings = cost_comp.get("estimated_savings", 0.0)
                net_financial_savings = net_savings
                
                # Check transfer details
                evidence.append(
                    f"Transfer total cost: ${cost_comp.get('branch_transfer_cost', 0.0):.2f} "
                    f"vs Supplier cost: ${cost_comp.get('supplier_purchase_cost', 0.0):.2f}."
                )
                recommendations.append({
                    "action": "Approve Branch-to-Branch Stock Transfer",
                    "cheapest_path": cheapest_path,
                    "estimated_savings": net_savings
                })
                confidence = cost_comp.get("confidence", 0.95)
            else:
                evidence.append("Local stockout detected; transfer suggested but costs uncalculated.")
                recommendations.append({"action": "Review Transfer Proposal"})
                
        elif status == "BACKORDER":
            reasoning.append("Network stock depleted completely.")
            evidence.append("Reorder priority score critical.")
            recommendations.append({"action": "Trigger Supplier Procurement"})
            confidence = 0.99
            
        else: # APPROVED local checkout
            reasoning.append("Approved local order validation.")
            evidence.append("Stock is available locally at current branch.")
            confidence = 0.98

        return {
            "agent": "RegionalAI_Composer",
            "verdict_status": status,
            "overall_confidence": confidence,
            "reasoning": reasoning,
            "evidence": evidence,
            "recommendations": recommendations,
            "overall_business_impact": {
                "category": "Inter-Branch Logistics" if status == "REDIRECT_TRANSFER" else "Retail Sale",
                "savings_realized": net_financial_savings,
                "workflow_flow_path": "Approval Required" if status == "REDIRECT_TRANSFER" else "Auto-Checkout",
                "risk_score": risk_score
            },
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

from typing import Optional
