"""
GET /dashboard/summary — Returns real aggregated dashboard data.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.services.analytics_service import AnalyticsService
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger("api.dashboard")


@router.get("/summary")
def get_dashboard_summary(branch_id: Optional[str] = Query(None, description="Optional branch filter")):
    """Get aggregated dashboard metrics for today."""
    try:
        svc = AnalyticsService()
        return svc.get_dashboard_summary(branch_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Dashboard summary failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
