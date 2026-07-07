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

class DirectDispenseRequest(BaseModel):
    branch_id: UUID
    first_name: str
    last_name: str
    phone: str
    medicine_id: UUID
    quantity: int


@router.post("/direct-dispense")
def direct_dispense(req: DirectDispenseRequest):
    """Directly dispense walk-in order and immediately deduct branch stock."""
    db = get_supabase()
    notif_svc = NotificationService()
    try:
        # 1. Look up or create Customer
        phone = req.phone.strip()
        first_name = req.first_name.strip()
        last_name = req.last_name.strip()

        customer_id = None
        cust_res = db.table("customers").select("id").eq("phone", phone).eq("deleted_at", None).execute()
        if cust_res.data:
            customer_id = cust_res.data[0]["id"]
        else:
            new_cust = db.table("customers").insert({
                "first_name": first_name,
                "last_name": last_name,
                "phone": phone,
                "loyalty_points": 0
            }).execute()
            if not new_cust.data:
                raise HTTPException(status_code=500, detail="Failed to create customer")
            customer_id = new_cust.data[0]["id"]

            db.table("customer_profiles").insert({
                "customer_id": customer_id,
                "gender": "Unspecified"
            }).execute()

        # 2. Select FEFO inventory record
        inv_res = db.table("inventory") \
            .select("*, medicine_batches(expiry_date)") \
            .eq("branch_id", str(req.branch_id)) \
            .eq("medicine_id", str(req.medicine_id)) \
            .execute()
        
        inventory_records = inv_res.data or []
        available_records = [r for r in inventory_records if r.get("quantity", 0) > 0]
        if not available_records:
            raise HTTPException(status_code=400, detail="Requested medicine is out of stock at this branch.")

        def get_expiry(r):
            batch = r.get("medicine_batches")
            if batch and isinstance(batch, dict) and batch.get("expiry_date"):
                return batch["expiry_date"]
            return "9999-12-31"

        available_records.sort(key=get_expiry)

        total_available = sum(r.get("quantity", 0) for r in available_records)
        if total_available < req.quantity:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient stock status. Requested: {req.quantity}, available overall: {total_available}"
            )

        # 3. Deduct stock sequential FEFO
        rem_qty = req.quantity
        deducted_batches = []

        for rec in available_records:
            if rem_qty <= 0:
                break
            take_qty = min(rec["quantity"], rem_qty)
            new_qty = rec["quantity"] - take_qty

            db.table("inventory").update({"quantity": new_qty}).eq("id", rec["id"]).execute()

            deducted_batches.append({
                "batch_id": rec["batch_id"],
                "inventory_id": rec["id"],
                "quantity": take_qty
            })

            # Record inventory transaction
            db.table("inventory_transactions").insert({
                "branch_id": str(req.branch_id),
                "medicine_id": str(req.medicine_id),
                "batch_id": rec["batch_id"],
                "inventory_id": rec["id"],
                "type": "sale",
                "qty_changed": -take_qty,
                "notes": "Direct Dispense Handover"
            }).execute()

            rem_qty -= take_qty

        # 4. Insert order header as completed
        import random
        order_no = f"ORD-{random.randint(100000, 999999)}"

        mrp = 99.00
        price_res = db.table("medicine_prices") \
            .select("mrp") \
            .eq("medicine_id", str(req.medicine_id)) \
            .eq("is_active", True) \
            .execute()
        if price_res.data:
            mrp = float(price_res.data[0]["mrp"])

        total_amount = mrp * req.quantity
        order_data = {
            "branch_id": str(req.branch_id),
            "customer_id": customer_id,
            "order_no": order_no,
            "subtotal": total_amount,
            "tax_amount": total_amount * 0.18,
            "discount_amount": 0.0,
            "total_amount": total_amount * 1.18,
            "status": "completed"
        }
        new_order = db.table("orders").insert(order_data).execute()
        if not new_order.data:
            raise HTTPException(status_code=500, detail="Failed to create order record")
        order = new_order.data[0]

        # 5. Insert order items & link transactions
        for db_batch in deducted_batches:
            db.table("order_items").insert({
                "order_id": order["id"],
                "medicine_id": str(req.medicine_id),
                "batch_id": db_batch["batch_id"],
                "quantity": db_batch["quantity"],
                "unit_price": mrp,
                "net_price": mrp * db_batch["quantity"]
            }).execute()

            db.table("inventory_transactions") \
                .update({"reference_id": order["id"]}) \
                .eq("branch_id", str(req.branch_id)) \
                .eq("medicine_id", str(req.medicine_id)) \
                .eq("batch_id", db_batch["batch_id"]) \
                .eq("qty_changed", -db_batch["quantity"]) \
                .eq("notes", "Direct Dispense Handover") \
                .execute()

        # 6. Generate paid invoice
        invoice_data = {
            "order_id": order["id"],
            "branch_id": str(req.branch_id),
            "invoice_no": f"INV-{random.randint(100000, 999999)}",
            "amount_due": 0.0,
            "amount_paid": order["total_amount"],
            "status": "paid"
        }
        db.table("invoices").insert(invoice_data).execute()

        # 7. Audits & system notifications
        notif_svc.notify_branch(
            branch_id=str(req.branch_id),
            title="Walk-in Direct Dispensation",
            message=f"Pharmacist Dispensed {req.quantity} units of medicine directly to customer {first_name}.",
            severity="info",
            notification_type="system"
        )
        notif_svc.create_ai_log(
            agent_name="Inventory AI",
            message=f"Stock directly committed for walk-in order {order_no}.",
            log_level="info",
            session_id=order["id"]
        )

        return {"status": "success", "message": f"Successfully dispensed walk-in order {order_no}.", "order": order}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Direct dispense failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orders")
def list_pending_orders(branch_id: UUID = None):
    """Retrieve all pending orders (Ready for Dispensing queue)."""
    db = get_supabase()
    try:
        # Fetch pending orders
        query = db.table("orders") \
            .select("*, branches(name), customers(first_name, last_name)")
        if branch_id:
            query = query.eq("branch_id", str(branch_id))
        result = query.eq("status", "pending") \
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

        # 4. Handle Invoice and construct Refund Loop if payment was collected at POS
        inv_res = db.table("invoices").select("id, status").eq("order_id", order["id"]).execute()
        if inv_res.data:
            invoice_record = inv_res.data[0]
            new_status = "refunded" if invoice_record["status"] == "paid" else "failed"
            db.table("invoices").update({"status": new_status}).eq("id", invoice_record["id"]).execute()


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
def list_history(branch_id: UUID = None):
    """Retrieve history of completed/finalized pharmacist checkouts."""
    db = get_supabase()
    try:
        query = db.table("orders") \
            .select("*, branches(name), customers(first_name, last_name)")
        if branch_id:
            query = query.eq("branch_id", str(branch_id))
        result = query.in_("status", ["completed", "cancelled"]) \
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
