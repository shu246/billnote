from fastapi import APIRouter
from models.customer import Customer
from services.customer_service import  create_customer, list_customers

router = APIRouter()

# 顧客登録API
@router.post("/customers")
def create_customer_api(customer: Customer):
    result = create_customer(customer)
    return {
        "status": "ok",
        "data": result
    }

@router.get("/customers")
def list_customers():
    return list_customers()
