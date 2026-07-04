"""
GET /inventory/check — Check stock at a branch.
GET /inventory/network — Search all branches for medicine stock.
"""
from fastapi import APIRouter, HTTPException, Query
from uuid import UUID
from app.services.inventory_service import InventoryService
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger("api.inventory")


@router.get("/check")
def check_inventory(
    branch_id: UUID = Query(..., description="Branch UUID"),
    medicine_id: UUID = Query(..., description="Medicine UUID"),
    quantity: int = Query(1, ge=1, description="Required quantity"),
):
    """Check local stock availability at a specific branch."""
    try:
        svc = InventoryService()
        result = svc.check_local_inventory(str(branch_id), str(medicine_id), quantity)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Inventory check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/network")
def check_network(
    medicine_id: UUID = Query(..., description="Medicine UUID"),
    exclude_branch_id: UUID = Query(None, description="Exclude this branch"),
):
    """Search the entire branch network for stock of a specific medicine."""
    try:
        svc = InventoryService()
        exclude = str(exclude_branch_id) if exclude_branch_id else ""
        results = svc.inv_svc_repo_fallback_network(medicine_id, exclude) if False else None

        # Use the repository directly for network search
        from app.repositories.inventory_repo import InventoryRepository
        repo = InventoryRepository()
        results = repo.find_stock_across_network(str(medicine_id), exclude)
        return {"branches": results, "total_results": len(results)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Network inventory search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
