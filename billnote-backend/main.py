from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from routers.upload import router as upload_router
from routers.search import router as search_router
import os

app = FastAPI()

# ファイルアップロードのAPIルーターのみを登録
app.include_router(upload_router)
app.include_router(search_router)

# --- フロントエンドとの接続設定 ---

# index.htmlがある場所を特定する (親フォルダに移動してフロントエンド側を見る)
# main.py の場所を基準にパスを計算
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "billnote-frontend", "static")

# /static というURLで、フロントエンドのstaticフォルダの中身を公開する
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
async def read_index():
    # ブラウザで「/」にアクセスした時に index.html を返す
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))