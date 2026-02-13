import boto3
import uuid
from datetime import datetime
from boto3.dynamodb.conditions import Key

# AWS設定
dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')
table = dynamodb.Table('Invoices') # DynamoDBテーブル名

def get_existing_customer_id(phone: str):
    """
    GSI(PhoneIndex)を使用して、電話番号から既存の顧客IDを高速検索する
    """
    # 電話番号が None, 空文字, または文字列の "None" の場合は検索しない
    if not phone or phone == "None" or phone == "":
        return None

    # GSIを使ってクエリを実行
    response = table.query(
        IndexName='PhoneIndex',
        KeyConditionExpression=Key('phone').eq(str(phone))
    )
    
    items = response.get('Items', [])
    if items:
        # 既に見つかった場合は、その顧客IDを使い回す
        return items[0]['customer_id']
    
    return None

def create_invoice_record(extracted_data: dict, year_val: int, month_val: int, s3_path: str):
    """
    請求書情報をDynamoDBに保存し、顧客の名寄せも行う
    """
    # 1. invoice_id を自動生成（この請求書固有のID）
    invoice_id = str(uuid.uuid4())
    
    # 2. 電話番号の取得と判定
    # excel_service.py で設定した "None" を受け取る
    phone = str(extracted_data.get('phone', "None")).strip()
    
    # --- 顧客ID（customer_id）の決定ロジック ---
    if phone == "None" or phone == "":
        # 電話番号がない場合は一律で顧客IDを「0」にする
        customer_id = "0"
    else:
        # 電話番号がある場合、既存の顧客がいるかチェック
        existing_id = get_existing_customer_id(phone)
        if existing_id:
            customer_id = existing_id
        else:
            # 新規顧客（電話番号はあるが初登録）なら新しいUUIDを発行
            customer_id = str(uuid.uuid4())

    # 3. データの整形
    invoice_month = f"{year_val}-{str(month_val).zfill(2)}"
    
    # 保存するデータの作成
    item = {
        'invoice_id': invoice_id,
        'customer_id': customer_id,
        'customer_name': extracted_data.get('customer_name', "名称未設定"),
        'address': extracted_data.get('address', ""),
        'phone': phone,
        'total_amount': int(extracted_data.get('total_amount', 0)),
        's3_path': s3_path,
        'invoice_month': invoice_month,
        'created_at': datetime.now().isoformat()
    }

    # 4. DynamoDBへ書き込み
    table.put_item(Item=item)
    return item

def search_invoices_by_customer(customer_name: str):
    """顧客名で検索"""
    response = table.query(
        IndexName='CustomerNameIndex',
        KeyConditionExpression=Key('customer_name').eq(customer_name)
    )
    return response.get('Items', [])

def search_invoices_by_month(invoice_month: str):
    """年月で検索"""
    response = table.query(
        IndexName='DateSearchIndex',
        KeyConditionExpression=Key('invoice_month').eq(invoice_month)
    )
    return response.get('Items', [])

def search_invoices_by_customer_id(customer_id: str):
    """顧客IDで検索 (CustomerIDIndexを使用)"""
    response = table.query(
        IndexName='CustomerIDIndex',
        KeyConditionExpression=Key('customer_id').eq(customer_id)
    )
    return response.get('Items', [])

def check_duplicate_invoice(customer_name: str, invoice_month: str, total_amount: int):
    """同じ顧客、同じ月、同じ金額のデータがあるかチェックする"""
    response = table.query(
        IndexName='CustomerNameIndex',
        KeyConditionExpression=Key('customer_name').eq(customer_name)
    )
    
    items = response.get('Items', [])
    # 同名顧客の中で、月と金額が一致するものがあるか絞り込み
    duplicates = [
        item for item in items 
        if item.get('invoice_month') == invoice_month and int(item.get('total_amount')) == total_amount
    ]
    return duplicates