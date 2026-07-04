"""
Nexus AI — Collaboration Integration Runner
Runs the workflow coordinator through both APPROVED and REDIRECT_TRANSFER paths.
"""
from __future__ import annotations
import asyncio
from uuid import uuid4
from app.ai.workflow.coordinator import WorkflowCoordinator
from app.ai.communication.layer import InMemoryMessageBus, AgentCommunicationLayer
from app.ai.agents.sales.sales_agent import SalesAIAgent
from app.ai.agents.inventory.inventory_agent import InventoryAIAgent
from app.ai.agents.finance.finance_agent import FinanceAIAgent
from app.ai.agents.regional.regional_agent import RegionalAIAgent
from app.ai.agents.models.core import AgentMetadata, AgentCapability
from app.ai.agents.interfaces.hooks import AgentMemoryHooks, AgentLoggingHooks, AgentMetricsTracker
from typing import Any, Dict

# Standard Mock implementations for required agent dependencies
class MockMemory(AgentMemoryHooks):
    async def load_short_term(self, context) -> dict: return {}
    async def load_long_term(self, context) -> dict: return {}
    async def commit_workflow_memory(self, uuid, data) -> None: pass

class MockLogger(AgentLoggingHooks):
    def log_execution_start(self, agent_id, request) -> None: pass
    def log_tool_usage(self, agent_id, tool_name, success) -> None: pass
    def log_execution_complete(self, agent_id, response, duration_ms) -> None: pass

class MockTracker(AgentMetricsTracker):
    def increment_execution(self, agent_id, success) -> None: pass
    def record_runtime(self, agent_id, ms) -> None: pass
    def record_confidence(self, agent_id, score) -> None: pass

async def run_scenario():
    # 1. Initialize message bus
    bus = InMemoryMessageBus()
    comms = AgentCommunicationLayer(bus)
    
    # Simple dummy capabilities
    caps = AgentCapability(readable_data=[], writable_data=[], allowed_tools=[], approval_level=0, maximum_scope="")
    
    # 2. Instantiate all agents with mocked hooks
    sales = SalesAIAgent(
        metadata=AgentMetadata(id=uuid4(), name="SalesAI", description="", version="1.0", capabilities=caps),
        memory=MockMemory(), logger=MockLogger(), metrics=MockTracker()
    )
    inventory = InventoryAIAgent(
        metadata=AgentMetadata(id=uuid4(), name="InventoryAI", description="", version="1.0", capabilities=caps),
        memory=MockMemory(), logger=MockLogger(), metrics=MockTracker()
    )
    finance = FinanceAIAgent(
        metadata=AgentMetadata(id=uuid4(), name="FinanceAI", description="", version="1.0", capabilities=caps),
        memory=MockMemory(), logger=MockLogger(), metrics=MockTracker()
    )
    regional = RegionalAIAgent(
        metadata=AgentMetadata(id=uuid4(), name="RegionalAI", description="", version="1.0", capabilities=caps),
        memory=MockMemory(), logger=MockLogger(), metrics=MockTracker()
    )
    
    coordinator = WorkflowCoordinator(comms, sales, inventory, finance, regional)
    
    # Scenario A: Local Stock availability
    order_a = {
        "order_id": "O-APPROVED",
        "branch_id": "BRANCH-1",
        "items": [{"medicine_id": "M-NORMAL", "quantity": 5}],
        "total_amount": 27.50
    }
    print("LOG: Triggering Scenario A (Local Stock exists)...")
    res_a = await coordinator.execute_checkout_workflow(order_a, has_prescription=True)
    print(f"Scenario A Final Status: {res_a.shared_state.order.status}")
    print(f"Scenario A Invoice Generated: {res_a.shared_state.invoice.generated} (Invoice ID: {res_a.shared_state.invoice.invoice_id})")
    
    # Scenario B: Local Stockout -> Inter-branch transfer redirect
    order_b = {
        "order_id": "O-TRANSFER",
        "branch_id": "BRANCH-1",
        "items": [{"medicine_id": "M-STOCKOUT", "quantity": 10}],
        "total_amount": 55.00
    }
    print("\nLOG: Triggering Scenario B (Local Stockout -> Inter-branch transfer optimization)...")
    res_b = await coordinator.execute_checkout_workflow(order_b, has_prescription=True)
    print(f"Scenario B Final Status: {res_b.shared_state.order.status} (Requires approval: {res_b.shared_state.approval.requires_approval})")
    print(f"Scenario B Transfer Recommended: Needed={res_b.shared_state.transfer.needed}, From={res_b.shared_state.transfer.from_branch} -> To={res_b.shared_state.transfer.to_branch}")
    print(f"Scenario B Savings Estimated: ${res_b.shared_state.transfer.estimated_freight_cost:.2f} freight cost recorded.")

if __name__ == "__main__":
    asyncio.run(run_scenario())
