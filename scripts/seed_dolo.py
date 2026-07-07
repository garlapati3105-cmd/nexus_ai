import sys
import os
from uuid import UUID

# Add apps/api to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "apps", "api")))

try:
    from app.core.database import get_supabase
except ImportError:
    # fallback for execution context paths
    sys.path.append(os.path.abspath("apps/api"))
    from app.core.database import get_supabase

db = get_supabase()

def run_seeding():
    print("Connecting to Supabase to run Dolo medicine seeding...")
    
    # 1. Fetch category id
    cat_res = db.table("medicine_categories").select("id").eq("name", "Analgesics").execute()
    if cat_res.data:
        category_id = cat_res.data[0]["id"]
    else:
        # Fallback to first category
        cat_fallback = db.table("medicine_categories").select("id").limit(1).execute()
        category_id = cat_fallback.data[0]["id"] if cat_fallback.data else None

    # Fetch manufacturer id
    mfr_res = db.table("manufacturers").select("id").limit(1).execute()
    manufacturer_id = mfr_res.data[0]["id"] if mfr_res.data else None

    # Dolo identifiers
    dolo_med_id = "d010c650-d010-4010-b010-101010101010"
    dolo_batch_id = "dbab4e50-dbab-4bab-abab-babababababa"

    # Insert medicine
    med_check = db.table("medicines").select("id").eq("id", dolo_med_id).execute()
    if not med_check.data:
        db.table("medicines").insert({
            "id": dolo_med_id,
            "category_id": category_id,
            "manufacturer_id": manufacturer_id,
            "sku": "SKU-DOLO-650",
            "substance_name": "Paracetamol",
            "brand_name": "Dolo 650mg",
            "dosage_form": "Tablet",
            "strength": "650mg",
            "requires_prescription": False
        }).execute()
        print("Success: Inserted Dolo 650mg medicine record.")
    else:
        print("Dolo 650mg medicine record already exists.")

    # Insert price
    price_check = db.table("medicine_prices").select("id").eq("medicine_id", dolo_med_id).execute()
    if not price_check.data:
        db.table("medicine_prices").insert({
            "medicine_id": dolo_med_id,
            "branch_id": None,
            "mrp": 30.00,
            "purchase_price": 18.00,
            "discount_percentage": 0.00,
            "is_active": True
        }).execute()
        print("Success: Inserted Dolo price config (MRP 30, Cost 18).")
    else:
        print("Dolo price config already exists.")

    # Insert batch
    batch_check = db.table("medicine_batches").select("id").eq("id", dolo_batch_id).execute()
    if not batch_check.data:
        db.table("medicine_batches").insert({
            "id": dolo_batch_id,
            "medicine_id": dolo_med_id,
            "batch_number": "BAT-DOLO-000",
            "manufacturing_date": "2025-01-01",
            "expiry_date": "2027-12-31"
        }).execute()
        print("Success: Inserted Dolo active batch BAT-DOLO-000 (expires 2027-12-31).")
    else:
        print("Dolo batch record already exists.")

    # Get branches
    branches_res = db.table("branches").select("id").execute()
    branches = branches_res.data or []

    # Insert/update stock levels to 150
    for b in branches:
        bid = b["id"]
        inv_check = db.table("inventory").select("id").eq("branch_id", bid).eq("batch_id", dolo_batch_id).execute()
        if not inv_check.data:
            db.table("inventory").insert({
                "branch_id": bid,
                "medicine_id": dolo_med_id,
                "batch_id": dolo_batch_id,
                "quantity": 150,
                "reserved_quantity": 0,
                "reorder_level": 15,
                "max_level": 300
            }).execute()
            print(f"Seeded 150 Dolo units for branch {bid}.")
        else:
            db.table("inventory").update({
                "quantity": 150,
                "reserved_quantity": 0
            }).eq("branch_id", bid).eq("batch_id", dolo_batch_id).execute()
            print(f"Updated inventory quantity to 150 Dolo units for branch {bid}.")

    print("Dolo medicine stock seeding completed successfully!")

if __name__ == "__main__":
    run_seeding()
