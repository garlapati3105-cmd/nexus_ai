import os
import pathlib

BASE_DIR = pathlib.Path(__file__).parent / "app"

# Directory structure
DIRS = [
    "api/endpoints",
    "core",
    "services",
    "repositories",
    "schemas",
    "models" # If needed
]

for d in DIRS:
    (BASE_DIR / d).mkdir(parents=True, exist_ok=True)

# ----------------- SCHEMAS -----------------
schema_file = BASE_DIR / "schemas" / "workflow.py"
schema_file.write_text("""
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID

class OrderRequest(BaseModel):
    customer_id: UUID
    branch_id: UUID
    medicine_id: UUID
    quantity: int

class InventoryCheck(BaseModel):
    branch_id: UUID
    medicine_id: UUID
    quantity: int

class TransferProposal(BaseModel):
    from_branch_id: UUID
    to_branch_id: UUID
    medicine_id: UUID
    quantity: int
    cost: float

class ApprovalRequest(BaseModel):
    transfer_id: UUID
    approved: bool
    approved_by: UUID
""")

# ----------------- REPOSITORIES -----------------
repo_base = BASE_DIR / "repositories"

repo_base.joinpath("base.py").write_text("""
class BaseRepository:
    def __init__(self, db_session=None):
        self.db = db_session
""")

repo_base.joinpath("order_repo.py").write_text("""
from .base import BaseRepository
import uuid

class OrderRepository(BaseRepository):
    def create_order(self, customer_id: uuid.UUID, branch_id: uuid.UUID, total: float):
        # MOCK
        return {"id": uuid.uuid4(), "status": "completed"}
""")

repo_base.joinpath("inventory_repo.py").write_text("""
from .base import BaseRepository
import uuid

class InventoryRepository(BaseRepository):
    def check_stock(self, branch_id: uuid.UUID, medicine_id: uuid.UUID) -> int:
        # Mocking 0 for a specific medicine to trigger the transfer workflow, otherwise 100
        # For simplicity, we just return a dict depending on the workflow
        pass
        
    def reserve_stock(self, branch_id: uuid.UUID, medicine_id: uuid.UUID, quantity: int):
        return True
""")

repo_base.joinpath("transfer_repo.py").write_text("""
from .base import BaseRepository
import uuid

class TransferRepository(BaseRepository):
    def create_transfer(self, from_branch, to_branch, medicine_id, quantity):
        return {"transfer_id": uuid.uuid4(), "status": "pending_approval"}
        
    def update_status(self, transfer_id, status):
        return {"transfer_id": transfer_id, "status": status}
""")

# ----------------- SERVICES -----------------
svc_base = BASE_DIR / "services"

svc_base.joinpath("order_service.py").write_text("""
from app.repositories.order_repo import OrderRepository

class OrderService:
    def __init__(self):
        self.repo = OrderRepository()
        
    def generate_invoice(self, order_id):
        # mock
        return {"invoice_id": "INV-12345"}
        
    def complete_order(self, customer_id, branch_id, quantity):
        return self.repo.create_order(customer_id, branch_id, quantity * 10)
""")

svc_base.joinpath("inventory_service.py").write_text("""
from app.repositories.inventory_repo import InventoryRepository
import uuid

class InventoryService:
    def check_local_inventory(self, branch_id: uuid.UUID, medicine_id: uuid.UUID, required_qty: int) -> bool:
        # For the sake of the mock, let's say if quantity > 10 we return False to trigger the transfer flow
        if required_qty > 10:
            return False
        return True
        
    def reserve_inventory(self, branch_id: uuid.UUID, medicine_id: uuid.UUID, quantity: int):
        return True
        
    def find_nearest_branch_with_stock(self, current_branch: uuid.UUID, medicine_id: uuid.UUID):
        # Mock nearest branch
        return uuid.uuid4()
""")

