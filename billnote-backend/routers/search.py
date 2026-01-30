# routers/search.py

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
from services.invoice_service import search_invoices_by_customer, search_invoices_by_month
from services.s3_service import generate_download_url
import io
import urllib.parse

router = APIRouter()

@router.get("/search/customer")
async def get_by_customer(name: str = Query(..., description="検索したい顧客名")):
    results = search_invoices_by_customer(name)
    return {"results": results}

@router.get("/search/month")
async def get_by_month(
    year: int = Query(..., ge=2000), 
    month: int = Query(..., ge=1, le=12)
):
    try:
        # 保存形式に合わせて "YYYY-MM" に変換
        month_str = f"{year}-{str(month).zfill(2)}" # zfillで確実に2桁にする
        results = search_invoices_by_month(month_str)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"検索エラー: {str(e)}")
    
@router.get("/search/customer_id")
async def get_by_customer_id(customer_id: str = Query(..., description="検索したい顧客ID")):
    # invoice_serviceに後述する新しい関数を呼び出す
    from services.invoice_service import search_invoices_by_customer_id
    results = search_invoices_by_customer_id(customer_id)
    return {"results": results}

@router.get("/download")
async def download_invoice(s3_path: str = Query(..., description="s3://... のフルパス")):
    try:
        file_content, file_name = generate_download_url(s3_path)
        
        # ファイル名をURLエンコード（日本語ファイル名対策）
        encoded_filename = urllib.parse.quote(file_name)

        return StreamingResponse(
            io.BytesIO(file_content),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={encoded_filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ダウンロードエラー: {str(e)}")