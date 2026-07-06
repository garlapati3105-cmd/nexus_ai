"""
Nexus AI — Inventory Service
Handles local stock checks, FEFO reservation, and network-wide stock search.
All operations use real Supabase database through InventoryRepository.
"""
from __future__ import annotations
from app.repositories.inventory_repo import InventoryRepository
from app.core.logging import get_logger
from app.core.exceptions import InsufficientStockException

logger = get_logger("service.inventory")


class InventoryService:
    def __init__(self):
        self.repo = InventoryRepository()

    def check_local_inventory(
        self,
        branch_id: str,
        medicine_id: str,
        required_qty: int,
    ) -> dict:
        """
        Check if a branch has sufficient stock for a medicine.
        Returns {"available": bool, "total_stock": int, "batches": [...]}
        """
        total = self.repo.get_total_stock(branch_id, medicine_id)
        batches = self.repo.check_stock(branch_id, medicine_id)

        result = {
            "available": total >= required_qty,
            "total_stock": total,
            "batches": batches,
        }
        logger.info(
            f"Stock check: branch={branch_id}, medicine={medicine_id}, "
            f"required={required_qty}, available={total}, sufficient={result['available']}"
        )
        return result

    def reserve_inventory(
        self,
        branch_id: str,
        medicine_id: str,
        quantity: int,
    ) -> list[dict]:
        """
        Reserve stock using FEFO strategy (deducts from oldest-expiry batches first).
        Returns list of deducted batch details.
        Raises InsufficientStockException if not enough stock.
        """
        logger.info(f"Reserving {quantity} units of {medicine_id} at branch {branch_id}")
        return self.repo.reserve_stock(branch_id, medicine_id, quantity)

    def commit_inventory(self, branch_id: str, medicine_id: str, batch_id: str, quantity: int) -> dict:
        """Commit reserved stock, decrementing the actual quantity."""
        return self.repo.commit_reserved_stock(branch_id, medicine_id, batch_id, quantity)

    def release_inventory(self, branch_id: str, medicine_id: str, batch_id: str, quantity: int) -> dict:
        """Release reserved stock, removing the reservation hold."""
        return self.repo.release_reserved_stock(branch_id, medicine_id, batch_id, quantity)

    def find_nearest_branch_with_stock(
        self,
        current_branch_id: str,
        medicine_id: str,
    ) -> dict | None:
        """
        Search the entire network for branches that have stock.
        Returns the branch with the highest available quantity (nearest proxy).
        """
        results = self.repo.find_stock_across_network(medicine_id, current_branch_id)

        if not results:
            logger.warning(
                f"No stock found anywhere in the network for medicine {medicine_id}"
            )
            return None

        # Return the branch with the most stock (best candidate)
        best = results[0]
        logger.info(
            f"Best stock source: branch={best.get('branch_id')}, qty={best.get('quantity')}"
        )
        return best

    def get_branch_inventory(
        self,
        branch_id: str,
        offset: int = 0,
        limit: int = 50,
    ) -> list[dict]:
        """Paginated inventory listing for a branch."""
        return self.repo.get_branch_inventory(branch_id, offset, limit)