svc_base.joinpath("finance_service.py").write_text("""
class FinanceService:
    def calculate_transfer_cost(self, from_branch, to_branch, quantity):
        return 15.00
""")

svc_base.joinpath("approval_service.py").write_text("""
class ApprovalService:
    def request_approval(self, transfer_id):
        return {"approval_req_id": "APP-111", "status": "pending"}
""")

svc_base.joinpath("notification_service.py").write_text("""
class NotificationService:
    def notify_branch(self, branch_id, message):
        pass
        
    def create_ai_log(self, action, details):
        pass
""")

svc_base.joinpath("analytics_service.py").write_text("""
class AnalyticsService:
    def update_dashboard(self, data):
        pass
""")

svc_base.joinpath("transfer_service.py").write_text("""
from app.repositories.transfer_repo import TransferRepository

class TransferService:
    def __init__(self):
        self.repo = TransferRepository()
        
    def create_transfer_proposal(self, from_branch, to_branch, medicine_id, quantity):
        return self.repo.create_transfer(from_branch, to_branch, medicine_id, quantity)
        
    def execute_transfer(self, transfer_id):
        return self.repo.update_status(transfer_id, "approved_and_shipped")
""")

svc_base.joinpath("workflow_service.py").write_text("""
from app.services.order_service import OrderService
from app.services.inventory_service import InventoryService
from app.services.transfer_service import TransferService
from app.services.finance_service import FinanceService
from app.services.approval_service import ApprovalService
from app.services.notification_service import NotificationService
from app.services.analytics_service import AnalyticsService

class WorkflowService:
    def __init__(self):
        self.order_svc = OrderService()
        self.inv_svc = InventoryService()
        self.transfer_svc = TransferService()
        self.finance_svc = FinanceService()
        self.approval_svc = ApprovalService()
        self.notif_svc = NotificationService()
        self.analytics_svc = AnalyticsService()
        
    def process_purchase(self, customer_id, branch_id, medicine_id, quantity):
        # Sales AI Validates (Mocked)
        ai_validation = True
        self.notif_svc.create_ai_log("Sales AI Validation", "Order validated")
        
        # Check inventory
        has_stock = self.inv_svc.check_local_inventory(branch_id, medicine_id, quantity)
        
        if has_stock:
            # Reserve
            self.inv_svc.reserve_inventory(branch_id, medicine_id, quantity)
            # Create Order
            order = self.order_svc.complete_order(customer_id, branch_id, quantity)
            # Invoice
            invoice = self.order_svc.generate_invoice(order['id'])
            
            self.analytics_svc.update_dashboard({"order": order})
            self.notif_svc.create_ai_log("Inventory AI", "Stock reserved locally")
            self.notif_svc.notify_branch(branch_id, "Order completed locally")
            
            return {"status": "completed_locally", "order": order, "invoice": invoice}
        else:
            # Branch out of stock, regional AI triggers
            self.notif_svc.create_ai_log("Regional AI", "Stock not found locally, checking network")
            nearest_branch = self.inv_svc.find_nearest_branch_with_stock(branch_id, medicine_id)
            
            # Inventory AI Recommends Transfer
            self.notif_svc.create_ai_log("Inventory AI", f"Recommend transfer from {nearest_branch}")
            
            # Finance calculations
            cost = self.finance_svc.calculate_transfer_cost(nearest_branch, branch_id, quantity)
            
            # Proposal & Transfer
            transfer = self.transfer_svc.create_transfer_proposal(nearest_branch, branch_id, medicine_id, quantity)
            
            # Approval
            approval = self.approval_svc.request_approval(transfer['transfer_id'])
            
            self.analytics_svc.update_dashboard({"transfer": transfer})
            self.notif_svc.notify_branch(branch_id, "Transfer proposal generated, awaiting approval")
            
            return {
                "status": "transfer_proposed",
                "transfer": transfer,
                "approval": approval,
                "cost": cost
            }
""")

