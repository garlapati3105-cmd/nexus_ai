"""
FastAPI Router for Cashier operations.
Supports POS customer registry search, SKU lookup, order creation & payments.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from uuid import UUID
from typing import List, Optional
from app.core.database import get_supabase
from app.services.order_service import OrderService
from app.services.inventory_service import InventoryService
from app.services.notification_service import NotificationService
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger("api.cashier")

class CustomerCreateRequest(BaseModel):
    first_name: str
    last_name: str
    phone: str
    email: Optional[str] = None
    gender: Optional[str] = "Unspecified"
    date_of_birth: Optional[str] = None
    address: Optional[str] = None

class OrderItemSelect(BaseModel):
    medicine_id: UUID
    batch_id: UUID
    quantity: int = Field(gt=0)

class OrderCreateRequest(BaseModel):
    branch_id: UUID
    customer_id: UUID
    items: List[OrderItemSelect]

class PaymentConfirmRequest(BaseModel):
    order_id: UUID
    payment_method_id: UUID
    amount: float = Field(gt=0)
    transaction_no: Optional[str] = None

@router.get("/customers")
def get_customers(search: Optional[str] = None):
    """Retrieve list of registered customers, optionally filtered by phone or name."""
    db = get_supabase()
    try:
        query = db.table("customers").select("*").eq("deleted_at", None)
        if search:
            # Simple query logic on phone or first_name
            query = query.or_(f"phone.ilike.%{search}%,first_name.ilike.%{search}%")
        result = query.limit(50).execute()
        return result.data or []
    except Exception as e:
        logger.error(f"Failed to fetch customers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/customer")
def create_customer(req: CustomerCreateRequest):
    """Register a new customer and establish their profile."""
    db = get_supabase()
    try:
        # Create Customer
        cus_result = db.table("customers").insert({
            "first_name": req.first_name,
            "last_name": req.last_name,
            "phone": req.phone,
            "email": req.email,
            "loyalty_points": 0
        }).execute()
        
        if not cus_result.data:
            raise HTTPException(status_code=500, detail="Failed to save customer record")
        customer = cus_result.data[0]
        
        # Create Customer Profile
        db.table("customer_profiles").insert({
            "customer_id": customer["id"],
            "gender": req.gender,
            "date_of_birth": req.date_of_birth,
            "address": req.address
        }).execute()
        
        return customer
    except Exception as e:
        logger.error(f"Failed to create customer: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/medicines")
def get_medicines(search: Optional[str] = None, branch_id: Optional[UUID] = None):
    """Query SKUs, MRPS cost, and batch inventory details."""
    db = get_supabase()
    try:
        # Build query for active medicines
        query = db.table("medicines").select("*, medicine_prices(*), medicine_batches(*)")
        if search:
            query = query.or_(f"brand_name.ilike.%{search}%,substance_name.ilike.%{search}%")
        
        med_result = query.limit(50).execute()
        meds = med_result.data or []
        
        # If branch lookup is passed, join with inventory availability
        formatted_meds = []
        for m in meds:
            qty = 0
            matching_batches = m.get("medicine_batches") or []
            # Lookup inventory for branch if provided
            if branch_id and matching_batches:
                batch_ids = [b["id"] for b in matching_batches]
                inv_res = db.table("inventory") \
                    .select("*") \
                    .eq("branch_id", str(branch_id)) \
                    .in_("batch_id", batch_ids) \
                    .execute()
                inv_data = inv_res.data or []
                qty = sum(inv_row.get("quantity", 0) - inv_row.get("reserved_quantity", 0) for inv_row in inv_data)
                
            price_list = m.get("medicine_prices") or []
            mrp = 99.00
            for p in price_list:
                if p["is_active"]:
                    mrp = float(p["mrp"])
                    break
            
            formatted_meds.append({
                "id": m["id"],
                "brand_name": m["brand_name"],
                "substance_name": m["substance_name"],
                "sku": m["sku"],
                "requires_prescription": m["requires_prescription"],
                "strength": m["strength"],
                "mrp": mrp,
                "available_stock": qty,
                "batches": matching_batches
            })
            
        return formatted_meds
    except Exception as e:
        logger.error(f"Failed to query medicines: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/order")
def create_pos_draft_order(req: OrderCreateRequest):
    """Place customer order items and reserve branch inventory stock FEFO."""
    db = get_supabase()
    order_svc = OrderService()
    inv_svc = InventoryService()
    try:
        # 1. FEFO Stock check and Reservation
        for item in req.items:
            # Increments reserved_quantity for this branch, medicine & quantity
            inv_svc.reserve_inventory(
                branch_id=str(req.branch_id),
                medicine_id=str(item.medicine_id),
                quantity=item.quantity
            )
            
        # 2. Formulate items structure for Order Service
        items_payload = []
        for o_item in req.items:
            items_payload.append({
                "medicine_id": str(o_item.medicine_id),
                "batch_id": str(o_item.batch_id),
                "quantity": o_item.quantity
            })
            
        # 3. Create order header
        order = order_svc.create_order(
            branch_id=str(req.branch_id),
            customer_id=str(req.customer_id),
            items=items_payload
        )
        
        return order
    except Exception as e:
        logger.error(f"Draft POS order failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/payment")
def checkout_pos_payment(req: PaymentConfirmRequest):
    """Complete order billing details: generates invoice, saves payment record."""
    db = get_supabase()
    order_svc = OrderService()
    notif_svc = NotificationService()
    try:
        # Create payment record
        payment_data = {
            "order_id": str(req.order_id),
            "payment_method_id": str(req.payment_method_id),
            "amount": req.amount,
            "transaction_no": req.transaction_no or f"TX-{UUID(int=0).hex[:8].upper()}",
            "status": "paid"
        }
        payment = db.table("payments").insert(payment_data).execute()
        
        # Pull order branch info
        order_res = db.table("orders").select("*").eq("id", str(req.order_id)).execute()
        if not order_res.data:
            raise HTTPException(status_code=404, detail="Order not found")
        order = order_res.data[0]
        
        # Generate fiscal invoice
        invoice = order_svc.generate_invoice(order["id"], order["branch_id"])
        
        # Create user notifications (that order is READY_FOR_DISPENSING)
        db.table("notifications").insert({
            "branch_id": order["branch_id"],
            "title": "Payment Completed",
            "message": f"Payment of ₹{req.amount} received for POS Order {order['order_no']}. Ready for dispensing.",
            "type": "system",
            "severity": "info",
            "is_read": False
        }).execute()
        
        return {
            "status": "success",
            "payment": payment.data[0] if payment.data else None,
            "invoice": invoice
        }
    except Exception as e:
        logger.error(f"Payment checkout failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orders")
def list_today_orders(branch_id: Optional[UUID] = None):
    """Fetch today's orders list for terminal audit."""
    db = get_supabase()
    try:
        query = db.table("orders").select("*, customers(first_name, last_name)")
        if branch_id:
            query = query.eq("branch_id", str(branch_id))
        result = query.order("created_at", desc=True).limit(50).execute()
        return result.data or []
    except Exception as e:
        logger.error(f"Failed to count cashier transactions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orders/{order_id}")
def get_cashier_order_details(order_id: UUID):
    """Retrieve detailed invoices and checkouts by order ID."""
    db = get_supabase()
    try:
        order_res = db.table("orders").select("*, customers(*), branches(*)").eq("id", str(order_id)).execute()
        if not order_res.data:
            raise HTTPException(status_code=404, detail="Order not found")
        order = order_res.data[0]
        
        items_res = db.table("order_items").select("*, medicines(*)").eq("order_id", order["id"]).execute()
        order["items"] = items_res.data or []
        
        pay_res = db.table("payments").select("*").eq("order_id", order["id"]).execute()
        order["payments"] = pay_res.data or []
        
        inv_res = db.table("invoices").select("*").eq("order_id", order["id"]).execute()
        order["invoice"] = inv_res.data[0] if inv_res.data else None
        
        return order
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cashier details failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
def list_cashier_history(branch_id: Optional[UUID] = None):
    """Fetch list of completed history orders."""
    return list_today_orders(branch_id)
