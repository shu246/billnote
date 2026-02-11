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
    if not phone or phone == "None":
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
    # 1. invoice_id を自動生成
    invoice_id = str(uuid.uuid4())
    
    # 2. 既存顧客のチェック
    phone = str(extracted_data.get('phone', ""))
    existing_id = get_existing_customer_id(phone)
    
    if existing_id:
        customer_id = existing_id
    else:
        # 新規顧客の場合、連絡先があればID発行、なければ "0"
        address = str(extracted_data.get('address', ""))
        customer_id = str(uuid.uuid4()) if (phone and phone != "None") or (address and address != "None") else "0"

    # 3. 日付データの整形（年-月）
    invoice_month = f"{year_val}-{str(month_val).zfill(2)}"

    # 4. DynamoDB保存データの作成
    item = {
        'invoice_id': invoice_id,
        'customer_id': customer_id,
        'customer_name': str(extracted_data['customer_name']),
        'address': str(extracted_data['address']) if extracted_data['address'] else "",
        'phone': phone if phone != "None" else "",
        'invoice_month': invoice_month, # YYYY-MM
        'year': year_val,
        'month': month_val,
        'total_amount': int(extracted_data['total_amount']) if extracted_data['total_amount'] else 0,
        's3_path': s3_path,
        'created_at': datetime.now().isoformat()
    }

    # 5. DynamoDBへ書き込み
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
    # 顧客名インデックスを使って、その人のその月のデータを検索
    response = table.query(
        IndexName='CustomerNameIndex',
        KeyConditionExpression=Key('customer_name').eq(customer_name),
        # フィルタリングで月と金額を絞り込む
        FilterExpression='invoice_month = :m AND total_amount = :a',
        ExpressionAttributeValues={
            ':m': invoice_month,
            ':a': total_amount
        }
    )
    return response.get('Items', []) # 存在すればリストが返る