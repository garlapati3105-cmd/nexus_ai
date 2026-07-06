"""
Nexus AI — Workflow Service (Central Orchestrator)
Coordinates the full medicine purchase workflow across all domain services.
All operations now hit the real Supabase PostgreSQL database.

Workflow:
1. Validate order (Sales AI — mocked)
2. Check local inventory
3a. IF stock available → Reserve → Create Order → Invoice → Analytics → Notify
3b. IF stock unavailable → Network scan → Transfer proposal → Approval → Notify
"""
from __future__ import annotations
import uuid as uuid_mod
from app.services.order_service import OrderService
from app.services.inventory_service import InventoryService
from app.services.transfer_service import TransferService
from app.services.finance_service import FinanceService
from app.services.approval_service import ApprovalService
from app.services.notification_service import NotificationService
from app.services.analytics_service import AnalyticsService
from app.core.logging import get_logger
from app.core.exceptions import ValidationException

logger = get_logger("service.workflow")


class WorkflowService:
    def __init__(self):
        self.order_svc = OrderService()
        self.inv_svc = InventoryService()
        self.transfer_svc = TransferService()
        self.finance_svc = FinanceService()
        self.approval_svc = ApprovalService()
        self.notif_svc = NotificationService()
        self.analytics_svc = AnalyticsService()

    def process_purchase(
        self,
        customer_id: str,
        branch_id: str,
        medicine_id: str,
        quantity: int,
    ) -> dict:
        """
        Execute the full medicine purchase workflow.
        Returns the outcome including all created entities.
        """
        workflow_id = str(uuid_mod.uuid4())
        logger.info(f"[WF-{workflow_id}] Starting purchase workflow")

        # ── Step 1: Sales AI Validation (Mocked) ─────────────────
        ai_validation = True  # Future: call LangGraph Sales AI agent
        self.notif_svc.create_ai_log(
            agent_name="Sales AI",
            message=f"Order validated for customer {customer_id}, medicine {medicine_id}, qty {quantity}",
            session_id=workflow_id,
        )
        self.analytics_svc.record_ai_decision(branch_id)

        if not ai_validation:
            raise ValidationException("Sales AI rejected this order.")

        # ── Step 2: Check Local Inventory ─────────────────────────
        stock_check = self.inv_svc.check_local_inventory(branch_id, medicine_id, quantity)

        if stock_check["available"]:
            return self._execute_local_order(
                workflow_id, customer_id, branch_id, medicine_id, quantity, stock_check
            )
        else:
            return self._execute_transfer_workflow(
                workflow_id, customer_id, branch_id, medicine_id, quantity, stock_check
            )

    def _execute_local_order(
        self,
        workflow_id: str,
        customer_id: str,
        branch_id: str,
        medicine_id: str,
        quantity: int,
        stock_check: dict,
    ) -> dict:
        """
        Happy path: stock exists locally.
        Reserve → Order → Invoice → Analytics → Notification
        """
        logger.info(f"[WF-{workflow_id}] Local stock available. Proceeding with local order.")

        # ── Step 3a.1: Reserve Inventory (FEFO) ──────────────────
        batches = stock_check["batches"]
        if not batches:
            raise ValidationException("Stock data inconsistent — no batches found.")

        # Use the first available batch (FEFO-sorted from repository)
        primary_batch_id = batches[0].get("batch_id", batches[0].get("id"))

        reserved = self.inv_svc.reserve_inventory(branch_id, medicine_id, quantity)
        self.notif_svc.create_ai_log(
            agent_name="Inventory AI",
            message=f"Stock reserved: {quantity} units via FEFO at branch {branch_id}",
            session_id=workflow_id,
        )

        try:
            # ── Step 3a.2: Create Order ──────────────────────────────
            order = self.order_svc.create_order(
                branch_id=branch_id,
                customer_id=customer_id,
                items=[{
                    "medicine_id": medicine_id,
                    "batch_id": primary_batch_id,
                    "quantity": quantity,
                }],
            )

            # ── Step 3a.3: Complete Order ────────────────────────────
            self.order_svc.complete_order(order["id"])

            # ── Step 3a.4: Generate Invoice ──────────────────────────
            invoice = self.order_svc.generate_invoice(order["id"], branch_id)

            # ── Step 3a.5: Update Analytics ──────────────────────────
            self.analytics_svc.record_sale(
                branch_id=branch_id,
                total_amount=float(order.get("total_amount", 0)),
                items_sold=quantity,
            )

            # ── Step 3a.6: Create Notification ───────────────────────
            self.notif_svc.notify_branch(
                branch_id=branch_id,
                title="Order Completed",
                message=f"Order {order.get('order_no', order['id'])} completed. "
                        f"Invoice: {invoice.get('invoice_no', invoice['id'])}",
                severity="info",
            )
        except Exception as e:
            logger.error(f"[WF-{workflow_id}] Error in local order processing. Rolling back reservation. Error: {e}")
            for res_item in reserved:
                self.inv_svc.release_inventory(
                    branch_id=branch_id,
                    medicine_id=medicine_id,
                    batch_id=res_item["batch_id"],
                    quantity=res_item["deducted"],
                )
            raise e

        # Commit stock once all creation steps succeed
        for res_item in reserved:
            self.inv_svc.commit_inventory(
                branch_id=branch_id,
                medicine_id=medicine_id,
                batch_id=res_item["batch_id"],
                quantity=res_item["deducted"],
            )

        logger.info(f"[WF-{workflow_id}] Local order completed & committed: {order['id']}")

        return {
            "workflow_id": workflow_id,
            "status": "completed_locally",
            "order": order,
            "invoice": invoice,
            "reserved_batches": reserved,
        }

    def _execute_transfer_workflow(
        self,
        workflow_id: str,
        customer_id: str,
        branch_id: str,
        medicine_id: str,
        quantity: int,
        stock_check: dict,
    ) -> dict:
        """
        Fallback path: local stock insufficient.
        Network scan → Transfer proposal → Finance → Approval → Notification
        """
        logger.info(f"[WF-{workflow_id}] Local stock insufficient. Initiating transfer workflow.")

        # ── Step 3b.1: Record Stockout ───────────────────────────
        self.analytics_svc.record_stockout(branch_id)
        self.notif_svc.create_ai_log(
            agent_name="Regional AI Manager",
            message=f"Stockout detected at branch {branch_id} for medicine {medicine_id}. "
                    f"Available: {stock_check['total_stock']}, Required: {quantity}. Scanning network...",
            session_id=workflow_id,
        )
        self.analytics_svc.record_ai_decision(branch_id)

        # ── Step 3b.2: Find Nearest Branch with Stock ────────────
        source = self.inv_svc.find_nearest_branch_with_stock(branch_id, medicine_id)

        if not source:
            self.notif_svc.notify_branch(
                branch_id=branch_id,
                title="Stock Unavailable Network-Wide",
                message=f"Medicine {medicine_id} is out of stock across all branches.",
                severity="high",
                notification_type="critical_alert",
            )
            return {
                "workflow_id": workflow_id,
                "status": "stock_unavailable_network_wide",
                "local_stock": stock_check["total_stock"],
                "required": quantity,
            }

        source_branch_id = source["branch_id"]
        source_batch_id = source.get("batch_id", "")
        source_quantity = source.get("quantity", 0)

        self.notif_svc.create_ai_log(
            agent_name="Inventory AI",
            message=f"Transfer recommended from branch {source_branch_id} "
                    f"(available: {source_quantity} units)",
            session_id=workflow_id,
        )

        # ── Step 3b.3: Finance AI Calculates Transfer Cost ───────
        cost = self.finance_svc.calculate_transfer_cost(
            from_branch_id=source_branch_id,
            to_branch_id=branch_id,
            quantity=quantity,
        )
        self.notif_svc.create_ai_log(
            agent_name="Finance AI",
            message=f"Transfer cost calculated: ₹{cost['total']} for {quantity} units",
            session_id=workflow_id,
        )
        self.analytics_svc.record_ai_decision(branch_id)

        # ── Step 3b.4: Generate Transfer Proposal ────────────────
        transfer = self.transfer_svc.create_transfer_proposal(
            from_branch_id=source_branch_id,
            to_branch_id=branch_id,
            medicine_id=medicine_id,
            batch_id=source_batch_id,
            quantity=quantity,
            freight_charges=cost["total"],
        )

        # ── Step 3b.5: Create Approval Request ───────────────────
        approval = self.approval_svc.create_transfer_approval(
            transfer_id=transfer["id"],
            branch_id=branch_id,
            title=f"Transfer Approval: {quantity} units from {source_branch_id}",
            description=f"Medicine {medicine_id}, estimated cost: ₹{cost['total']}",
        )

        # ── Step 3b.6: Notification ──────────────────────────────
        self.notif_svc.notify_branch(
            branch_id=branch_id,
            title="Transfer Proposal Generated",
            message=f"Transfer of {quantity} units proposed from branch {source_branch_id}. "
                    f"Estimated cost: ₹{cost['total']}. Awaiting manager approval.",
            severity="medium",
            notification_type="ai_trace",
        )

        logger.info(f"[WF-{workflow_id}] Transfer proposal created: {transfer['id']}")

        return {
            "workflow_id": workflow_id,
            "status": "transfer_proposed",
            "transfer": transfer,
            "approval": approval,
            "cost": cost,
            "source_branch_id": source_branch_id,
            "local_stock": stock_check["total_stock"],
        }
