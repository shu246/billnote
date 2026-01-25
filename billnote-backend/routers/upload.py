from fastapi import APIRouter, File, UploadFile

router = APIRouter()

@router.post("/upload")
async def upload_invoice(file: UploadFile = File(...)):
    contents = await file.read()
    return {"filename": file.filename}
