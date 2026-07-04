"""
Nexus AI — Collaboration Context & Shared State
Models for maintaining order check status, telemetry monitoring, and workflows.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from uuid import UUID
import datetime

# --- SHARED BUSINESS STATE ---
class OrderState(BaseModel):
    order_id: Optional[str] = None
    customer_id: Optional[str] = None
    items: List[Dict[str, Any]] = []
    total_amount: float = 0.0
    status: str = "PENDING"

class InventoryState(BaseModel):
    checked: bool = False
    is_available: bool = False
    low_stock_items: List[str] = []

class TransferState(BaseModel):
    needed: bool = False
    from_branch: Optional[str] = None
    to_branch: Optional[str] = None
    medicine_id: Optional[str] = None
    quantity: int = 0
    estimated_freight_cost: float = 0.0

class ApprovalState(BaseModel):
    req_level: int = 0
    requires_approval: bool = False
    approved: bool = False
    approved_by: Optional[str] = None

class InvoiceState(BaseModel):
    generated: bool = False
    invoice_id: Optional[str] = None
    final_billing_amount: float = 0.0

class NotificationState(BaseModel):
    sent: bool = False
    recipient: Optional[str] = None
    channels: List[str] = []

class SharedBusinessState(BaseModel):
    order: OrderState = Field(default_factory=OrderState)
    inventory: InventoryState = Field(default_factory=InventoryState)
    transfer: TransferState = Field(default_factory=TransferState)
    approval: ApprovalState = Field(default_factory=ApprovalState)
    invoice: InvoiceState = Field(default_factory=InvoiceState)
    notifications: NotificationState = Field(default_factory=NotificationState)
    progress: List[str] = []

# --- METRICS & TELEMETRY ---
class CollaborationMetrics(BaseModel):
    workflow_duration_ms: float = 0.0
    agent_latencies: Dict[str, float] = {}
    success_rate: float = 1.0
    decision_accuracy: float = 1.0
    agent_communication_count: int = 0

class WorkflowContext(BaseModel):
    workflow_id: UUID
    session_id: str
    shared_state: SharedBusinessState = Field(default_factory=SharedBusinessState)
    metrics: CollaborationMetrics = Field(default_factory=CollaborationMetrics)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
