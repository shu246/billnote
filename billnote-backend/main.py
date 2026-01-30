from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from mangum import Mangum
from routers.upload import router as upload_router
from routers.search import router as search_router
import os

app = FastAPI()

# ファイルアップロードのAPIルーターのみを登録
app.include_router(upload_router)
app.include_router(search_router)

# --- フロントエンドとの接続設定 ---

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. まず同じ階層の static を探す (Lambda/デプロイ用)
# 2. なければ一つ上の階層を探す (ローカル開発用)
static_path = os.path.join(BASE_DIR, "static")
if not os.path.exists(static_path):
    static_path = os.path.join(BASE_DIR, "..", "billnote-frontend", "static")

app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(static_path, "index.html"))

handler = Mangum(app)