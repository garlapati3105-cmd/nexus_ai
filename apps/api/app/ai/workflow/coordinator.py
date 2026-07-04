"""
Nexus AI — Workflow Coordinator
Deterministic orchestration engine running the standard checkout pipeline.
"""
from __future__ import annotations
from typing import Any, Dict, List
from uuid import UUID, uuid4
import time

from app.ai.workflow.context import WorkflowContext, SharedBusinessState, CollaborationMetrics
from app.ai.communication.layer import AgentCommunicationLayer
from app.ai.agents.sales.sales_agent import SalesAIAgent
from app.ai.agents.inventory.inventory_agent import InventoryAIAgent
from app.ai.agents.finance.finance_agent import FinanceAIAgent
from app.ai.agents.regional.regional_agent import RegionalAIAgent
from app.ai.agents.models.core import AgentRequest, AgentContext

class WorkflowCoordinator:
    """
    Coordinates execution transitions. Directs pipeline steps from Sales check 
    through stock checks, pricing, composite decisions, approvals, and logs.
    """
    
    def __init__(
        self,
        comms: AgentCommunicationLayer,
        sales_agent: SalesAIAgent,
        inventory_agent: InventoryAIAgent,
        finance_agent: FinanceAIAgent,
        regional_agent: RegionalAIAgent
    ):
        self.comms = comms
        self.sales = sales_agent
        self.inventory = inventory_agent
        self.finance = finance_agent
        self.regional = regional_agent

    async def execute_checkout_workflow(
        self, 
        order_details: Dict[str, Any], 
        has_prescription: bool = False
    ) -> WorkflowContext:
        """Runs the complete collaborative operational cycle."""
        start_time = time.time()
        workflow_id = uuid4()
        session_id = f"session-{uuid4()}"
        
        # Initialize context state
        context = WorkflowContext(
            workflow_id=workflow_id,
            session_id=session_id
        )
        state = context.shared_state
        metrics = context.metrics
        
        # Populate initial Order state
        state.order.order_id = order_details.get("order_id", "O-99")
        state.order.items = order_details.get("items", [])
        state.order.total_amount = order_details.get("total_amount", 55.00)
        state.order.status = "VALIDATING"
        state.progress.append("Workflow Initialized")
        
        med_id = order_details["items"][0]["medicine_id"] if order_details.get("items") else "M-111"
        qty = order_details["items"][0]["quantity"] if order_details.get("items") else 5
        branch_id = order_details.get("branch_id", "BRANCH-1")
        
        # 1. Dispatch to Sales AI
        time_a = time.time()
        agent_context = AgentContext(
            user_id=None,
            role="System",
            organization_id=uuid4(),
            branch_id=UUID(int=1) if branch_id == "BRANCH-1" else uuid4(),
            workflow_id=workflow_id,
            session_id=session_id,
            business_context={}
        )
        sales_req = AgentRequest(
            task_id=uuid4(),
            goal=f"Verify order validation for item {med_id}",
            context=agent_context,
            parameters={
                "medicine_id": med_id,
                "has_prescription": has_prescription,
                "order_id": state.order.order_id
            }
        )
        
        state.progress.append("Sales AI: Validating order rules")
        sales_resp = await self.sales.execute(sales_req)
        metrics.agent_latencies["SalesAI"] = (time.time() - time_a) * 1000
        metrics.agent_communication_count += 1
        
        sales_out = sales_resp.structured_output
        status = sales_out.get("validation_status", "APPROVED")
        
        # 2. Inventory check
        time_b = time.time()
        state.progress.append("Inventory AI: Evaluating stock ratios")
        inv_req = AgentRequest(
            task_id=uuid4(),
            goal="Inspect stock parameters.",
            context=agent_context,
            parameters={"medicine_id": med_id}
        )
        inv_resp = await self.inventory.execute(inv_req)
        metrics.agent_latencies["InventoryAI"] = (time.time() - time_b) * 1000
        metrics.agent_communication_count += 1
        
        # Write state variables
        state.inventory.checked = True
        state.inventory.is_available = (status == "APPROVED")
        
        finance_out = None
        
        # 3. Handle stockout redirections
        if status == "REDIRECT_TRANSFER":
            state.progress.append("Regional AI: Coordinating transfer routes")
            # Regional schedules Finance evaluation
            time_c = time.time()
            state.progress.append("Finance AI: Determining transfer margins")
            fin_req = AgentRequest(
                task_id=uuid4(),
                goal="Assess freight vs purchase prices.",
                context=agent_context,
                parameters={"medicine_id": med_id, "quantity": qty}
            )
            fin_resp = await self.finance.execute(fin_req)
            metrics.agent_latencies["FinanceAI"] = (time.time() - time_c) * 1000
            metrics.agent_communication_count += 1
            
            finance_out = fin_resp.structured_output
            cost_comp = finance_out.get("cost_comparison", {})
            
            state.transfer.needed = True
            state.transfer.medicine_id = med_id
            state.transfer.quantity = qty
            state.transfer.estimated_freight_cost = cost_comp.get("branch_transfer_cost", 25.00)
            state.transfer.from_branch = "BRANCH-2"
            state.transfer.to_branch = branch_id

        # 4. Regional AI: Merges and writes recommendation
        time_r = time.time()
        state.progress.append("Regional AI: Composing composite decision")
        
        # Run composite logic
        from app.ai.workflow.composer import DecisionComposer
        composite_verdict = DecisionComposer.compose(sales_out, inv_resp.structured_output, finance_out)
        metrics.agent_latencies["RegionalAI"] = (time.time() - time_r) * 1000
        
        # Update Approval & Invoice details base rules
        if status == "REDIRECT_TRANSFER":
            state.approval.requires_approval = True
            state.approval.req_level = 1
            state.order.status = "WAITING_APPROVAL"
        elif status == "REJECTED_PRESCRIPTION":
            state.order.status = "CANCELLED"
        else:
            # Complete logic
            state.order.status = "COMPLETED"
            state.invoice.generated = True
            state.invoice.invoice_id = f"INV-{uuid4().hex[:6].upper()}"
            state.invoice.final_billing_amount = state.order.total_amount
            
            state.notifications.sent = True
            state.notifications.recipient = "Customer"
            state.notifications.channels = ["SMS"]

        state.progress.append("Workflow Execution Terminated")
        metrics.workflow_duration_ms = (time.time() - start_time) * 1000
        
        # Broadcast context update using standard Comm Layer
        await self.comms.broadcast_context_update(workflow_id, context.model_dump())
        return context
