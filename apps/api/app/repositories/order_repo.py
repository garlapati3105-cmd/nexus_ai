"""
Nexus AI — Order Repository
Real Supabase operations for: orders, order_items, payments, invoices, invoice_items.
"""
from __future__ import annotations
from typing import Any
from app.repositories.base import BaseRepository
from app.core.logging import get_logger
from app.core.exceptions import DatabaseOperationException

logger = get_logger("repository.order")


class OrderRepository(BaseRepository):
    TABLE_NAME = "orders"

    def create_order(
        self,
        branch_id: str,
        customer_id: str,
        cashier_id: str | None,
        order_no: str,
        subtotal: float,
        tax_amount: float,
        discount_amount: float,
        total_amount: float,
    ) -> dict:
        """Insert into orders table and return the created row."""
        data = {
            "branch_id": branch_id,
            "customer_id": customer_id,
            "cashier_id": cashier_id,
            "order_no": order_no,
            "subtotal": subtotal,
            "tax_amount": tax_amount,
            "discount_amount": discount_amount,
            "total_amount": total_amount,
            "status": "pending",
        }
        return self.create(data)

    def create_order_item(self, item_data: dict[str, Any]) -> dict:
        """Insert a single order_item row."""
        try:
            result = self.db.table("order_items").insert(item_data).execute()
            if result.data:
                return result.data[0]
            raise DatabaseOperationException("create_order_item", "No data returned")
        except DatabaseOperationException:
            raise
        except Exception as e:
            logger.error(f"create_order_item failed: {e}")
            raise DatabaseOperationException("create_order_item", str(e))

    def create_payment(self, payment_data: dict[str, Any]) -> dict:
        """Insert a payment record against an order."""
        try:
            result = self.db.table("payments").insert(payment_data).execute()
            if result.data:
                return result.data[0]
            raise DatabaseOperationException("create_payment", "No data returned")
        except DatabaseOperationException:
            raise
        except Exception as e:
            logger.error(f"create_payment failed: {e}")
            raise DatabaseOperationException("create_payment", str(e))

    def complete_order(self, order_id: str) -> dict:
        """Update order status to 'completed'."""
        return self.update(order_id, {"status": "completed"})

    def get_orders_by_branch(
        self,
        branch_id: str,
        status: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> list[dict]:
        """Fetch orders for a branch with optional status filter."""
        filters: dict[str, Any] = {"branch_id": branch_id}
        if status:
            filters["status"] = status
        return self.list(filters=filters, offset=offset, limit=limit)

    def get_order_items(self, order_id: str) -> list[dict]:
        """Fetch all line items for an order."""
        try:
            result = self.db.table("order_items").select("*").eq("order_id", order_id).execute()
            return result.data or []
        except Exception as e:
            logger.error(f"get_order_items failed: {e}")
            raise DatabaseOperationException("get_order_items", str(e))

    def generate_order_number(self, branch_id: str) -> str:
        """Generate the next sequential order number for a branch."""
        try:
            result = (
                self.db.table("orders")
                .select("order_no")
                .eq("branch_id", branch_id)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
            if result.data:
                last_no = result.data[0]["order_no"]
                seq = int(last_no.split("-")[-1]) + 1
            else:
                seq = 1
            return f"ORD-{seq:08d}"
        except Exception as e:
            logger.error(f"generate_order_number failed: {e}")
            import uuid
            return f"ORD-{uuid.uuid4().hex[:8].upper()}"
