"""
Nexus AI — Central API Router
Mounts all endpoint routers with their prefixes and tags.
"""
from fastapi import APIRouter
from app.api.endpoints import orders, inventory, transfers, approvals, invoices, dashboard, workflow, pharmacist, cashier

api_router = APIRouter()
api_router.include_router(orders.router, prefix="/orders", tags=["Orders"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["Inventory"])
api_router.include_router(transfers.router, prefix="/transfers", tags=["Transfers"])
api_router.include_router(approvals.router, prefix="/approvals", tags=["Approvals"])
api_router.include_router(invoices.router, prefix="/invoices", tags=["Invoices"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(workflow.router, prefix="/workflow", tags=["Workflow"])
api_router.include_router(pharmacist.router, prefix="/pharmacist", tags=["Pharmacist"])
api_router.include_router(cashier.router, prefix="/cashier", tags=["Cashier"])
