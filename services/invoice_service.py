import boto3
import uuid
from datetime import datetime
from boto3.dynamodb.conditions import Key, Attr

# AWS設定
dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')
table = dynamodb.Table('Invoices') # DynamoDBテーブル名

def get_existing_customer_id(phone: str):
    """
    GSI(PhoneIndex)を使用して、電話番号から既存の顧客IDを高速検索する
    (名寄せ機能：既存機能の維持)
    """
    if not phone or phone == "None" or phone == "":
        return None

    response = table.query(
        IndexName='PhoneIndex',
        KeyConditionExpression=Key('phone').eq(str(phone))
    )
    
    items = response.get('Items', [])
    if items:
        return items[0]['customer_id']
    
    return None

def create_invoice_record(extracted_data: dict, year_val: int, month_val: int, s3_path: str):
    """
    請求書情報をDynamoDBに保存し、顧客の名寄せも行う
    (顧客ID:0 の対応を含む)
    """
    invoice_id = str(uuid.uuid4())
    
    # 電話番号が未入力なら "None" になっている想定
    phone = str(extracted_data.get('phone', "None")).strip()
    
    # 電話番号がない場合は顧客IDを「0」にする (追加した仕様)
    if phone == "None" or phone == "":
        customer_id = "0"
    else:
        # 電話番号がある場合、既存の顧客がいるか検索
        existing_id = get_existing_customer_id(phone)
        if existing_id:
            customer_id = existing_id
        else:
            # 新規顧客なら新しいIDを発行
            customer_id = str(uuid.uuid4())

    invoice_month = f"{year_val}-{str(month_val).zfill(2)}"
    
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

    table.put_item(Item=item)
    return item

def search_invoices_by_customer(customer_name: str):
    """
    顧客名で検索 (苗字だけでもヒットするように .contains を使用)
    """
    # 完全一致から部分一致に変更しつつ、全データから検索
    response = table.scan(
        FilterExpression=Attr('customer_name').contains(customer_name)
    )
    return response.get('Items', [])

def search_invoices_by_month(invoice_month: str):
    """
    年月で検索 (既存機能の維持)
    """
    response = table.query(
        IndexName='DateSearchIndex',
        KeyConditionExpression=Key('invoice_month').eq(invoice_month)
    )
    return response.get('Items', [])

def search_invoices_by_customer_id(customer_id: str):
    """
    顧客IDで検索 (既存機能の維持)
    """
    response = table.query(
        IndexName='CustomerIDIndex',
        KeyConditionExpression=Key('customer_id').eq(customer_id)
    )
    return response.get('Items', [])

def check_duplicate_invoice(customer_name: str, invoice_month: str, total_amount: int):
    """
    重複チェック (既存機能の維持)
    """
    # 既存の CustomerNameIndex を使用して高速にクエリ
    response = table.query(
        IndexName='CustomerNameIndex',
        KeyConditionExpression=Key('customer_name').eq(customer_name)
    )
    
    items = response.get('Items', [])
    duplicates = [
        item for item in items 
        if item.get('invoice_month') == invoice_month and int(item.get('total_amount')) == total_amount
    ]
    return duplicates