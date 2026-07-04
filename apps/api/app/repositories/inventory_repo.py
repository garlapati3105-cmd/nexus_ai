"""
Nexus AI — Inventory Repository
Real Supabase operations for: inventory, inventory_transactions, medicine lookup.
"""
from __future__ import annotations
from typing import Any
from app.repositories.base import BaseRepository
from app.core.logging import get_logger
from app.core.exceptions import DatabaseOperationException, InsufficientStockException

logger = get_logger("repository.inventory")


class InventoryRepository(BaseRepository):
    TABLE_NAME = "inventory"

    def check_stock(self, branch_id: str, medicine_id: str) -> list[dict]:
        """
        Returns all inventory rows for a given medicine at a branch.
        Sorted by batch expiry (FEFO — First Expiry, First Out).
        """
        try:
            result = (
                self.db.table("inventory")
                .select("*, medicine_batches!inner(id, batch_number, expiry_date)")
                .eq("branch_id", branch_id)
                .eq("medicine_id", medicine_id)
                .gt("quantity", 0)
                .order("medicine_batches(expiry_date)", desc=False)
                .execute()
            )
            return result.data or []
        except Exception as e:
            logger.error(f"check_stock failed: {e}")
            # Fallback: query without join ordering
            try:
                result = (
                    self.db.table("inventory")
                    .select("*")
                    .eq("branch_id", branch_id)
                    .eq("medicine_id", medicine_id)
                    .gt("quantity", 0)
                    .execute()
                )
                return result.data or []
            except Exception as e2:
                logger.error(f"check_stock fallback failed: {e2}")
                raise DatabaseOperationException("check_stock", str(e2))

    def get_total_stock(self, branch_id: str, medicine_id: str) -> int:
        """Returns the sum of all batch quantities for a medicine at a branch."""
        rows = self.check_stock(branch_id, medicine_id)
        return sum(row.get("quantity", 0) for row in rows)

    def reserve_stock(
        self,
        branch_id: str,
        medicine_id: str,
        quantity: int,
    ) -> list[dict]:
        """
        Decrements inventory using FEFO strategy.
        Returns the list of inventory rows that were decremented.
        Raises InsufficientStockException if not enough stock.
        """
        rows = self.check_stock(branch_id, medicine_id)
        total_available = sum(r["quantity"] for r in rows)

        if total_available < quantity:
            raise InsufficientStockException(branch_id, medicine_id, total_available, quantity)

        remaining = quantity
        updated_rows = []

        for row in rows:
            if remaining <= 0:
                break

            batch_qty = row["quantity"]
            deduction = min(batch_qty, remaining)
            new_qty = batch_qty - deduction

            updated = self.update(row["id"], {"quantity": new_qty})
            updated_rows.append({
                "inventory_id": row["id"],
                "batch_id": row["batch_id"],
                "deducted": deduction,
                "remaining": new_qty,
            })
            remaining -= deduction

        logger.info(
            f"Reserved {quantity} units of medicine {medicine_id} at branch {branch_id}"
        )
        return updated_rows

    def find_stock_across_network(
        self,
        medicine_id: str,
        exclude_branch_id: str,
    ) -> list[dict]:
        """
        Searches all branches for stock of a specific medicine.
        Excludes the requesting branch. Returns branches sorted by quantity desc.
        """
        try:
            result = (
                self.db.table("inventory")
                .select("*, branches!inner(id, name, code, city)")
                .eq("medicine_id", medicine_id)
                .neq("branch_id", exclude_branch_id)
                .gt("quantity", 0)
                .order("quantity", desc=True)
                .execute()
            )
            return result.data or []
        except Exception as e:
            logger.error(f"find_stock_across_network failed: {e}")
            # Fallback without join
            try:
                result = (
                    self.db.table("inventory")
                    .select("*")
                    .eq("medicine_id", medicine_id)
                    .neq("branch_id", exclude_branch_id)
                    .gt("quantity", 0)
                    .order("quantity", desc=True)
                    .execute()
                )
                return result.data or []
            except Exception as e2:
                raise DatabaseOperationException("find_stock_across_network", str(e2))

    def get_branch_inventory(
        self,
        branch_id: str,
        offset: int = 0,
        limit: int = 50,
    ) -> list[dict]:
        """Paginated list of all inventory for a branch."""
        return self.list(
            filters={"branch_id": branch_id},
            offset=offset,
            limit=limit,
        )

    def create_inventory_transaction(self, tx_data: dict[str, Any]) -> dict:
        """Insert an inventory_transactions record for audit purposes."""
        try:
            result = self.db.table("inventory_transactions").insert(tx_data).execute()
            if result.data:
                return result.data[0]
            raise DatabaseOperationException("create_inventory_transaction", "No data returned")
        except DatabaseOperationException:
            raise
        except Exception as e:
            logger.error(f"create_inventory_transaction failed: {e}")
            raise DatabaseOperationException("create_inventory_transaction", str(e))
