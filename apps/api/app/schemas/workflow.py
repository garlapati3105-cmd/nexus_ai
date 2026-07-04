"""
Nexus AI — Pydantic Schemas
Request and response models for the workflow API.
API contracts are unchanged — only types are tightened.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID


# ─── Order Schemas ───────────────────────────────────────────
class OrderRequest(BaseModel):
    customer_id: UUID
    branch_id: UUID
    medicine_id: UUID
    quantity: int = Field(gt=0, le=10000, description="Order quantity (1-10000)")


class OrderItemResponse(BaseModel):
    id: Optional[str] = None
    medicine_id: str
    batch_id: str
    quantity: int
    unit_price: float
    discount_percentage: float
    net_price: float


# ─── Inventory Schemas ───────────────────────────────────────
class InventoryCheckRequest(BaseModel):
    branch_id: UUID
    medicine_id: UUID
    quantity: int = Field(gt=0, default=1)


# ─── Transfer Schemas ────────────────────────────────────────
class TransferProposal(BaseModel):
    from_branch_id: UUID
    to_branch_id: UUID
    medicine_id: UUID
    quantity: int = Field(gt=0)
    cost: float = 0.0


# ─── Approval Schemas ────────────────────────────────────────
class ApprovalRequest(BaseModel):
    transfer_id: Optional[UUID] = None
    approval_id: Optional[UUID] = None
    approved: bool
    approved_by: UUID
    comments: Optional[str] = None
