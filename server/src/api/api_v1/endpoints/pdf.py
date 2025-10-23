from fastapi import FastAPI, APIRouter, Request, UploadFile, File, HTTPException
from pathlib import Path
import shutil
import zipfile
import os
from utils.gemini import GeminiPDFExtractor
from bson.objectid import ObjectId
from schemas.pdf import Pdf,PdfBase
from models.pdf import PdfModel

router = APIRouter()
pdf_model = PdfModel()

base_dir = os.path.dirname(os.path.abspath(__file__)) 
file_path = os.path.join(base_dir, f"../../../data")

UPLOAD_DIR = Path(file_path)
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/upload_file")
async def upload_file(request: Request, file: UploadFile = File(...)):
    gemini_extractor = GeminiPDFExtractor()
    try:
        if file.filename.endswith(".pdf"):
            new_pdf_id = pdf_model.create_pdf(request, {"pdfName":file.filename})
            file_path = UPLOAD_DIR / f"{new_pdf_id}_{file.filename}"
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            extract = await gemini_extractor.extract_and_structure_pdf(f"{new_pdf_id}_{file.filename}")
            update_pdf = pdf_model.update(request, "_id", ObjectId(new_pdf_id), {"resumeContent": extract})
            return {"filename": file.filename, "saved_path": str(file_path)}

        elif file.filename.endswith(".zip"):
            # Save ZIP temporarily
            zip_path = UPLOAD_DIR / file.filename
            with open(zip_path, "wb") as f:
                shutil.copyfileobj(file.file, f)


            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                for member in zip_ref.namelist():
                    if member.lower().endswith(".pdf"):
                        original_name = Path(member).stem
                        new_pdf_id = pdf_model.create_pdf(request, {"pdfName":f"{original_name}.pdf"})
                        new_filename = f"{new_pdf_id}_{original_name}.pdf"
                        new_file_path = UPLOAD_DIR / new_filename

                        with zip_ref.open(member) as source, open(new_file_path, "wb") as target:
                            shutil.copyfileobj(source, target)
                        extract = await gemini_extractor.extract_and_structure_pdf(new_filename)
                        update_pdf = pdf_model.update(request, "_id", ObjectId(new_pdf_id), {"resumeContent": extract})

            os.remove(zip_path)
            return {
                "filename": file.filename,
                "saved_path": str(zip_path)
            }

        else:
            raise HTTPException(status_code=400, detail="Only PDF or ZIP files are allowed.")
    except Exception as e:
        print("Error uploading pdf:", e)
        raise HTTPException(status_code=400, detail="Error")
    
@router.get('/extract_pdf', response_description="Structure text from sample PDF")
async def structure_pdf(request: Request, pdf_file_name: str):
    gemini_extractor = GeminiPDFExtractor()
    return await gemini_extractor.extract_and_structure_pdf(pdf_file_name)