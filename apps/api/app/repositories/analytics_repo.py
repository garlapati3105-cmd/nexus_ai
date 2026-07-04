"""
Nexus AI — Analytics Repository
Real Supabase operations for: daily_branch_metrics, network_metrics, revenues.
"""
from __future__ import annotations
from app.repositories.base import BaseRepository
from app.core.logging import get_logger
from app.core.exceptions import DatabaseOperationException
from app.core.config import get_settings
from datetime import date

logger = get_logger("repository.analytics")


class AnalyticsRepository(BaseRepository):
    TABLE_NAME = "daily_branch_metrics"

    def upsert_daily_metrics(
        self,
        branch_id: str,
        sales_amount: float = 0.0,
        transaction_count: int = 0,
        items_sold: int = 0,
    ) -> dict:
        """
        Upsert daily branch metrics. Increments values if a row exists for today.
        """
        today = date.today().isoformat()
        try:
            # Check if today's row exists
            existing = (
                self.db.table(self.TABLE_NAME)
                .select("*")
                .eq("branch_id", branch_id)
                .eq("date", today)
                .execute()
            )

            if existing.data:
                row = existing.data[0]
                new_sales = float(row["total_sales"]) + sales_amount
                new_txns = row["total_transactions"] + transaction_count
                new_items = row["items_sold"] + items_sold
                avg_order = new_sales / new_txns if new_txns > 0 else 0.0

                return self.update(row["id"], {
                    "total_sales": new_sales,
                    "total_transactions": new_txns,
                    "items_sold": new_items,
                    "average_order_value": round(avg_order, 2),
                })
            else:
                avg_order = sales_amount / transaction_count if transaction_count > 0 else 0.0
                data = {
                    "branch_id": branch_id,
                    "date": today,
                    "total_sales": sales_amount,
                    "total_transactions": transaction_count,
                    "items_sold": items_sold,
                    "average_order_value": round(avg_order, 2),
                    "stockouts_count": 0,
                    "expiries_detected": 0,
                    "ai_decisions_executed": 0,
                }
                return self.create(data)
        except Exception as e:
            logger.error(f"upsert_daily_metrics failed: {e}")
            raise DatabaseOperationException("upsert_daily_metrics", str(e))

    def increment_stockout(self, branch_id: str) -> None:
        """Increment stockout counter for today's metrics."""
        today = date.today().isoformat()
        try:
            existing = (
                self.db.table(self.TABLE_NAME)
                .select("id, stockouts_count")
                .eq("branch_id", branch_id)
                .eq("date", today)
                .execute()
            )
            if existing.data:
                row = existing.data[0]
                self.update(row["id"], {"stockouts_count": row["stockouts_count"] + 1})
        except Exception as e:
            logger.warning(f"increment_stockout failed (non-fatal): {e}")

    def increment_ai_decision(self, branch_id: str) -> None:
        """Increment AI decision counter for today's metrics."""
        today = date.today().isoformat()
        try:
            existing = (
                self.db.table(self.TABLE_NAME)
                .select("id, ai_decisions_executed")
                .eq("branch_id", branch_id)
                .eq("date", today)
                .execute()
            )
            if existing.data:
                row = existing.data[0]
                self.update(row["id"], {"ai_decisions_executed": row["ai_decisions_executed"] + 1})
        except Exception as e:
            logger.warning(f"increment_ai_decision failed (non-fatal): {e}")

    def get_dashboard_summary(self, branch_id: str | None = None) -> dict:
        """
        Returns aggregated dashboard summary data.
        If branch_id is None, returns network-wide summary.
        """
        today = date.today().isoformat()
        try:
            query = self.db.table(self.TABLE_NAME).select("*").eq("date", today)
            if branch_id:
                query = query.eq("branch_id", branch_id)
            result = query.execute()
            rows = result.data or []

            total_sales = sum(float(r.get("total_sales", 0)) for r in rows)
            total_txns = sum(r.get("total_transactions", 0) for r in rows)
            total_items = sum(r.get("items_sold", 0) for r in rows)
            total_stockouts = sum(r.get("stockouts_count", 0) for r in rows)
            total_ai = sum(r.get("ai_decisions_executed", 0) for r in rows)

            return {
                "date": today,
                "total_sales": total_sales,
                "total_transactions": total_txns,
                "total_items_sold": total_items,
                "total_stockouts": total_stockouts,
                "ai_decisions_executed": total_ai,
                "branches_reporting": len(rows),
            }
        except Exception as e:
            logger.error(f"get_dashboard_summary failed: {e}")
            raise DatabaseOperationException("get_dashboard_summary", str(e))

    def upsert_revenue(self, branch_id: str, amount: float) -> dict:
        """Upsert revenue record for today."""
        today = date.today().isoformat()
        try:
            existing = (
                self.db.table("revenues")
                .select("*")
                .eq("branch_id", branch_id)
                .eq("revenue_date", today)
                .execute()
            )
            if existing.data:
                row = existing.data[0]
                return (
                    self.db.table("revenues")
                    .update({
                        "amount": float(row["amount"]) + amount,
                        "sales_count": row["sales_count"] + 1,
                    })
                    .eq("id", row["id"])
                    .execute()
                ).data[0]
            else:
                return (
                    self.db.table("revenues")
                    .insert({
                        "branch_id": branch_id,
                        "amount": amount,
                        "sales_count": 1,
                        "revenue_date": today,
                    })
                    .execute()
                ).data[0]
        except Exception as e:
            logger.error(f"upsert_revenue failed: {e}")
            raise DatabaseOperationException("upsert_revenue", str(e))
