import boto3

s3 = boto3.client('s3', region_name='ap-northeast-1')
BUCKET_NAME = "billnote-storage-exceldata"

async def upload_file_to_s3(file_obj):
    # ファイルオブジェクトから名前を取得（io.BytesIOなどの場合）
    file_key = f"invoices/{getattr(file_obj, 'name', 'unnamed.xlsx')}" 
    s3.upload_fileobj(file_obj, BUCKET_NAME, file_key)
    return f"s3://{BUCKET_NAME}/{file_key}"

def generate_download_url(s3_path: str):
    """s3://bucket/key の形式からバケット名とキーを分離して取得する"""
    path_parts = s3_path.replace("s3://", "").split("/", 1)
    bucket = path_parts[0]
    key = path_parts[1]
    
    response = s3.get_object(Bucket=bucket, Key=key)
    # ファイルの中身と、パスの最後（ファイル名）を返す
    return response['Body'].read(), key.split("/")[-1]