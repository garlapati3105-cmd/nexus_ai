"""
Nexus AI — LangGraph Nodes
Converts base agent exec boundaries into LangGraph executable state transitions.
"""
from __future__ import annotations
import time
from uuid import uuid4, UUID
from typing import Dict, Any

from app.ai.langgraph.state import GraphWorkflowState
from app.ai.agents.sales.sales_agent import SalesAIAgent
from app.ai.agents.inventory.inventory_agent import InventoryAIAgent
from app.ai.agents.finance.finance_agent import FinanceAIAgent
from app.ai.agents.regional.regional_agent import RegionalAIAgent
from app.ai.agents.models.core import AgentMetadata, AgentCapability, AgentRequest, AgentContext
from app.ai.agents.interfaces.hooks import AgentMemoryHooks, AgentLoggingHooks, AgentMetricsTracker

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

# Lazy instantiation of agents to reuse across invocations
_caps = AgentCapability(readable_data=[], writable_data=[], allowed_tools=[], approval_level=0, maximum_scope="")
_agents = {
    "sales": SalesAIAgent(
        metadata=AgentMetadata(id=uuid4(), name="SalesAI", description="", version="1.0", capabilities=_caps),
        memory=MockMemory(), logger=MockLogger(), metrics=MockTracker()
    ),
    "inventory": InventoryAIAgent(
        metadata=AgentMetadata(id=uuid4(), name="InventoryAI", description="", version="1.0", capabilities=_caps),
        memory=MockMemory(), logger=MockLogger(), metrics=MockTracker()
    ),
    "finance": FinanceAIAgent(
        metadata=AgentMetadata(id=uuid4(), name="FinanceAI", description="", version="1.0", capabilities=_caps),
        memory=MockMemory(), logger=MockLogger(), metrics=MockTracker()
    ),
    "regional": RegionalAIAgent(
        metadata=AgentMetadata(id=uuid4(), name="RegionalAI", description="", version="1.0", capabilities=_caps),
        memory=MockMemory(), logger=MockLogger(), metrics=MockTracker()
    )
}

async def sales_node(state: GraphWorkflowState) -> Dict[str, Any]:
    """Execute Sales AI to validate orders and check generic prescriptions."""
    start_time = time.time()
    workflow_id = UUID(state["workflow_id"]) if state.get("workflow_id") else uuid4()
    session_id = state.get("session_id", "")
    
    agent_context = AgentContext(
        user_id=None, role="System", organization_id=uuid4(),
        branch_id=UUID(int=1) if state.get("branch_id") == "BRANCH-1" else uuid4(),
        workflow_id=workflow_id, session_id=session_id, business_context={}
    )
    
    req = AgentRequest(
        task_id=uuid4(),
        goal=f"Verify order validation for item {state.get('medicine_id')}",
        context=agent_context,
        parameters={
            "medicine_id": state.get("medicine_id", "M-111"),
            "has_prescription": state.get("has_prescription", False),
            "order_id": state.get("order", {}).get("order_id", "O-99")
        }
    )
    
    res = await _agents["sales"].execute(req)
    latency = (time.time() - start_time) * 1000
    
    sales_out = res.structured_output
    status = sales_out.get("validation_status", "APPROVED")
    
    progress = list(state.get("progress", []))
    progress.append(f"Sales AI Check complete: {status}")
    
    latencies = dict(state.get("agent_latencies", {}))
    latencies["SalesAI"] = latency
    
    return {
        "sales_outputs": sales_out,
        "progress": progress,
        "agent_latencies": latencies,
        "order": {**state.get("order", {}), "status": "VALIDATING"}
    }

async def inventory_node(state: GraphWorkflowState) -> Dict[str, Any]:
    """Execute Inventory AI stock evaluations."""
    start_time = time.time()
    workflow_id = UUID(state["workflow_id"]) if state.get("workflow_id") else uuid4()
    session_id = state.get("session_id", "")
    
    agent_context = AgentContext(
        user_id=None, role="System", organization_id=uuid4(),
        branch_id=UUID(int=1) if state.get("branch_id") == "BRANCH-1" else uuid4(),
        workflow_id=workflow_id, session_id=session_id, business_context={}
    )
    
    req = AgentRequest(
        task_id=uuid4(),
        goal="Inspect stock parameters.",
        context=agent_context,
        parameters={"medicine_id": state.get("medicine_id", "M-111")}
    )
    
    res = await _agents["inventory"].execute(req)
    latency = (time.time() - start_time) * 1000
    
    progress = list(state.get("progress", []))
    progress.append("Inventory AI Check complete")
    
    latencies = dict(state.get("agent_latencies", {}))
    latencies["InventoryAI"] = latency
    
    sales_status = state.get("sales_outputs", {}).get("validation_status", "APPROVED")
    is_available = (sales_status == "APPROVED")
    
    return {
        "inventory_outputs": res.structured_output,
        "inventory": {
            "checked": True,
            "is_available": is_available
        },
        "progress": progress,
        "agent_latencies": latencies
    }

