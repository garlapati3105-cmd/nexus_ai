"""
Nexus AI — LangGraph Graphs
Compiles the main StateGraph with node transitions and conditional routing.
"""
from __future__ import annotations
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from app.ai.langgraph.state import GraphWorkflowState
from app.ai.langgraph.nodes import (
    sales_node,
    inventory_node,
    finance_node,
    regional_node,
    approval_node,
    invoice_node
)
from app.ai.langgraph.edges import (
    stock_available_condition,
    finance_routing_condition
)

def create_workflow_graph() -> StateGraph:
    """Coordinates compiling nodes and edges into an executable LangGraph topology."""
    workflow = StateGraph(GraphWorkflowState)
    
    # 1. Register executive nodes
    workflow.add_node("sales", sales_node)
    workflow.add_node("inventory", inventory_node)
    workflow.add_node("finance", finance_node)
    workflow.add_node("regional", regional_node)
    workflow.add_node("approval", approval_node)
    workflow.add_node("invoice", invoice_node)

    # 2. Wired transitions
    workflow.add_edge(START, "sales")
    workflow.add_edge("sales", "inventory")
    
    # Conditional stockout redirection
    workflow.add_conditional_edges(
        "inventory",
        stock_available_condition,
        {
            "yes_path": "finance",
            "no_path": "regional",
            "end_path": END
        }
    )
    
    # Regional routes to Finance calculation in Stockout NO path
    workflow.add_edge("regional", "finance")
    
    # Finance conditional path (routes to approval if transfer is active, otherwise invoice)
    workflow.add_conditional_edges(
        "finance",
        finance_routing_condition,
        {
            "approval_path": "approval",
            "invoice_path": "invoice"
        }
    )
    
    # Gating and complete steps
    workflow.add_edge("approval", "invoice")
    workflow.add_edge("invoice", END)
    
    # Compile with memory checkpointer
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)

# Pre-compiled instance
workflow_graph = create_workflow_graph()
