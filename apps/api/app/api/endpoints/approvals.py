"""
POST /approvals — Approve or reject a transfer/document.
"""
from fastapi import APIRouter, HTTPException
from app.schemas.workflow import ApprovalRequest
from app.services.approval_service import ApprovalService
from app.services.transfer_service import TransferService
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger("api.approvals")


@router.post("/")
def process_approval(req: ApprovalRequest):
    """Approve or reject a pending approval. If approved, executes the linked transfer."""
    try:
        approval_svc = ApprovalService()
        transfer_svc = TransferService()

        # Determine which approval to process
        if req.approval_id:
            approval_id = str(req.approval_id)
        elif req.transfer_id:
            # Look up the approval by transfer reference
            pending = approval_svc.get_pending()
            matched = [
                a for a in pending
                if a.get("document_reference_id") == str(req.transfer_id)
            ]
            if not matched:
                raise HTTPException(status_code=404, detail="No pending approval found for this transfer.")
            approval_id = matched[0]["id"]
        else:
            raise HTTPException(status_code=422, detail="Provide either approval_id or transfer_id.")

        actor_id = str(req.approved_by)

        if req.approved:
            # Approve
            approval = approval_svc.approve(approval_id, actor_id, req.comments)

            # Execute the linked transfer if it's a stock_transfer type
            approval_data = approval_svc.get_approval(approval_id)
            if approval_data.get("document_type") == "stock_transfer":
                transfer_id = approval_data["document_reference_id"]
                transfer = transfer_svc.approve_and_execute(transfer_id)
                return {
                    "status": "approved_and_executed",
                    "approval": approval,
                    "transfer": transfer,
                }

            return {"status": "approved", "approval": approval}
        else:
            # Reject
            approval = approval_svc.reject(approval_id, actor_id, req.comments)

            # Also reject the linked transfer
            approval_data = approval_svc.get_approval(approval_id)
            if approval_data.get("document_type") == "stock_transfer":
                transfer_id = approval_data["document_reference_id"]
                transfer_svc.reject_transfer(
                    transfer_id, req.comments or "Rejected by manager"
                )

            return {"status": "rejected", "approval": approval}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Approval processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pending")
def get_pending_approvals(branch_id: str = None):
    """List all pending approvals, optionally filtered by branch."""
    try:
        svc = ApprovalService()
        return svc.get_pending(branch_id)
    except Exception as e:
        logger.error(f"Get pending approvals failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
