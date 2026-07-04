"""
Nexus AI — Medicine Repository
Real Supabase operations for: medicines, medicine_batches, medicine_prices.
"""
from __future__ import annotations
from app.repositories.base import BaseRepository
from app.core.logging import get_logger
from app.core.exceptions import DatabaseOperationException

logger = get_logger("repository.medicine")


class MedicineRepository(BaseRepository):
    TABLE_NAME = "medicines"

    def get_medicine_with_price(self, medicine_id: str, branch_id: str | None = None) -> dict | None:
        """
        Fetch a medicine with its active price.
        Checks branch-specific price first, falls back to global (branch_id IS NULL).
        """
        try:
            medicine = self.find_by_id(medicine_id)

            # Try branch-specific price first
            price_result = None
            if branch_id:
                price_result = (
                    self.db.table("medicine_prices")
                    .select("*")
                    .eq("medicine_id", medicine_id)
                    .eq("branch_id", branch_id)
                    .eq("is_active", True)
                    .limit(1)
                    .execute()
                )

            # Fallback to global price
            if not price_result or not price_result.data:
                price_result = (
                    self.db.table("medicine_prices")
                    .select("*")
                    .eq("medicine_id", medicine_id)
                    .is_("branch_id", "null")
                    .eq("is_active", True)
                    .limit(1)
                    .execute()
                )

            medicine["price"] = price_result.data[0] if price_result and price_result.data else None
            return medicine
        except Exception as e:
            logger.error(f"get_medicine_with_price failed: {e}")
            raise DatabaseOperationException("get_medicine_with_price", str(e))

    def get_batches_for_medicine(self, medicine_id: str) -> list[dict]:
        """Fetch all batches for a medicine, sorted by expiry (FEFO)."""
        try:
            result = (
                self.db.table("medicine_batches")
                .select("*")
                .eq("medicine_id", medicine_id)
                .order("expiry_date", desc=False)
                .execute()
            )
            return result.data or []
        except Exception as e:
            logger.error(f"get_batches_for_medicine failed: {e}")
            raise DatabaseOperationException("get_batches_for_medicine", str(e))

    def search_medicines(self, query_text: str, limit: int = 20) -> list[dict]:
        """Search medicines by brand name, substance name, or SKU."""
        try:
            result = (
                self.db.table(self.TABLE_NAME)
                .select("*")
                .or_(
                    f"brand_name.ilike.%{query_text}%,"
                    f"substance_name.ilike.%{query_text}%,"
                    f"sku.ilike.%{query_text}%"
                )
                .limit(limit)
                .execute()
            )
            return result.data or []
        except Exception as e:
            logger.error(f"search_medicines failed: {e}")
            raise DatabaseOperationException("search_medicines", str(e))
