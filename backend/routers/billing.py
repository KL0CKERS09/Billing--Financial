from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from dependencies import supabase, get_current_user

router = APIRouter(prefix="/billing", tags=["billing"])

class ServiceItem(BaseModel):
    name: str
    price: float

class MedicineItem(BaseModel):
    inventory_id: int
    name: str
    qty: int
    unit_price: float

class CreateBillingRequest(BaseModel):
    consultation_id: int
    service_items: List[ServiceItem]
    medicine_items: List[MedicineItem]
    service_fee: float
    medicine_fee: float
    other_fees: float = 0
    receipt_no: str


@router.get("/consultations")
async def billing_consultations(user=Depends(get_current_user)):
    result = supabase.table("CONSULTATIONS").select("""
        id, ConsultationNumber, Date, Diagnosis, Status, patient_id, owner_id,
        PATIENTS ( id, Name, Species, Breed, Age ),
        OWNERS   ( id, FirstName, LastName, PhoneNumber, Address )
    """).order("created_at", desc=True).execute()
    return result.data


@router.get("/inventory")
async def billing_inventory(category: str = None, user=Depends(get_current_user)):
    query = supabase.table("INVENTORY").select(
        "id, Name, UnitPrice, Unit, Stock, Category"
    ).gt("Stock", 0)
    if category:
        query = query.eq("Category", category)
    result = query.order("Name").execute()
    return result.data


@router.post("/create", status_code=201)
async def create_billing(body: CreateBillingRequest, user=Depends(get_current_user)):

    existing = supabase.table("BILLING") \
        .select("id, Status") \
        .eq("consultation_id", body.consultation_id) \
        .execute()

    if existing.data:
        raise HTTPException(
            status_code=409,
            detail=f"A billing record already exists for this consultation. Billing ID: {existing.data[0]['id']}"
        )

    billing_result = supabase.table("BILLING").insert({
        "consultation_id": body.consultation_id,
        "ServiceFee":      body.service_fee,
        "MedicineFee":     body.medicine_fee,
        "OtherFees":       body.other_fees,
        "Status":          "Paid",
        "ReceiptNo":       body.receipt_no,
    }).execute()

    if not billing_result.data:
        raise HTTPException(500, "Failed to create billing record")

    billing_id = billing_result.data[0]["id"]

    for svc in body.service_items:
        supabase.table("BILLING_ITEMS").insert({
            "billing_id":  billing_id,
            "type":        "service",
            "description": svc.name,
            "unit_price":  svc.price,
            "quantity":    1,
            "subtotal":    svc.price,
        }).execute()

    for med in body.medicine_items:
        supabase.table("BILLING_ITEMS").insert({
            "billing_id":  billing_id,
            "type":        "medicine",
            "description": med.name,
            "unit_price":  med.unit_price,
            "quantity":    med.qty,
            "subtotal":    med.unit_price * med.qty,
        }).execute()
        current = supabase.table("INVENTORY").select("Stock").eq("id", med.inventory_id).execute()
        if current.data:
            new_stock = max(0, int(current.data[0]["Stock"]) - med.qty)
            supabase.table("INVENTORY").update({"Stock": new_stock}).eq("id", med.inventory_id).execute()

    supabase.table("CONSULTATIONS").update({"Status": "Billed"}).eq("id", body.consultation_id).execute()
    return {"message": "Billing created successfully", "billing_id": billing_id}


@router.get("")
async def get_billing(
    page: int = 1,
    limit: int = 10,
    status: Optional[str] = None,
    user=Depends(get_current_user)
):
    query = supabase.table("BILLING").select("""
        id, ServiceFee, MedicineFee, OtherFees, SubTotal, VAT, TotalAmount, Status, created_at,
        CONSULTATIONS (
            ConsultationNumber, Date, Diagnosis,
            PATIENTS ( Name, Breed ),
            OWNERS   ( FirstName, LastName, PhoneNumber )
        )
    """)
    if status:
        query = query.eq("Status", status)
    result = query.order("created_at", desc=True) \
                  .range((page - 1) * limit, page * limit - 1) \
                  .execute()
    return result.data


@router.patch("/{billing_id}/status")
async def update_billing_status(billing_id: int, body: dict, user=Depends(get_current_user)):
    new_status = body.get("status")
    if new_status not in ("Pending", "Paid", "Cancelled"):
        raise HTTPException(400, "Invalid status")
    supabase.table("BILLING").update({"Status": new_status}).eq("id", billing_id).execute()
    if new_status == "Paid":
        billing = supabase.table("BILLING").select("consultation_id").eq("id", billing_id).execute()
        if billing.data:
            supabase.table("CONSULTATIONS").update({"Status": "Billed"}) \
                .eq("id", billing.data[0]["consultation_id"]).execute()
    return {"message": "Status updated"}


@router.get("/{billing_id}")
async def get_billing_record(billing_id: int, user=Depends(get_current_user)):
    result = supabase.table("BILLING").select("""
        id, ServiceFee, MedicineFee, OtherFees, SubTotal, VAT, TotalAmount, Status, ReceiptNo, created_at,
        CONSULTATIONS (
            ConsultationNumber, Date, Diagnosis, Notes,
            PATIENTS ( Name, Species, Breed ),
            OWNERS   ( FirstName, LastName, PhoneNumber, Address )
        ),
        BILLING_ITEMS ( type, description, unit_price, quantity, subtotal )
    """).eq("id", billing_id).single().execute()
    return result.data