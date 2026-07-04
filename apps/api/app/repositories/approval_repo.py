"""
Nexus AI — Approval Repository
Real Supabase operations for: approvals, approval_steps, approval_history.
"""
from __future__ import annotations
from app.repositories.base import BaseRepository
from app.core.logging import get_logger
from app.core.exceptions import DatabaseOperationException
from app.core.config import get_settings

logger = get_logger("repository.approval")


class ApprovalRepository(BaseRepository):
    TABLE_NAME = "approvals"

    def create_approval(
        self,
        branch_id: str,
        document_type: str,
        document_reference_id: str,
        title: str,
        description: str | None = None,
        total_steps: int = 1,
        created_by: str | None = None,
    ) -> dict:
        """Create an approval workflow record."""
        settings = get_settings()
        data = {
            "organization_id": settings.ORG_ID,
            "branch_id": branch_id,
            "document_type": document_type,
            "document_reference_id": document_reference_id,
            "title": title,
            "description": description,
            "current_step": 1,
            "total_steps": total_steps,
            "status": "pending",
            "created_by": created_by,
        }
        return self.create(data)

    def create_approval_step(self, approval_id: str, step_number: int, approver_role_id: str | None = None) -> dict:
        """Create an approval step."""
        data = {
            "approval_id": approval_id,
            "step_number": step_number,
            "approver_role_id": approver_role_id,
            "status": "pending",
        }
        try:
            result = self.db.table("approval_steps").insert(data).execute()
            if result.data:
                return result.data[0]
            raise DatabaseOperationException("create_approval_step", "No data returned")
        except DatabaseOperationException:
            raise
        except Exception as e:
            logger.error(f"create_approval_step failed: {e}")
            raise DatabaseOperationException("create_approval_step", str(e))

    def approve(self, approval_id: str, actor_id: str, comments: str | None = None) -> dict:
        """Mark an approval as approved and log history."""
        # Update main approval
        updated = self.update(approval_id, {"status": "approved"})

        # Log into approval_history
        try:
            approval = self.find_by_id(approval_id)
            self.db.table("approval_history").insert({
                "approval_id": approval_id,
                "step_number": approval.get("current_step", 1),
                "action_taken": "approved",
                "actor_id": actor_id,
                "comments": comments,
            }).execute()
        except Exception as e:
            logger.warning(f"approval_history insert failed (non-fatal): {e}")

        return updated

    def reject(self, approval_id: str, actor_id: str, comments: str | None = None) -> dict:
        """Mark an approval as rejected."""
        updated = self.update(approval_id, {"status": "rejected"})

        try:
            approval = self.find_by_id(approval_id)
            self.db.table("approval_history").insert({
                "approval_id": approval_id,
                "step_number": approval.get("current_step", 1),
                "action_taken": "rejected",
                "actor_id": actor_id,
                "comments": comments,
            }).execute()
        except Exception as e:
            logger.warning(f"approval_history insert failed (non-fatal): {e}")

        return updated

    def get_pending_approvals(self, branch_id: str | None = None, limit: int = 50) -> list[dict]:
        """List pending approvals, optionally filtered by branch."""
        filters = {"status": "pending"}
        if branch_id:
            filters["branch_id"] = branch_id
        return self.list(filters=filters, limit=limit)
