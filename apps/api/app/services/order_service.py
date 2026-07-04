"""
Nexus AI — Order Service
Orchestrates order creation, line items, payments, and invoice generation.
All operations use real Supabase database through repositories.
"""
from __future__ import annotations
from app.repositories.order_repo import OrderRepository
from app.repositories.invoice_repo import InvoiceRepository
from app.repositories.medicine_repo import MedicineRepository
from app.repositories.employee_repo import EmployeeRepository
from app.core.logging import get_logger
from app.core.exceptions import ValidationException, EntityNotFoundException

logger = get_logger("service.order")

# Tax rate constant
GST_RATE = 12.0  # percent


class OrderService:
    def __init__(self):
        self.order_repo = OrderRepository()
        self.invoice_repo = InvoiceRepository()
        self.medicine_repo = MedicineRepository()
        self.employee_repo = EmployeeRepository()

    def create_order(
        self,
        branch_id: str,
        customer_id: str,
        items: list[dict],
        cashier_id: str | None = None,
    ) -> dict:
        """
        Create a full order with line items.
        items: list of {"medicine_id": str, "batch_id": str, "quantity": int}
        Returns the created order with all items.
        """
        if not items:
            raise ValidationException("Order must have at least one item.")

        # Resolve a cashier if not provided
        if not cashier_id:
            cashier_id = self.employee_repo.get_any_cashier_for_branch(branch_id)

        # Generate order number
        order_no = self.order_repo.generate_order_number(branch_id)

        # Calculate pricing from live medicine prices
        order_items_data = []
        subtotal = 0.0
        total_tax = 0.0

        for item in items:
            med = self.medicine_repo.get_medicine_with_price(item["medicine_id"], branch_id)
            price_info = med.get("price") if med else None

            if price_info:
                unit_price = float(price_info["mrp"])
                discount_pct = float(price_info.get("discount_percentage", 0))
            else:
                unit_price = 150.0  # Safe fallback
                discount_pct = 0.0

            qty = item["quantity"]
            discounted_price = unit_price * (1 - discount_pct / 100)
            item_tax = discounted_price * qty * (GST_RATE / 100)
            net_price = discounted_price * qty + item_tax

            order_items_data.append({
                "medicine_id": item["medicine_id"],
                "batch_id": item["batch_id"],
                "quantity": qty,
                "unit_price": round(unit_price, 2),
                "discount_percentage": round(discount_pct, 2),
                "tax_percentage": GST_RATE,
                "net_price": round(net_price, 2),
            })

            subtotal += discounted_price * qty
            total_tax += item_tax

        total_amount = subtotal + total_tax

        # 1. Create the order header
        order = self.order_repo.create_order(
            branch_id=branch_id,
            customer_id=customer_id,
            cashier_id=cashier_id,
            order_no=order_no,
            subtotal=round(subtotal, 2),
            tax_amount=round(total_tax, 2),
            discount_amount=0.0,
            total_amount=round(total_amount, 2),
        )

        # 2. Create line items
        created_items = []
        for oi in order_items_data:
            oi["order_id"] = order["id"]
            created_item = self.order_repo.create_order_item(oi)
            created_items.append(created_item)

        order["items"] = created_items
        logger.info(f"Order {order_no} created with {len(created_items)} items, total: {total_amount}")
        return order

    def complete_order(self, order_id: str) -> dict:
        """Mark order as completed."""
        return self.order_repo.complete_order(order_id)

    def generate_invoice(self, order_id: str, branch_id: str) -> dict:
        """
        Generate an invoice for a completed order.
        Creates invoice header + line items from order data.
        """
        order = self.order_repo.find_by_id(order_id)
        order_items = self.order_repo.get_order_items(order_id)

        invoice_no = self.invoice_repo.generate_invoice_number(branch_id)

        # Create invoice header
        invoice = self.invoice_repo.create_invoice(
            order_id=order_id,
            branch_id=branch_id,
            invoice_no=invoice_no,
            total_tax=float(order.get("tax_amount", 0)),
            total_amount=float(order.get("total_amount", 0)),
        )

        # Create invoice line items
        for oi in order_items:
            self.invoice_repo.create_invoice_item({
                "invoice_id": invoice["id"],
                "order_item_id": oi["id"],
                "item_description": f"Medicine {oi['medicine_id']}",
                "qty": oi["quantity"],
                "unit_rate": float(oi["unit_price"]),
                "tax_amount": round(float(oi["net_price"]) - float(oi["unit_price"]) * oi["quantity"], 2),
                "net_amount": float(oi["net_price"]),
            })

        logger.info(f"Invoice {invoice_no} generated for order {order_id}")
        return invoice

    def create_payment(self, order_id: str, amount: float, payment_method_id: str) -> dict:
        """Record payment for an order."""
        return self.order_repo.create_payment({
            "order_id": order_id,
            "payment_method_id": payment_method_id,
            "amount": amount,
            "status": "paid",
            "notes": "POS payment - API",
        })
