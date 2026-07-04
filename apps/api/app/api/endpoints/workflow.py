"""
GET /workflow/{id} — Get workflow status.
Note: In the current phase, workflow state is not persisted.
This returns transfer/approval status when given a related entity ID.
"""
from fastapi import APIRouter, HTTPException
from uuid import UUID
from app.services.transfer_service import TransferService
from app.services.approval_service import ApprovalService
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger("api.workflow")


@router.get("/{id}")
def get_workflow_status(id: UUID):
    """
    Get workflow status by ID.
    Attempts to resolve as transfer first, then approval.
    """
    entity_id = str(id)
    try:
        # Try as transfer
        try:
            transfer_svc = TransferService()
            transfer = transfer_svc.get_transfer(entity_id)
            return {
                "workflow_id": entity_id,
                "type": "stock_transfer",
                "status": transfer.get("status"),
                "data": transfer,
            }
        except Exception:
            pass

        # Try as approval
        try:
            approval_svc = ApprovalService()
            approval = approval_svc.get_approval(entity_id)
            return {
                "workflow_id": entity_id,
                "type": "approval",
                "status": approval.get("status"),
                "data": approval,
            }
        except Exception:
            pass

        raise HTTPException(status_code=404, detail=f"No workflow found with ID {entity_id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Workflow status lookup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
