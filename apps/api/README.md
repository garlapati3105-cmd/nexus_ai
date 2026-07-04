
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
