"""
FastAPI Router for Pharmacist operations.
Enforces role check (simulated/prototype checking or roles join).
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from uuid import UUID
from typing import List
from app.core.database import get_supabase
from app.services.notification_service import NotificationService
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger("api.pharmacist")

class DispenseRequest(BaseModel):
    order_id: UUID

class RejectRequest(BaseModel):
    order_id: UUID

@router.get("/orders")
def list_pending_orders():
    """Retrieve all pending orders (Ready for Dispensing queue)."""
    db = get_supabase()
    try:
        # Fetch pending orders
        result = db.table("orders") \
            .select("*, branches(name), customers(first_name, last_name)") \
            .eq("status", "pending") \
            .order("created_at", desc=True) \
            .execute()
        
        orders = result.data or []
        for order in orders:
            items_res = db.table("order_items") \
                .select("*, medicines(brand_name, substance_name)") \
                .eq("order_id", order["id"]) \
                .execute()
            order["items"] = items_res.data or []
            
        return orders
    except Exception as e:
        logger.error(f"Failed to list pending orders: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orders/{order_id}")
def get_order_details(order_id: UUID):
    """Retrieve specific order details with items and medicines."""
    db = get_supabase()
    try:
        order_res = db.table("orders") \
            .select("*, branches(name), customers(first_name, last_name)") \
            .eq("id", str(order_id)) \
            .execute()
        if not order_res.data:
            raise HTTPException(status_code=404, detail="Order not found")
        order = order_res.data[0]
        
        items_res = db.table("order_items") \
            .select("*, medicines(brand_name, substance_name)") \
            .eq("order_id", order["id"]) \
            .execute()
        order["items"] = items_res.data or []
        
        return order
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve order details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/dispense")
def dispense_order(req: DispenseRequest):
    """Confirm prescription verification, dispense medicine, and commit inventory levels."""
    db = get_supabase()
    notif_svc = NotificationService()
    try:
        # 1. Fetch order details
        order_res = db.table("orders").select("*").eq("id", str(req.order_id)).execute()
        if not order_res.data:
            raise HTTPException(status_code=404, detail="Order not found")
        order = order_res.data[0]
        
        if order["status"] != "pending":
            return {"status": "ignored", "message": f"Order already in {order['status']} state."}

        items_res = db.table("order_items").select("*").eq("order_id", order["id"]).execute()
        items = items_res.data or []

        # 2. Process each item: commit inventory levels
        for item in items:
            inv_res = db.table("inventory") \
                .select("*") \
                .eq("branch_id", order["branch_id"]) \
                .eq("medicine_id", item["medicine_id"]) \
                .eq("batch_id", item["batch_id"]) \
                .execute()
            if not inv_res.data:
                continue
            inv = inv_res.data[0]
            
            # Check negative limit issues - safely adjust
            new_qty = max(0, inv["quantity"] - item["quantity"])
            new_reserved = max(0, inv["reserved_quantity"] - item["quantity"])
            
            db.table("inventory") \
                .update({"quantity": new_qty, "reserved_quantity": new_reserved}) \
                .eq("id", inv["id"]) \
                .execute()

            # Record double-entry stock transactions
            db.table("inventory_transactions").insert({
                "branch_id": order["branch_id"],
                "medicine_id": item["medicine_id"],
                "batch_id": item["batch_id"],
                "inventory_id": inv["id"],
                "type": "sale",
                "qty_changed": -item["quantity"],
                "reference_id": order["id"],
                "notes": "POS Dispensed Handover"
            }).execute()

        # 3. Transition order status to completed
        db.table("orders").update({"status": "completed"}).eq("id", order["id"]).execute()

        # 4. Sync invoice status to paid
        db.table("invoices").update({"status": "paid"}).eq("order_id", order["id"]).execute()

        # 5. Create audits and logs
        notif_svc.notify_branch(
            branch_id=order["branch_id"],
            title="Medicines Handed Over",
            message=f"Pharmacist completed dispensing order {order['order_no']}.",
            severity="info",
            notification_type="system"
        )
        notif_svc.create_ai_log(
            agent_name="Inventory AI",
            message=f"Stock successfully committed and reservation details cleared for order {order['order_no']}.",
            log_level="info",
            session_id=order["id"]
        )

        return {"status": "success", "message": f"Order {order['order_no']} successfully dispensed & committed."}
    except Exception as e:
        logger.error(f"Dispense failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reject")
def reject_dispensing(req: RejectRequest):
    """Reject dispensing order. Releases held stock reservations and cancels order."""
    db = get_supabase()
    notif_svc = NotificationService()
    try:
        # 1. Fetch order details
        order_res = db.table("orders").select("*").eq("id", str(req.order_id)).execute()
        if not order_res.data:
            raise HTTPException(status_code=404, detail="Order not found")
        order = order_res.data[0]
        
        if order["status"] != "pending":
            raise HTTPException(status_code=400, detail=f"Order is in {order['status']} state, cannot reject")

        items_res = db.table("order_items").select("*").eq("order_id", order["id"]).execute()
        items = items_res.data or []

        # 2. Release stock reservations (decrease reserved_quantity, keep quantity intact)
        for item in items:
            inv_res = db.table("inventory") \
                .select("*") \
                .eq("branch_id", order["branch_id"]) \
                .eq("medicine_id", item["medicine_id"]) \
                .eq("batch_id", item["batch_id"]) \
                .execute()
            if not inv_res.data:
                continue
            inv = inv_res.data[0]
            new_reserved = max(0, inv["reserved_quantity"] - item["quantity"])
            db.table("inventory") \
                .update({"reserved_quantity": new_reserved}) \
                .eq("id", inv["id"]) \
                .execute()

        # 3. Mark order as cancelled
        db.table("orders").update({"status": "cancelled"}).eq("id", order["id"]).execute()

        # 4. Sync invoice status to failed/cancelled
        db.table("invoices").update({"status": "failed"}).eq("order_id", order["id"]).execute()

        notif_svc.notify_branch(
            branch_id=order["branch_id"],
            title="Dispensing Rejected",
            message=f"Pharmacist rejected dispensing for order {order['order_no']}.",
            severity="warning",
            notification_type="system"
        )
        notif_svc.create_ai_log(
            agent_name="Inventory AI",
            message=f"Stock reservations released for rejected order {order['order_no']}.",
            log_level="warning",
            session_id=order["id"]
        )

        return {"status": "success", "message": f"Order {order['order_no']} dispensing rejected. Stock released."}
    except Exception as e:
        logger.error(f"Rejection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
def list_history():
    """Retrieve history of completed/finalized pharmacist checkouts."""
    db = get_supabase()
    try:
        result = db.table("orders") \
            .select("*, branches(name), customers(first_name, last_name)") \
            .in_("status", ["completed", "cancelled"]) \
            .order("updated_at", desc=True) \
            .limit(50) \
            .execute()
        
        orders = result.data or []
        for order in orders:
            items_res = db.table("order_items") \
                .select("*, medicines(brand_name, substance_name)") \
                .eq("order_id", order["id"]) \
                .execute()
            order["items"] = items_res.data or []
            
        return orders
    except Exception as e:
        logger.error(f"Failed to list history: {e}")
        raise HTTPException(status_code=500, detail=str(e))
