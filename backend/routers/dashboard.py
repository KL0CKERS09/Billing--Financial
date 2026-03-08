from fastapi import APIRouter, Depends
from dependencies import supabase, get_current_user
from datetime import date
router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats")
async def dashboard_stats(user=Depends(get_current_user)):
    total_c     = supabase.table("CONSULTATIONS").select("id", count="exact").execute()
    pending_b   = supabase.table("BILLING").select("id", count="exact").eq("Status", "Pending").execute()
    completed_b = supabase.table("BILLING").select("id", count="exact").eq("Status", "Paid").execute()
    revenue_r   = supabase.table("BILLING").select("TotalAmount", "VAT").eq("Status", "Paid").execute()

    total_revenue = sum(float(r["TotalAmount"] or 0) for r in revenue_r.data)
    total_vat     = sum(float(r["VAT"] or 0)         for r in revenue_r.data)
    total_tx      = len(revenue_r.data)

    return {
        "total_consultations": total_c.count or 0,
        "pending_billing":     pending_b.count or 0,
        "completed_billing":   completed_b.count or 0,
        "total_revenue":       round(total_revenue, 2),
        "total_transactions":  total_tx,
        "avg_transaction":     round(total_revenue / total_tx, 2) if total_tx else 0,
        "total_vat_collected": round(total_vat, 2),
    }


@router.get("/consultations")
async def recent_consultations(limit: int = 10, user=Depends(get_current_user)):
    result = supabase.table("CONSULTATIONS").select("""
        id, ConsultationNumber, Date, Diagnosis, Status,
        PATIENTS ( Name, Breed, Species ),
        OWNERS   ( FirstName, LastName, PhoneNumber )
    """).order("created_at", desc=True).limit(limit).execute()
    return result.data


@router.get("/admin-stats")
async def admin_stats(user=Depends(get_current_user)):
    today = date.today().isoformat()

    owners_all   = supabase.table("OWNERS").select("id, created_at").execute()
    total_owners = len(owners_all.data)
    this_month   = date.today().replace(day=1).isoformat()
    owners_diff  = sum(1 for o in owners_all.data if o.get("created_at","") >= this_month)

    patients_all = supabase.table("PATIENTS").select("id, Species").execute()
    total_patients = len(patients_all.data)
    dog_count = sum(1 for p in patients_all.data if (p.get("Species") or "").lower() == "dog")
    cat_count = sum(1 for p in patients_all.data if (p.get("Species") or "").lower() == "cat")

    appts = supabase.table("APPOINTMENTS").select("id, Status") \
        .eq("AppointmentDate", today).execute()
    today_appts = len(appts.data)
    confirmed   = sum(1 for a in appts.data if a.get("Status") == "Confirmed")
    waiting     = sum(1 for a in appts.data if a.get("Status") == "Waiting")
    cancelled   = sum(1 for a in appts.data if a.get("Status") == "Cancelled")
    
    low_stock = supabase.table("INVENTORY").select("id") \
        .lte("Stock", 10).gt("Stock", 0).execute()
    low_stock_count = len(low_stock.data)

    from datetime import timedelta
    in_7_days = (date.today() + timedelta(days=7)).isoformat()
    expiring = supabase.table("INVENTORY").select("id") \
        .lte("ExpiryDate", in_7_days) \
        .gte("ExpiryDate", today).execute()
    expiring_count = len(expiring.data) if expiring.data else 0

    billing_today = supabase.table("BILLING").select(
        "TotalAmount, created_at"
    ).eq("Status", "Paid").gte("created_at", today + "T00:00:00").execute()
    today_revenue = sum(float(b.get("TotalAmount") or 0) for b in billing_today.data)

    yesterday = (date.today() - timedelta(days=1)).isoformat()
    billing_yesterday = supabase.table("BILLING").select(
        "TotalAmount, created_at"
    ).eq("Status", "Paid") \
     .gte("created_at", yesterday + "T00:00:00") \
     .lt("created_at", today + "T00:00:00").execute()
    yesterday_revenue = sum(float(b.get("TotalAmount") or 0) for b in billing_yesterday.data)
    revenue_diff = round(
        ((today_revenue - yesterday_revenue) / yesterday_revenue * 100) if yesterday_revenue else 0, 1
    )

    audit_logs = supabase.table("AUDIT_LOGS").select("""
        id, Action, Module, Details, Icon, created_at,
        USERS ( FirstName, LastName )
    """).order("created_at", desc=True).limit(10).execute()

    expenses = supabase.table("EXPENSES").select("*") \
        .gte("created_at", today + "T00:00:00") \
        .order("created_at", desc=True).execute()

    return {
        "stats": {
            "totalOwners":       total_owners,
            "ownersDiff":        owners_diff,
            "totalPatients":     total_patients,
            "dogCount":          dog_count,
            "catCount":          cat_count,
            "todayAppointments": today_appts,
            "confirmed":         confirmed,
            "waiting":           waiting,
            "cancelled":         cancelled,
            "lowStock":          low_stock_count,
            "expiringMeds":      expiring_count,
            "todayRevenue":      today_revenue,
            "revenueDiff":       revenue_diff,
        },
        "audit_logs": audit_logs.data or [],
        "expenses":   expenses.data or [],
    }

@router.get("/audit-logs")
async def get_audit_logs(user=Depends(get_current_user)):
    result = supabase.table("AUDIT_LOGS").select("""
        id, Action, Module, Details, Icon, created_at,
        USERS ( FirstName, LastName )
    """).order("created_at", desc=True).limit(200).execute()
    return result.data or []


@router.get("/all-expenses")
async def get_all_expenses(user=Depends(get_current_user)):
    result = supabase.table("EXPENSES").select("*") \
        .order("created_at", desc=True).limit(200).execute()
    return result.data or []