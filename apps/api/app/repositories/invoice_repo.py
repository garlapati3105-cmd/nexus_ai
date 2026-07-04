"""
Nexus AI — Invoice Repository
Real Supabase operations for: invoices, invoice_items.
"""
from __future__ import annotations
from typing import Any
from app.repositories.base import BaseRepository
from app.core.logging import get_logger
from app.core.exceptions import DatabaseOperationException

logger = get_logger("repository.invoice")


class InvoiceRepository(BaseRepository):
    TABLE_NAME = "invoices"

    def create_invoice(
        self,
        order_id: str,
        branch_id: str,
        invoice_no: str,
        total_tax: float,
        total_amount: float,
    ) -> dict:
        """Insert an invoice linked to an order."""
        data = {
            "order_id": order_id,
            "branch_id": branch_id,
            "invoice_no": invoice_no,
            "total_tax": total_tax,
            "total_amount": total_amount,
            "status": "paid",
        }
        return self.create(data)

    def create_invoice_item(self, item_data: dict[str, Any]) -> dict:
        """Insert an invoice_items row."""
        try:
            result = self.db.table("invoice_items").insert(item_data).execute()
            if result.data:
                return result.data[0]
            raise DatabaseOperationException("create_invoice_item", "No data returned")
        except DatabaseOperationException:
            raise
        except Exception as e:
            logger.error(f"create_invoice_item failed: {e}")
            raise DatabaseOperationException("create_invoice_item", str(e))

    def get_invoice_by_order(self, order_id: str) -> dict | None:
        """Fetch the invoice associated with a specific order."""
        try:
            result = (
                self.db.table(self.TABLE_NAME)
                .select("*")
                .eq("order_id", order_id)
                .execute()
            )
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"get_invoice_by_order failed: {e}")
            raise DatabaseOperationException("get_invoice_by_order", str(e))

    def generate_invoice_number(self, branch_id: str) -> str:
        """Generate the next sequential invoice number."""
        try:
            result = (
                self.db.table(self.TABLE_NAME)
                .select("invoice_no")
                .eq("branch_id", branch_id)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
            if result.data:
                last_no = result.data[0]["invoice_no"]
                seq = int(last_no.split("-")[-1]) + 1
            else:
                seq = 1
            return f"INV-NEX-{seq:08d}"
        except Exception as e:
            logger.error(f"generate_invoice_number failed: {e}")
            import uuid
            return f"INV-NEX-{uuid.uuid4().hex[:8].upper()}"