# ----------------- ENDPOINTS -----------------
api_base = BASE_DIR / "api" / "endpoints"

api_base.joinpath("orders.py").write_text("""
from fastapi import APIRouter
from app.schemas.workflow import OrderRequest
from app.services.workflow_service import WorkflowService

router = APIRouter()
workflow_svc = WorkflowService()

@router.post("/")
def create_order(request: OrderRequest):
    result = workflow_svc.process_purchase(
        request.customer_id,
        request.branch_id,
        request.medicine_id,
        request.quantity
    )
    return result
""")

api_base.joinpath("inventory.py").write_text("""
from fastapi import APIRouter
import uuid

router = APIRouter()

@router.get("/check")
def check_inventory(branch_id: uuid.UUID, medicine_id: uuid.UUID):
    return {"stock": 10}

@router.get("/network")
def check_network(medicine_id: uuid.UUID):
    return {"branches": []}
""")

api_base.joinpath("transfers.py").write_text("""
from fastapi import APIRouter
from app.services.transfer_service import TransferService

router = APIRouter()
svc = TransferService()

@router.post("/")
def create_transfer():
    return {"status": "created"}
""")

api_base.joinpath("approvals.py").write_text("""
from fastapi import APIRouter
from app.schemas.workflow import ApprovalRequest
from app.services.transfer_service import TransferService

router = APIRouter()
svc = TransferService()

@router.post("/")
def approve_transfer(req: ApprovalRequest):
    if req.approved:
        res = svc.execute_transfer(req.transfer_id)
        # Usually logic to finalize order & invoice here
        return {"status": "approved_and_executed", "data": res}
    return {"status": "rejected"}
""")

api_base.joinpath("invoices.py").write_text("""
from fastapi import APIRouter

router = APIRouter()

@router.post("/")
def create_invoice():
    return {"invoice": "mock_invoice"}
""")

api_base.joinpath("dashboard.py").write_text("""
from fastapi import APIRouter

router = APIRouter()

@router.get("/summary")
def get_dashboard_summary():
    return {"sales": 1000, "transfers": 2}
""")

api_base.joinpath("workflow.py").write_text("""
from fastapi import APIRouter
import uuid

router = APIRouter()

@router.get("/{id}")
def get_workflow_status(id: uuid.UUID):
    return {"workflow_id": id, "status": "completed"}
""")

# ----------------- MAIN API ROUTER -----------------
(BASE_DIR / "api" / "router.py").write_text("""
from fastapi import APIRouter
from app.api.endpoints import orders, inventory, transfers, approvals, invoices, dashboard, workflow

api_router = APIRouter()
api_router.include_router(orders.router, prefix="/orders", tags=["Orders"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["Inventory"])
api_router.include_router(transfers.router, prefix="/transfers", tags=["Transfers"])
api_router.include_router(approvals.router, prefix="/approvals", tags=["Approvals"])
api_router.include_router(invoices.router, prefix="/invoices", tags=["Invoices"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(workflow.router, prefix="/workflow", tags=["Workflow"])
""")

# ----------------- MAIN APP -----------------
(BASE_DIR / "main.py").write_text("""
from fastapi import FastAPI
from app.api.router import api_router

app = FastAPI(title="Nexus AI Backend - Enterprise Workflow API")
app.include_router(api_router)
""")

# ----------------- REQUIREMENTS -----------------
(BASE_DIR.parent / "requirements.txt").write_text("""
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.2
""")

# ----------------- DOCS -----------------
(BASE_DIR.parent / "README.md").write_text("""
# Nexus AI - Backend Workflow
## Sales & Transfer Enterprise Architecture

This backend implements the core workflow for medicine purchase and inter-branch transfer when out of stock.

### Services implemented:
- OrderService
- InventoryService
- TransferService
- FinanceService
- ApprovalService
- WorkflowService
- AnalyticsService
- NotificationService

### To run:
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```
""")

print("Successfully built the backend enterprise structure.")
