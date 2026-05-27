from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from routers.upload import router as upload_router
from routers.search import router as search_router
from routers.customer import router as customer_router

app = FastAPI()

# --- CORS設定 ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # すべてのオリジンを許可
    allow_credentials=True,
    allow_methods=["*"],  # すべてのHTTPメソッドを許可
    allow_headers=["*"],  # すべてのヘッダーを許可
)

# ルーターの登録
app.include_router(upload_router, prefix="/billnote-api")
app.include_router(search_router, prefix="/billnote-api")
app.include_router(customer_router, prefix="/billnote-api")

# AWS Lambda用のハンドラー設定
handler = Mangum(app)