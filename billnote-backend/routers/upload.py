from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from utils.excel_service import extract_excel_data
from services.s3_service import upload_file_to_s3
from services.invoice_service import create_invoice_record
import io

router = APIRouter()

@router.post("/upload")
async def upload_invoice(
    file: UploadFile = File(...),
    year: int = Form(...),
    month: int = Form(...)
):
    try:
        # 先にファイルの中身をメモリに読み込む
        file_content = await file.read()
        
        # --- 1. S3へ保存 ---
        # 読み込んだバイナリデータをio.BytesIOでファイル形式に見せかけて渡す
        file_obj = io.BytesIO(file_content)
        file_obj.name = file.filename # S3側でファイル名が必要なため
        s3_path = await upload_file_to_s3(file_obj)
        
        # --- 2. エクセル解析 ---
        extracted = extract_excel_data(file_content)
        
        # --- 3. DynamoDBへ保存 ---
        saved_item = create_invoice_record(
            extracted_data=extracted,
            year_val=year,
            month_val=month,
            s3_path=s3_path
        )
        
        return {"status": "success", "data": saved_item}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))