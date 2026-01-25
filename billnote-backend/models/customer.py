from pydantic import BaseModel

class Customer(BaseModel):
    name : str
    address : str | None = None
    phone : str | None = None
    