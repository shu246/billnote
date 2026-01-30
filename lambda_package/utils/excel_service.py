import openpyxl
from io import BytesIO

def extract_excel_data(file_content: bytes):
    # メモリ上のバイナリデータからエクセルを読み込む
    wb = openpyxl.load_workbook(filename=BytesIO(file_content), data_only=True)
    sheet = wb.active  # 一番左のシートを取得

    # 抽出したい項目を指定
    extracted = {
        "customer_name": sheet["A5"].value,  # 顧客名
        "address": sheet["C42"].value,       # 住所
        "phone": sheet["C44"].value,         # 電話番号
        "total_amount": sheet["H32"].value   # 合計金額
    }

    # 「様」の削除などの加工処理
    if extracted["customer_name"] and isinstance(extracted["customer_name"], str):
        extracted["customer_name"] = extracted["customer_name"].replace("様", "").strip()

    return extracted