"""
Nexus AI — LangGraph Edges & Conditions
Defines routing predicates for checking stock availability and approval states.
"""
from __future__ import annotations
from app.ai.langgraph.state import GraphWorkflowState

def stock_available_condition(state: GraphWorkflowState) -> str:
    """
    Evaluates whether the order checkout path can execute locally or
    requires inter-branch transfer redirection.
    """
    sales_outputs = state.get("sales_outputs", {})
    status = sales_outputs.get("validation_status", "APPROVED")
    
    if status == "APPROVED":
        return "yes_path"
    elif status == "REDIRECT_TRANSFER":
        return "no_path"
    else:  # REJECTED_PRESCRIPTION, BACKORDER, etc
        return "end_path"

def finance_routing_condition(state: GraphWorkflowState) -> str:
    """
    Routes after finance node execution depending on whether a stock
    transfer occurred or if we directly execute localized checkout billing.
    """
    transfer = state.get("transfer", {})
    if transfer.get("needed", False):
        return "approval_path"
    return "invoice_path"
