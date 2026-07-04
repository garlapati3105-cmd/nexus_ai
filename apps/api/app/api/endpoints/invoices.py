"""
POST /invoices — Generate an invoice for an existing order.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from uuid import UUID
from app.services.order_service import OrderService
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger("api.invoices")


class InvoiceCreateRequest(BaseModel):
    order_id: UUID
    branch_id: UUID


@router.post("/")
def create_invoice(req: InvoiceCreateRequest):
    """Generate an invoice for a completed order."""
    try:
        svc = OrderService()
        invoice = svc.generate_invoice(str(req.order_id), str(req.branch_id))
        return invoice
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Invoice creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
