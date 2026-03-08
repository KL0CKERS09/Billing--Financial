from fastapi import APIRouter, Depends
from dependencies import supabase, get_current_user

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/financial")
async def financial_report(year: int = None, user=Depends(get_current_user)):
    from datetime import date
    current_year = year or date.today().year

    paid_billing = supabase.table("BILLING") \
        .select("TotalAmount, VAT, ServiceFee, MedicineFee, created_at") \
        .eq("Status", "Paid").execute()

    total_cash_sales = sum(float(r["TotalAmount"] or 0) for r in paid_billing.data)
    total_vat        = sum(float(r["VAT"] or 0)         for r in paid_billing.data)

    monthly: dict = {}
    for r in paid_billing.data:
        if not r["created_at"]: continue
        month = r["created_at"][:7]
        monthly[month] = monthly.get(month, 0) + float(r["TotalAmount"] or 0)

    monthly_sales = [
        {"month": m, "sales": round(v, 2)}
        for m, v in sorted(monthly.items())
    ]

    service_items  = supabase.table("BILLING_ITEMS").select("description, subtotal, quantity").eq("type", "service").execute()
    medicine_items = supabase.table("BILLING_ITEMS").select("description, subtotal, quantity").eq("type", "medicine").execute()

    service_revenue: dict = {}
    for item in service_items.data:
        name = item["description"]
        if name not in service_revenue:
            service_revenue[name] = {"transactions": 0, "sales": 0}
        service_revenue[name]["transactions"] += int(item["quantity"] or 1)
        service_revenue[name]["sales"]        += float(item["subtotal"] or 0)

    medicine_total = sum(float(i["subtotal"] or 0) for i in medicine_items.data)
    medicine_tx    = len(medicine_items.data)

    revenue_breakdown = [
        {"category": k, "transactions": v["transactions"], "sales": round(v["sales"], 2)}
        for k, v in service_revenue.items()
    ]
    if medicine_total > 0:
        revenue_breakdown.append({
            "category": "Medicine Sales",
            "transactions": medicine_tx,
            "sales": round(medicine_total, 2)
        })

    total_cash_revenue = sum(r["sales"] for r in revenue_breakdown)

    expenses_result = supabase.table("EXPENSES").select("Category, Amount").execute()

    expense_map: dict = {}
    for e in expenses_result.data:
        cat = e["Category"]
        expense_map[cat] = expense_map.get(cat, 0) + float(e["Amount"] or 0)

    expense_breakdown = [
        {"category": k, "amount": round(v, 2)}
        for k, v in expense_map.items()
    ]

    total_expenses = sum(e["amount"] for e in expense_breakdown)
    net_profit     = total_cash_sales - total_expenses
    profit_margin  = round((net_profit / total_cash_sales * 100), 1) if total_cash_sales > 0 else 0

    total_consults = supabase.table("CONSULTATIONS").select("id", count="exact").execute()

    return {
        "year": current_year,
        "summary": {
            "total_cash_sales":    round(total_cash_sales, 2),
            "total_expenses":      round(total_expenses, 2),
            "net_cash_profit":     round(net_profit, 2),
            "profit_margin":       profit_margin,
            "total_vat":           round(total_vat, 2),
            "total_consultations": total_consults.count or 0,
        },
        "revenue_breakdown": revenue_breakdown,
        "expense_breakdown": expense_breakdown,
        "monthly_sales":     monthly_sales,
        "totals": {
            "total_cash_revenue": round(total_cash_revenue, 2),
            "total_expenses":     round(total_expenses, 2),
        }
    }


@router.get("/billing-history")
async def billing_history(user=Depends(get_current_user)):
    result = supabase.table("BILLING").select("""
        id, ServiceFee, MedicineFee, OtherFees,
        SubTotal, VAT, TotalAmount, Status, ReceiptNo, created_at,
        CONSULTATIONS (
            ConsultationNumber, Date,
            PATIENTS ( Name, Species, Breed ),
            OWNERS   ( FirstName, LastName )
        )
    """).eq("Status", "Paid") \
       .order("created_at", desc=True) \
       .execute()
    return result.data