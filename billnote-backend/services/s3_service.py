import boto3

s3 = boto3.client('s3', region_name='ap-northeast-1')
BUCKET_NAME = "billnote-storage-exceldata"

async def upload_file_to_s3(file_obj): # UploadFileの型指定を外すかAnyにする
    # file_obj.name がファイル名として使われます
    file_key = f"invoices/{file_obj.name}" 
    
    s3.upload_fileobj(
        file_obj,
        BUCKET_NAME,
        file_key
    )
    
    return f"s3://{BUCKET_NAME}/{file_key}"