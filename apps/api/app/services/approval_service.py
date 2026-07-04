"""
Nexus AI — Approval Service
Manages the approval workflow for transfers and other documents.
Uses real Supabase database through ApprovalRepository.
"""
from __future__ import annotations
from app.repositories.approval_repo import ApprovalRepository
from app.core.logging import get_logger

logger = get_logger("service.approval")

# The Branch Manager role ID from seed data
BRANCH_MANAGER_ROLE_ID = "d3333333-3333-4333-a333-333333333333"


class ApprovalService:
    def __init__(self):
        self.repo = ApprovalRepository()

    def create_transfer_approval(
        self,
        transfer_id: str,
        branch_id: str,
        title: str,
        description: str | None = None,
        created_by: str | None = None,
    ) -> dict:
        """
        Create an approval request for a stock transfer.
        Sets up a single-step approval assigned to the BRANCH_MANAGER role.
        """
        approval = self.repo.create_approval(
            branch_id=branch_id,
            document_type="stock_transfer",
            document_reference_id=transfer_id,
            title=title,
            description=description,
            total_steps=1,
            created_by=created_by,
        )

        # Create the approval step
        self.repo.create_approval_step(
            approval_id=approval["id"],
            step_number=1,
            approver_role_id=BRANCH_MANAGER_ROLE_ID,
        )

        logger.info(f"Transfer approval created: {approval['id']} for transfer {transfer_id}")
        return approval

    def approve(self, approval_id: str, actor_id: str, comments: str | None = None) -> dict:
        """Approve a pending approval."""
        result = self.repo.approve(approval_id, actor_id, comments)
        logger.info(f"Approval {approval_id} approved by {actor_id}")
        return result

    def reject(self, approval_id: str, actor_id: str, comments: str | None = None) -> dict:
        """Reject a pending approval."""
        result = self.repo.reject(approval_id, actor_id, comments)
        logger.info(f"Approval {approval_id} rejected by {actor_id}")
        return result

    def get_pending(self, branch_id: str | None = None) -> list[dict]:
        """Get all pending approvals, optionally filtered by branch."""
        return self.repo.get_pending_approvals(branch_id)

    def get_approval(self, approval_id: str) -> dict:
        """Get a specific approval by ID."""
        return self.repo.find_by_id(approval_id)
