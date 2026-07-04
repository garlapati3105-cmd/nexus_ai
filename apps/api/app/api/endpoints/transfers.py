"""
POST /transfers — Create a stock transfer between branches.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional
from app.services.transfer_service import TransferService
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger("api.transfers")


class TransferCreateRequest(BaseModel):
    from_branch_id: UUID
    to_branch_id: UUID
    medicine_id: UUID
    batch_id: UUID
    quantity: int = Field(gt=0)
    freight_charges: float = 0.0


@router.post("/")
def create_transfer(req: TransferCreateRequest):
    """Create an inter-branch stock transfer proposal."""
    try:
        svc = TransferService()
        result = svc.create_transfer_proposal(
            from_branch_id=str(req.from_branch_id),
            to_branch_id=str(req.to_branch_id),
            medicine_id=str(req.medicine_id),
            batch_id=str(req.batch_id),
            quantity=req.quantity,
            freight_charges=req.freight_charges,
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transfer creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{transfer_id}")
def get_transfer(transfer_id: UUID):
    """Get a transfer by ID with its items."""
    try:
        svc = TransferService()
        return svc.get_transfer(str(transfer_id))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get transfer failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