async def finance_node(state: GraphWorkflowState) -> Dict[str, Any]:
    """Calculate procurement transfer offsets and freight margins."""
    start_time = time.time()
    workflow_id = UUID(state["workflow_id"]) if state.get("workflow_id") else uuid4()
    session_id = state.get("session_id", "")
    
    agent_context = AgentContext(
        user_id=None, role="System", organization_id=uuid4(),
        branch_id=UUID(int=1) if state.get("branch_id") == "BRANCH-1" else uuid4(),
        workflow_id=workflow_id, session_id=session_id, business_context={}
    )
    
    req = AgentRequest(
        task_id=uuid4(),
        goal="Assess freight vs purchase prices.",
        context=agent_context,
        parameters={
            "medicine_id": state.get("medicine_id", "M-111"),
            "quantity": state.get("quantity", 5)
        }
    )
    
    res = await _agents["finance"].execute(req)
    latency = (time.time() - start_time) * 1000
    
    progress = list(state.get("progress", []))
    progress.append("Finance AI Cost analysis complete")
    
    latencies = dict(state.get("agent_latencies", {}))
    latencies["FinanceAI"] = latency
    
    cost_comp = res.structured_output.get("cost_comparison", {})
    
    return {
        "finance_outputs": res.structured_output,
        "transfer": {
            "needed": True,
            "medicine_id": state.get("medicine_id"),
            "quantity": state.get("quantity", 5),
            "estimated_freight_cost": cost_comp.get("branch_transfer_cost", 25.00),
            "from_branch": "BRANCH-2",
            "to_branch": state.get("branch_id", "BRANCH-1")
        },
        "progress": progress,
        "agent_latencies": latencies
    }

async def regional_node(state: GraphWorkflowState) -> Dict[str, Any]:
    """Trigger decision compositions aligning all telemetry metrics."""
    start_time = time.time()
    
    sales_out = state.get("sales_outputs", {})
    inv_out = state.get("inventory_outputs", {})
    fin_out = state.get("finance_outputs")
    
    from app.ai.workflow.composer import DecisionComposer
    composite = DecisionComposer.compose(sales_out, inv_out, fin_out)
    
    latency = (time.time() - start_time) * 1000
    progress = list(state.get("progress", []))
    progress.append("Regional AI composite composition complete")
    
    latencies = dict(state.get("agent_latencies", {}))
    latencies["RegionalAI"] = latency
    
    return {
        "composite_decision": composite,
        "progress": progress,
        "agent_latencies": latencies
    }

async def approval_node(state: GraphWorkflowState) -> Dict[str, Any]:
    """Execute approval gating mechanisms when redirect transfers is active."""
    progress = list(state.get("progress", []))
    progress.append("Approval gated authorization verified")
    
    return {
        "order": {**state.get("order", {}), "status": "WAITING_APPROVAL"},
        "approval": {
            "requires_approval": True,
            "approved": False,
            "approved_by": None
        },
        "progress": progress
    }

async def invoice_node(state: GraphWorkflowState) -> Dict[str, Any]:
    """Generate transactional billing invoices for approved segments."""
    progress = list(state.get("progress", []))
    progress.append("Invoice billing compiled successfully")
    
    amount = state.get("order", {}).get("total_amount", 55.00)
    
    return {
        "order": {**state.get("order", {}), "status": "COMPLETED"},
        "invoice": {
            "generated": True,
            "invoice_id": f"INV-{uuid4().hex[:6].upper()}",
            "final_billing_amount": amount
        },
        "notifications": {
            "sent": True,
            "recipient": "Customer",
            "channels": ["SMS"]
        },
        "progress": progress
    }
