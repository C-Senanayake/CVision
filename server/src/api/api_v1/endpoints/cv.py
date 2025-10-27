from fastapi import FastAPI, APIRouter, Request, UploadFile, File, HTTPException, Form, Query, Body
from pathlib import Path
import shutil
import zipfile
import os
from utils.gemini import GeminiPDFExtractor
from bson.objectid import ObjectId
from schemas.cv import Cv,cvBase,cvCreate
from models.cv import CvModel
from models.job import JobModel
from typing import List, Union, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, EmailStr, Field
from bs4 import BeautifulSoup
from fastapi.responses import FileResponse

router = APIRouter()
cv_model = CvModel()
job_model = JobModel()

base_dir = os.path.dirname(os.path.abspath(__file__)) 
file_path = os.path.join(base_dir, f"../../../data")

UPLOAD_DIR = Path(file_path)
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/upload_cv")
async def upload_cv(
    request: Request,
    files: List[UploadFile] = File(...),
    division: str = Form(...),
    jobName: str = Form(...),
    id: str = Form(...)
):
    gemini_extractor = GeminiPDFExtractor()
    if files is None or len(files) == 0:
        raise HTTPException(status_code=400, detail="No files uploaded")
    try:
        for file in files:
            if file.filename.endswith(".pdf"):
                new_pdf_id = cv_model.create_cv(request, {"cvName":file.filename, "division": division, "jobName": jobName, "jobId": id, "isDeleted": False, "comparisonResults": {}, "markGenerated": False, "finalMark": 0.0, "createdAt": datetime.now(timezone.utc)})
                file_path = UPLOAD_DIR / f"{new_pdf_id}_{file.filename}"
                with open(file_path, "wb") as f:
                    shutil.copyfileobj(file.file, f)
                extract = await gemini_extractor.extract_and_structure_pdf(f"{new_pdf_id}_{file.filename}")
                update_pdf = cv_model.update(request, "_id", ObjectId(new_pdf_id), {"candidateName": extract.get("personal_info").get("name") or "","resumeContent": extract})

            elif file.filename.endswith(".zip"):
                # Save ZIP temporarily
                zip_path = UPLOAD_DIR / file.filename
                with open(zip_path, "wb") as f:
                    shutil.copyfileobj(file.file, f)


                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    for member in zip_ref.namelist():
                        if member.lower().endswith(".pdf"):
                            original_name = Path(member).stem
                            new_pdf_id = cv_model.create_cv(request, {"cvName":f"{original_name}.pdf", "division": division, "jobName": jobName, "jobId": id, "isDeleted": False, "comparisonResults": {}, "markGenerated": False, "finalMark": 0.0,"createdAt": datetime.now(timezone.utc)})
                            new_filename = f"{new_pdf_id}_{original_name}.pdf"
                            new_file_path = UPLOAD_DIR / new_filename

                            with zip_ref.open(member) as source, open(new_file_path, "wb") as target:
                                shutil.copyfileobj(source, target)
                            extract = await gemini_extractor.extract_and_structure_pdf(new_filename)
                            update_pdf = cv_model.update(request, "_id", ObjectId(new_pdf_id), {"candidateName": extract.get("personal_info").get("name") or "","resumeContent": extract})

                os.remove(zip_path)

            else:
                raise HTTPException(status_code=400, detail="Only PDF or ZIP files are allowed.")
        return {
            "statusCode": 200,
            "message": "Files uploaded successfully"
        }
    except Exception as e:
        print("Error uploading pdf:", e)
        raise HTTPException(status_code=400, detail="Error")
    
@router.get("/fetch_cvs")
async def fetch_cvs(request: Request, 
    jobName: Optional[str] = Query(None),
    candidateName: Optional[str] = Query(None),
    division: Optional[str] = Query(None)):
    filter_dict = {}
    if division:
        filter_dict["division"] = division
    if jobName is not None:
        filter_dict["jobName"] = jobName
    if candidateName is not None:
        filter_dict["candidateName"] = candidateName
    filter_dict["isDeleted"] = False
    try:
        cvs =  cv_model.fetch_cvs(request, filter_dict)
        if cvs:
            return {"cvs": cvs}
        else:
            raise HTTPException(status_code=400, detail="Error fetching cvs")
    except Exception as e:
        print("Error fetching cvs:", e)
        raise HTTPException(status_code=400, detail="Error fetching cvs")

@router.delete("/delete_cv")
async def delete_cv(request: Request, id: str):
    try:
        updated_cv = cv_model.update(request, "_id", ObjectId(id), {"isDeleted": True})
        if updated_cv:
            return 
    except Exception as e:
        print("Error deleting cv:", e)
        raise HTTPException(status_code=400, detail="Error deleting cv")

@router.put("/update_cv")
async def update_cv(request: Request, cv: dict):
    try:
        updated_cv = cv_model.update(request, "_id", ObjectId(cv.get("id")), cv)
        if updated_cv:
            return 
    except Exception as e:
        print("Error updating cv:", e)
        raise HTTPException(status_code=400, detail="Error updating cv")
    
@router.get('/extract_pdf', response_description="Structure text from sample PDF")
async def structure_pdf(request: Request, pdf_file_name: str):
    gemini_extractor = GeminiPDFExtractor()
    return await gemini_extractor.extract_and_structure_pdf(pdf_file_name)

@router.post("/generate_mark")
async def generate_mark(request: Request, data: List[dict] = Body(...)):
    try:
        for cv in data:
            job_data = job_model.find(request, "_id", ObjectId(cv.get("jobId")))
            soup = BeautifulSoup(job_data["jobDescription"], "html.parser")
            job_data["jobDescription"] = soup.get_text(separator="\n")
            gemini_extractor = GeminiPDFExtractor()
            generated_marks = await gemini_extractor.generate_marks(cv.get("resumeContent"), job_data)
            total_mark = sum(item["mark"] for item in generated_marks.values())
            updated_cv = cv_model.update(request, "_id", ObjectId(cv.get("id")), {"comparisonResults": generated_marks, "markGenerated": True, "finalMark": total_mark})
            if updated_cv:
                return 
    except Exception as e:
        print("Error updating cv:", e)
        raise HTTPException(status_code=400, detail="Error updating cv")
    
@router.get("/get_pdf")
async def get_pdf(request: Request, 
    id: Optional[str] = Query(None),
    cvName: Optional[str] = Query(None)):
    # try to find a matching PDF
    pdf_file = next(UPLOAD_DIR.glob(f"{id}_{cvName}"), None)
    
    if not pdf_file or not pdf_file.exists():
        raise HTTPException(status_code=404, detail="PDF not found")
    
    return FileResponse(path=pdf_file, filename=pdf_file.name, media_type='application/pdf')