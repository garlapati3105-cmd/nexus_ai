"""
Nexus AI — Customer Repository
Real Supabase operations for: customers, customer_prescriptions.
"""
from __future__ import annotations
from app.repositories.base import BaseRepository
from app.core.logging import get_logger
from app.core.exceptions import DatabaseOperationException

logger = get_logger("repository.customer")


class CustomerRepository(BaseRepository):
    TABLE_NAME = "customers"

    def get_customer_with_prescriptions(self, customer_id: str) -> dict | None:
        """Fetch customer alongside their active prescriptions."""
        try:
            customer = self.find_by_id(customer_id)
            prescriptions = (
                self.db.table("customer_prescriptions")
                .select("*")
                .eq("customer_id", customer_id)
                .order("prescription_date", desc=True)
                .limit(5)
                .execute()
            )
            customer["prescriptions"] = prescriptions.data or []
            return customer
        except Exception as e:
            logger.error(f"get_customer_with_prescriptions failed: {e}")
            raise DatabaseOperationException("get_customer_with_prescriptions", str(e))

    def search_customers(self, query_text: str, limit: int = 20) -> list[dict]:
        """Search customers by name, phone, or email."""
        try:
            result = (
                self.db.table(self.TABLE_NAME)
                .select("*")
                .or_(
                    f"first_name.ilike.%{query_text}%,"
                    f"last_name.ilike.%{query_text}%,"
                    f"phone.ilike.%{query_text}%,"
                    f"email.ilike.%{query_text}%"
                )
                .limit(limit)
                .execute()
            )
            return result.data or []
        except Exception as e:
            logger.error(f"search_customers failed: {e}")
            raise DatabaseOperationException("search_customers", str(e))

    def update_loyalty_points(self, customer_id: str, points_to_add: int) -> dict:
        """Increment a customer's loyalty points."""
        try:
            customer = self.find_by_id(customer_id)
            current = customer.get("loyalty_points", 0)
            return self.update(customer_id, {"loyalty_points": current + points_to_add})
        except Exception as e:
            logger.error(f"update_loyalty_points failed: {e}")
            raise DatabaseOperationException("update_loyalty_points", str(e))
