"""
Nexus AI — LangGraph Integration Runner
Executes compiled LangGraph StateGraph through Yes and No conditional branches.
"""
from __future__ import annotations
import asyncio
from uuid import uuid4
from app.ai.langgraph.graphs import workflow_graph

async def run_scenarios():
    config = {"configurable": {"thread_id": "thread-1"}}
    
    # 1. Yes Path (Local Checkout Stock Available)
    state_yes = {
        "medicine_id": "M-NORMAL",
        "quantity": 5,
        "branch_id": "BRANCH-1",
        "has_prescription": True,
        "progress": [],
        "session_id": "session-yes",
        "workflow_id": str(uuid4()),
        "errors": [],
        "agent_latencies": {},
        "sales_outputs": {},
        "inventory_outputs": {},
        "finance_outputs": {},
        "composite_decision": {},
        "order": {"order_id": "O-APPROVED", "total_amount": 27.50},
        "inventory": {},
        "transfer": {},
        "approval": {},
        "invoice": {},
        "notifications": {}
    }
    
    print("LOG: Triggering LangGraph Scenario A (Local Stock Available/YES Path)...")
    res_yes = await workflow_graph.ainvoke(state_yes, config)
    print(f"Scenario A Final Status: {res_yes['order']['status']}")
    print(f"Scenario A Progress Traces: {res_yes['progress']}")
    print(f"Scenario A Latencies: {res_yes['agent_latencies']}")
    
    # 2. No Path (Local Stockout -> Inter-branch transfer)
    state_no = {
        "medicine_id": "M-STOCKOUT",
        "quantity": 10,
        "branch_id": "BRANCH-1",
        "has_prescription": True,
        "progress": [],
        "session_id": "session-no",
        "workflow_id": str(uuid4()),
        "errors": [],
        "agent_latencies": {},
        "sales_outputs": {},
        "inventory_outputs": {},
        "finance_outputs": {},
        "composite_decision": {},
        "order": {"order_id": "O-TRANSFER", "total_amount": 55.00},
        "inventory": {},
        "transfer": {},
        "approval": {},
        "invoice": {},
        "notifications": {}
    }
    
    print("\nLOG: Triggering LangGraph Scenario B (Stockout NO Path -> Transfer Redirect)...")
    res_no = await workflow_graph.ainvoke(state_no, {"configurable": {"thread_id": "thread-2"}})
    print(f"Scenario B Final Status: {res_no['order']['status']}")
    print(f"Scenario B Progress Traces: {res_no['progress']}")
    print(f"Scenario B Transfer: {res_no['transfer']}")
    print(f"Scenario B Composite Recommendation: {res_no['composite_decision'].get('verdict_status')}")

if __name__ == "__main__":
    asyncio.run(run_scenarios())
