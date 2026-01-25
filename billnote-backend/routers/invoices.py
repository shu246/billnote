from fastapi import APIRouter
from models.invoice import Invoice
from services.invoice_service import create_invoice, list_invoices

router = APIRouter()

# 請求書登録API
@router.post("/invoices")
def create_invoice_api(invoice: Invoice):
    result = create_invoice(invoice)
    return {
        "status": "ok",
        "data": result
    }

# 請求書一覧API
@router.get("/invoices")
def list_invoices_api():
    return list_invoices()
