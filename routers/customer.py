from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
# DynamoDPの処理が入っているinvoice_serviceをインポート
from services.invoice_service import update_invoice_customer_info

router = APIRouter()

# 送られてデータの形を定義
class UpdateCustomerRequest(BaseModel):
    invoice_id: str
    address: str
    phone: str

# 窓口を定義
@router.post("/update-customer")
def update_customer_info(req: UpdateCustomerRequest):
    try:
        # 読み込んだ関数に届いたデータを引き渡す
        update_invoice_customer_info(
            invoice_id = req.invoice_id,
            address = req.address,
            phone = req.phone
        )
        return {"status": "success", "message": "正常に更新されました"}
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))