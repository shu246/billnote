from fastapi import FastAPI
from routers.upload import router as upload_router

app = FastAPI()

# ファイルアップロードのAPIルーターのみを登録
app.include_router(upload_router)