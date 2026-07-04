"""
POST /orders — Create order and trigger the full purchase workflow.
"""
from fastapi import APIRouter, HTTPException
from app.schemas.workflow import OrderRequest
from app.services.workflow_service import WorkflowService
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger("api.orders")


@router.post("/")
def create_order(request: OrderRequest):
    """Execute the full medicine purchase workflow."""
    try:
        workflow_svc = WorkflowService()
        result = workflow_svc.process_purchase(
            customer_id=str(request.customer_id),
            branch_id=str(request.branch_id),
            medicine_id=str(request.medicine_id),
            quantity=request.quantity,
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Order creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
