"""
Nexus AI — Analytics Service
Updates dashboard metrics, revenue tracking using real database.
"""
from __future__ import annotations
from app.repositories.analytics_repo import AnalyticsRepository
from app.core.logging import get_logger

logger = get_logger("service.analytics")


class AnalyticsService:
    def __init__(self):
        self.repo = AnalyticsRepository()

    def record_sale(
        self,
        branch_id: str,
        total_amount: float,
        items_sold: int,
    ) -> None:
        """Record a sale into daily metrics and revenue tables."""
        try:
            self.repo.upsert_daily_metrics(
                branch_id=branch_id,
                sales_amount=total_amount,
                transaction_count=1,
                items_sold=items_sold,
            )
            self.repo.upsert_revenue(branch_id, total_amount)
            logger.info(f"Sale recorded: branch={branch_id}, amount={total_amount}")
        except Exception as e:
            # Analytics is non-critical; don't crash the order
            logger.warning(f"Analytics recording failed (non-fatal): {e}")

    def record_stockout(self, branch_id: str) -> None:
        """Increment the stockout counter for today."""
        try:
            self.repo.increment_stockout(branch_id)
        except Exception as e:
            logger.warning(f"Stockout recording failed (non-fatal): {e}")

    def record_ai_decision(self, branch_id: str) -> None:
        """Increment the AI decisions counter for today."""
        try:
            self.repo.increment_ai_decision(branch_id)
        except Exception as e:
            logger.warning(f"AI decision recording failed (non-fatal): {e}")

    def get_dashboard_summary(self, branch_id: str | None = None) -> dict:
        """Get aggregated dashboard summary."""
        return self.repo.get_dashboard_summary(branch_id)
