"""
Nexus AI — Transfer Service
Manages inter-branch stock transfer lifecycle.
All operations use real Supabase database through TransferRepository.
"""
from __future__ import annotations
from app.repositories.transfer_repo import TransferRepository
from app.repositories.inventory_repo import InventoryRepository
from app.core.logging import get_logger
from app.core.exceptions import TransferConflictException, EntityNotFoundException

logger = get_logger("service.transfer")


class TransferService:
    def __init__(self):
        self.repo = TransferRepository()
        self.inv_repo = InventoryRepository()

    def create_transfer_proposal(
        self,
        from_branch_id: str,
        to_branch_id: str,
        medicine_id: str,
        batch_id: str,
        quantity: int,
        freight_charges: float = 0.0,
        created_by: str | None = None,
    ) -> dict:
        """
        Create a stock_transfers record in 'draft' status with line items.
        """
        # Create the transfer header
        transfer = self.repo.create_transfer(
            from_branch_id=from_branch_id,
            to_branch_id=to_branch_id,
            created_by=created_by,
            freight_charges=freight_charges,
        )

        # Add transfer item
        item = self.repo.add_transfer_item({
            "transfer_id": transfer["id"],
            "medicine_id": medicine_id,
            "batch_id": batch_id,
            "qty_requested": quantity,
        })

        # Update status to pending_approval
        self.repo.update_status(transfer["id"], "pending_approval")

        transfer["items"] = [item]
        transfer["status"] = "pending_approval"
        logger.info(
            f"Transfer proposal created: {transfer['id']} "
            f"from {from_branch_id} → {to_branch_id}, qty={quantity}"
        )
        return transfer

    def approve_and_execute(self, transfer_id: str) -> dict:
        """
        Approve a transfer: deduct stock from source, update status to 'approved'.
        """
        transfer = self.repo.find_by_id(transfer_id)

        if transfer["status"] not in ("pending_approval", "draft"):
            raise TransferConflictException(
                f"Transfer {transfer_id} cannot be approved (current status: {transfer['status']})"
            )

        items = self.repo.get_transfer_items(transfer_id)

        # Deduct stock from the source branch
        for item in items:
            try:
                self.inv_repo.reserve_stock(
                    branch_id=transfer["from_branch_id"],
                    medicine_id=item["medicine_id"],
                    quantity=item["qty_requested"],
                )
                # Update qty_shipped
                self.repo.db.table("transfer_items").update(
                    {"qty_shipped": item["qty_requested"]}
                ).eq("id", item["id"]).execute()
            except Exception as e:
                logger.error(f"Stock deduction failed during transfer approval: {e}")
                self.repo.update_status(transfer_id, "cancelled", {"rejection_reason": str(e)})
                raise

        # Update transfer status to approved
        updated = self.repo.update_status(transfer_id, "approved")
        logger.info(f"Transfer {transfer_id} approved and stock deducted")
        return updated

    def reject_transfer(self, transfer_id: str, reason: str) -> dict:
        """Reject a transfer with a reason."""
        return self.repo.update_status(
            transfer_id, "rejected", {"rejection_reason": reason}
        )

    def receive_transfer(self, transfer_id: str) -> dict:
        """
        Mark a transfer as received.
        In a full implementation, this would add stock to the destination branch.
        """
        transfer = self.repo.find_by_id(transfer_id)
        if transfer["status"] != "approved":
            raise TransferConflictException(
                f"Transfer {transfer_id} cannot be received (status: {transfer['status']})"
            )

        updated = self.repo.update_status(transfer_id, "received")
        logger.info(f"Transfer {transfer_id} marked as received")
        return updated

    def get_transfer(self, transfer_id: str) -> dict:
        """Get a single transfer with items."""
        transfer = self.repo.find_by_id(transfer_id)
        transfer["items"] = self.repo.get_transfer_items(transfer_id)
        return transfer
