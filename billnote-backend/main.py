from fastapi import FastAPI
from routers.upload import router as upload_router
from routers.search import router as search_router

app = FastAPI()

# ファイルアップロードのAPIルーターのみを登録
app.include_router(upload_router)
app.include_router(search_router)