from fastapi import FastAPI, APIRouter, Request, UploadFile, File, HTTPException
from pathlib import Path
import shutil
import zipfile
import os
from utils.gemini import GeminiPDFExtractor

router = APIRouter()

base_dir = os.path.dirname(os.path.abspath(__file__)) 
file_path = os.path.join(base_dir, f"../../../data")

UPLOAD_DIR = Path(file_path)
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/upload_file")
async def upload_file(file: UploadFile = File(...)):
    if file.filename.endswith(".pdf"):
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        return {"filename": file.filename, "saved_path": str(file_path)}

    elif file.filename.endswith(".zip"):
        # Save ZIP temporarily
        zip_path = UPLOAD_DIR / file.filename
        with open(zip_path, "wb") as f:
            shutil.copyfileobj(file.file, f)


        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(UPLOAD_DIR)

        os.remove(zip_path)
        return {
            "filename": file.filename,
            "saved_path": str(zip_path)
        }

    else:
        raise HTTPException(status_code=400, detail="Only PDF or ZIP files are allowed.")
    
@router.get('/extract_pdf', response_description="Structure text from sample PDF")
async def structure_pdf(request: Request, pdf_file_name: str):
    gemini_extractor = GeminiPDFExtractor()
    return await gemini_extractor.extract_and_structure_pdf(pdf_file_name)