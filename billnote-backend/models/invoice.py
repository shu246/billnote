from pydantic import BaseModel

class Invoice(BaseModel):
    invoice_number: str
    customer_name: str
    amount: int
    date: str
    