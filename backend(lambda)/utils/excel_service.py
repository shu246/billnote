import openpyxl
import re
from io import BytesIO

def extract_excel_data(file_content: bytes):
    # メモリ上のバイナリデータからエクセルを読み込む
    wb = openpyxl.load_workbook(filename=BytesIO(file_content), data_only=True)
    sheet = wb.active  # 一番左のシートを取得

    # 電話番号のデータ取得
    raw_phone = sheet["C44"].value
    
    # 電話番号の判定
    if raw_phone:
        phone = str(raw_phone).strip()
    else:
        phone = "None"

    extracted = {
        "customer_name": sheet["A5"].value,  # 顧客名
        "address": sheet["C42"].value,       # 住所
        "phone": phone,                      # 電話番号
        "total_amount": sheet["H32"].value   # 合計金額
    }

    # 顧客名の加工処理
    if extracted["customer_name"] and isinstance(extracted["customer_name"], str):
        name = extracted["customer_name"]
        
        # 様と空白を削除
        name = name.replace("様", "")
        
        # 全角スペースと半角スペースをすべて削除
        name = re.sub(r'[\s　]+', '', name)
        
        extracted["customer_name"] = name

    # 合計金額の空チェック
    if extracted["total_amount"] is None:
        extracted["total_amount"] = 0

    return extracted