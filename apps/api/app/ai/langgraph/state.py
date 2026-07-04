"""
Nexus AI — LangGraph State Management
Defines workflow execution schemas, order telemetry, and transition logs.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional, TypedDict

class OrderState(TypedDict, total=False):
    order_id: str
    customer_id: str
    items: List[Dict[str, Any]]
    total_amount: float
    status: str

class InventoryState(TypedDict, total=False):
    checked: bool
    is_available: bool
    low_stock_items: List[str]

class TransferState(TypedDict, total=False):
    needed: bool
    from_branch: Optional[str]
    to_branch: Optional[str]
    medicine_id: Optional[str]
    quantity: int
    estimated_freight_cost: float

class ApprovalState(TypedDict, total=False):
    requires_approval: bool
    approved: bool
    approved_by: Optional[str]

class InvoiceState(TypedDict, total=False):
    generated: bool
    invoice_id: Optional[str]
    final_billing_amount: float

class NotificationState(TypedDict, total=False):
    sent: bool
    recipient: Optional[str]
    channels: List[str]

class GraphWorkflowState(TypedDict):
    order: OrderState
    inventory: InventoryState
    transfer: TransferState
    approval: ApprovalState
    invoice: InvoiceState
    notifications: NotificationState
    # Pipeline control parameters
    medicine_id: str
    quantity: int
    branch_id: str
    has_prescription: bool
    # Tracing, monitoring & state rollback elements
    progress: List[str]
    session_id: str
    workflow_id: str
    errors: List[str]
    agent_latencies: Dict[str, float]
    sales_outputs: Dict[str, Any]
    inventory_outputs: Dict[str, Any]
    finance_outputs: Dict[str, Any]
    composite_decision: Dict[str, Any]
