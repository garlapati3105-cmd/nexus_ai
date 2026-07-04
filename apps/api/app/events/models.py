"""
Nexus AI — Enterprise Event Models
Defines schema constraints for all business-level realtime events.
"""
from __future__ import annotations
import time
from uuid import uuid4
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class BaseEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"evt-{uuid4().hex[:8].upper()}")
    event_type: str
    timestamp: float = Field(default_factory=time.time)
    organization_id: str
    branch_id: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
    version: str = "1.0.0"

# Specific Business Events
class OrderCreated(BaseEvent):
    event_type: str = "OrderCreated"

class OrderUpdated(BaseEvent):
    event_type: str = "OrderUpdated"

class OrderCompleted(BaseEvent):
    event_type: str = "OrderCompleted"

class InventoryReserved(BaseEvent):
    event_type: str = "InventoryReserved"

class InventoryUpdated(BaseEvent):
    event_type: str = "InventoryUpdated"

class LowStockDetected(BaseEvent):
    event_type: str = "LowStockDetected"

class MedicineExpired(BaseEvent):
    event_type: str = "MedicineExpired"

class TransferRequested(BaseEvent):
    event_type: str = "TransferRequested"

class TransferApproved(BaseEvent):
    event_type: str = "TransferApproved"

class TransferCompleted(BaseEvent):
    event_type: str = "TransferCompleted"

class SupplierOrderCreated(BaseEvent):
    event_type: str = "SupplierOrderCreated"

class InvoiceGenerated(BaseEvent):
    event_type: str = "InvoiceGenerated"

class PaymentCompleted(BaseEvent):
    event_type: str = "PaymentCompleted"

class ApprovalRequested(BaseEvent):
    event_type: str = "ApprovalRequested"

class ApprovalApproved(BaseEvent):
    event_type: str = "ApprovalApproved"

class ApprovalRejected(BaseEvent):
    event_type: str = "ApprovalRejected"

class RecommendationGenerated(BaseEvent):
    event_type: str = "RecommendationGenerated"

class AIWorkflowStarted(BaseEvent):
    event_type: str = "AIWorkflowStarted"

class AIWorkflowCompleted(BaseEvent):
    event_type: str = "AIWorkflowCompleted"

class KnowledgeUpdated(BaseEvent):
    event_type: str = "KnowledgeUpdated"

class BranchHealthChanged(BaseEvent):
    event_type: str = "BranchHealthChanged"

class DashboardMetricsUpdated(BaseEvent):
    event_type: str = "DashboardMetricsUpdated"

class NotificationCreated(BaseEvent):
    event_type: str = "NotificationCreated"
