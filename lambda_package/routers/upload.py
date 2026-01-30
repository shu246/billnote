from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from utils.excel_service import extract_excel_data
from services.s3_service import upload_file_to_s3
from services.invoice_service import create_invoice_record, check_duplicate_invoice 
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
        
        # --- 1. エクセル解析 ---
        extracted = extract_excel_data(file_content)
        
        # --- 2. 重複チェックを追加！ ---
        invoice_month = f"{year}-{str(month).zfill(2)}"
        duplicates = check_duplicate_invoice(
            customer_name=extracted['customer_name'],
            invoice_month=invoice_month,
            total_amount=int(extracted['total_amount'])
        )
        
        # もし既に同じデータがあれば、ここで処理を止める
        if duplicates:
            raise HTTPException(
                status_code=400, 
                detail=f"重複エラー: {extracted['customer_name']}様の{invoice_month}（{extracted['total_amount']}円）は既に登録されています。"
            )

        # --- 3. S3へ保存（重複がない場合のみ実行される） ---
        file_obj = io.BytesIO(file_content)
        file_obj.name = file.filename
        s3_path = await upload_file_to_s3(file_obj)
        
        # --- 4. DynamoDBへ保存 ---
        saved_item = create_invoice_record(
            extracted_data=extracted,
            year_val=year,
            month_val=month,
            s3_path=s3_path
        )
        
        return {"status": "success", "data": saved_item}

    except HTTPException as e:
        # 400エラー（重複など）をそのまま返す
        raise e
    except Exception as e:
        # それ以外の予期せぬエラー
        raise HTTPException(status_code=500, detail=str(e))