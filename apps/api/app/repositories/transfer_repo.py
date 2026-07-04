"""
Nexus AI — Transfer Repository
Real Supabase operations for: stock_transfers, transfer_items.
"""
from __future__ import annotations
from typing import Any
from app.repositories.base import BaseRepository
from app.core.logging import get_logger
from app.core.exceptions import DatabaseOperationException

logger = get_logger("repository.transfer")


class TransferRepository(BaseRepository):
    TABLE_NAME = "stock_transfers"

    def create_transfer(
        self,
        from_branch_id: str,
        to_branch_id: str,
        created_by: str | None = None,
        freight_charges: float = 0.0,
    ) -> dict:
        """Create a new stock_transfers record in 'draft' status."""
        data = {
            "from_branch_id": from_branch_id,
            "to_branch_id": to_branch_id,
            "status": "draft",
            "freight_charges": freight_charges,
            "created_by": created_by,
        }
        return self.create(data)

    def add_transfer_item(self, item_data: dict[str, Any]) -> dict:
        """Insert a transfer_items row."""
        try:
            result = self.db.table("transfer_items").insert(item_data).execute()
            if result.data:
                return result.data[0]
            raise DatabaseOperationException("add_transfer_item", "No data returned")
        except DatabaseOperationException:
            raise
        except Exception as e:
            logger.error(f"add_transfer_item failed: {e}")
            raise DatabaseOperationException("add_transfer_item", str(e))

    def update_status(self, transfer_id: str, new_status: str, extra: dict | None = None) -> dict:
        """Update the transfer status and optionally set additional fields."""
        data = {"status": new_status}
        if extra:
            data.update(extra)
        return self.update(transfer_id, data)

    def get_transfer_items(self, transfer_id: str) -> list[dict]:
        """Fetch all line items for a transfer."""
        try:
            result = (
                self.db.table("transfer_items")
                .select("*")
                .eq("transfer_id", transfer_id)
                .execute()
            )
            return result.data or []
        except Exception as e:
            logger.error(f"get_transfer_items failed: {e}")
            raise DatabaseOperationException("get_transfer_items", str(e))

    def get_transfers_by_branch(
        self,
        branch_id: str,
        direction: str = "to",
        status: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> list[dict]:
        """
        Fetch transfers where the branch is either sender or receiver.
        direction: 'from' | 'to' | 'both'
        """
        try:
            col = "to_branch_id" if direction == "to" else "from_branch_id"
            query = self.db.table(self.TABLE_NAME).select("*").eq(col, branch_id)

            if status:
                query = query.eq("status", status)

            query = query.order("created_at", desc=True).range(offset, offset + limit - 1)
            result = query.execute()
            return result.data or []
        except Exception as e:
            logger.error(f"get_transfers_by_branch failed: {e}")
            raise DatabaseOperationException("get_transfers_by_branch", str(e))
