from fastapi import FastAPI
from routers import customers, invoices
from routers.upload import router as upload_router


app = FastAPI()

# 顧客のAPIルーターを登録
app.include_router(customers.router)

# 請求書のAPIルーターを登録
app.include_router(invoices.router)

# ファイルアップロードのAPIルーターを登録
app.include_router(upload_router)
