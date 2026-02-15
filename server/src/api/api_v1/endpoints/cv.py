from fastapi import FastAPI, APIRouter, Request, UploadFile, File, HTTPException, Form, Query, Body
from pathlib import Path
import shutil
import zipfile
import os
from utils.gemini import GeminiPDFExtractor
from utils.github_extractor import GitHubExtractor
from bson.objectid import ObjectId
from schemas.cv import Cv,cvBase,cvCreate
from models.cv import CvModel
from models.job import JobModel
from typing import List, Union, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, EmailStr, Field
from bs4 import BeautifulSoup
from fastapi.responses import FileResponse, StreamingResponse
from config.config import settings
import logging
import re
from urllib.parse import urlparse
import pdfplumber
from utils.mailing.email_templates import send_cv_received_email
from utils.excel_extraction import create_cv_excel

logger = logging.getLogger(__name__)

router = APIRouter()
cv_model = CvModel()
job_model = JobModel()

base_dir = os.path.dirname(os.path.abspath(__file__)) 
file_path = os.path.join(base_dir, f"../../../data")

UPLOAD_DIR = Path(file_path)
UPLOAD_DIR.mkdir(exist_ok=True)

async def enrich_cv_with_github(cv_id: str, resume_content: dict) -> Optional[dict]:
    """
    Automatically enrich CV with GitHub data if GitHub URL is present
    
    Args:
        cv_id: MongoDB ObjectId of CV
        resume_content: Extracted resume content
        
    Returns:
        GitHub data dictionary or None
    """
    try:
        # Extract GitHub URL from resume
        personal_info = resume_content.get("personal_info", {})
        github_url = personal_info.get("github", "")
        
        if not github_url:
            logger.info(f"No GitHub URL found for CV {cv_id}")
            return None
        
        # Extract username
        extractor = GitHubExtractor(token=settings.GITHUB_API_TOKEN)
        username = GitHubExtractor.extract_username_from_url(github_url)
        
        if not username:
            logger.warning(f"Could not extract username from GitHub URL: {github_url}")
            return None
        
        logger.info(f"Fetching GitHub data for username: {username}")
        
        # Fetch complete GitHub profile
        github_data = await extractor.get_complete_profile(username)
        
        if github_data["fetch_status"] == "success":
            logger.info(f"Successfully fetched GitHub data for {username}")
        else:
            logger.warning(f"GitHub enrichment failed for {username}: {github_data.get('error')}")
        
        return github_data
        
    except Exception as e:
        logger.error(f"Error enriching CV {cv_id} with GitHub data: {str(e)}")
        return None

def clean_links(raw_links: set[str]) -> list[str]:
    cleaned = set()
    for link in raw_links:
        link = link.strip().replace("\n", "").replace(" ", "")
        cleaned.add(link)
    return list(cleaned)

def classify_links(links: list[str]) -> dict:
    result = {
        "profiles": {
            "github": [],
            "linkedin": [],
            "medium": [],
            "website": []
        },
        "github_repos": [],
        "certificates": [],
        "emails": [],
        "others": []
    }

    for link in links:
        if link.startswith("mailto:"):
            result["emails"].append(link)
            continue

        parsed = urlparse(link)
        domain = parsed.netloc.lower()
        path_parts = parsed.path.strip("/").split("/")

        # ---------- GitHub ----------
        if domain == "github.com":
            if len(path_parts) == 1:
                # GitHub profile
                result["profiles"]["github"].append(link)
            elif len(path_parts) >= 2:
                # GitHub repository
                result["github_repos"].append(link)
            continue

        # ---------- LinkedIn ----------
        if "linkedin.com" in domain:
            if path_parts and path_parts[0] == "in":
                result["profiles"]["linkedin"].append(link)
            else:
                result["others"].append(link)
            continue

        # ---------- Medium ----------
        if "medium.com" in domain:
            result["profiles"]["medium"].append(link)
            continue

        # ---------- Certificates ----------
        if any(d in domain for d in ["hackerrank.com", "coursera.org", "udemy.com", "linkedin.com/learning"]):
            result["certificates"].append(link)
            continue

        if "drive.google.com" in domain:
            result["certificates"].append(link)
            continue

        # ---------- Personal website ----------
        if domain and not domain.endswith(("github.com", "linkedin.com", "medium.com")):
            result["profiles"]["website"].append(link)
            continue

        result["others"].append(link)

    return result

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
    
    successful_cvs = []
    failed_cvs = []
    
    try:
        for file in files:
            if file.filename.endswith(".pdf"):
                try:
                    new_pdf_id = cv_model.create_cv(request, {"cvName":file.filename, "division": division, "jobName": jobName, "jobId": id, "selectedForInterview": False, "isDeleted": False, "comparisonResults": {}, "markGenerated": False, "finalMark": 0.0, "createdAt": datetime.now(timezone.utc)})
                    file_path = UPLOAD_DIR / f"{new_pdf_id}_{file.filename}"
                    with open(file_path, "wb") as f:
                        shutil.copyfileobj(file.file, f)


                    links = set()
                    with pdfplumber.open(file_path) as pdf:
                        for page in pdf.pages:
                            if page.hyperlinks:
                                for link in page.hyperlinks:
                                    if link.get("uri"):
                                        links.add(link["uri"])

                    cleaned_links = clean_links(links)
                    classified_links = classify_links(cleaned_links)
                    # Extract CV content
                    extract = await gemini_extractor.extract_and_structure_pdf(f"{new_pdf_id}_{file.filename}", classified_links)

                    # Automatically enrich with GitHub data
                    github_data = await enrich_cv_with_github(str(new_pdf_id), extract)
                    
                    # Update CV with extracted content and GitHub data
                    update_data = {
                        "candidateName": extract.get("personal_info", {}).get("name") or "",
                        "resumeContent": extract
                    }
                    if github_data:
                        update_data["githubData"] = github_data
                    
                    # Send CV received email
                    try:
                        candidate_email = extract.get("personal_info", {}).get("email") or ""
                        candidate_name = extract.get("personal_info", {}).get("name") or ""
                        if candidate_email:
                            await send_cv_received_email(
                                recipient_email=candidate_email,
                                candidate_name=candidate_name,
                                position=jobName,
                                cc_emails=[]
                            )
                            logger.info(f"CV received email sent to {candidate_email}")
                            update_data["mailStatus"] = "received_email_sent"
                    except Exception as email_error:
                        logger.error(f"Failed to send CV received email: {email_error}")
                        # Don't fail the CV processing if email fails

                    update_pdf = cv_model.update(request, "_id", ObjectId(new_pdf_id), update_data)
                    await generate_mark(request, [update_pdf])
                    
                    
                    successful_cvs.append(file.filename)
                except Exception as e:
                    failed_cvs.append({"filename": file.filename, "error": str(e)})
                    print(f"Error processing {file.filename}: {e}")

            elif file.filename.endswith(".zip"):
                # Save ZIP temporarily
                count = 1
                zip_path = UPLOAD_DIR / file.filename
                with open(zip_path, "wb") as f:
                    shutil.copyfileobj(file.file, f)


                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    for member in zip_ref.namelist():
                        if member.lower().endswith(".pdf"):
                            try:
                                original_name = Path(member).stem
                                print(f"Processing {original_name}::{count}")
                                count += 1
                                new_pdf_id = cv_model.create_cv(request, {"cvName":f"{original_name}.pdf", "division": division, "jobName": jobName, "jobId": id, "isDeleted": False, "comparisonResults": {}, "markGenerated": False, "finalMark": 0.0,"createdAt": datetime.now(timezone.utc)})
                                new_filename = f"{new_pdf_id}_{original_name}.pdf"
                                new_file_path = UPLOAD_DIR / new_filename

                                with zip_ref.open(member) as source, open(new_file_path, "wb") as target:
                                    shutil.copyfileobj(source, target)

                                links = set()
                                with pdfplumber.open(new_file_path) as pdf:
                                    for page in pdf.pages:
                                        if page.hyperlinks:
                                            for link in page.hyperlinks:
                                                if link.get("uri"):
                                                    links.add(link["uri"])

                                cleaned_links = clean_links(links)
                                classified_links = classify_links(cleaned_links)
                                # Extract CV content
                                extract = await gemini_extractor.extract_and_structure_pdf(new_filename, classified_links)
                                
                                # Automatically enrich with GitHub data
                                github_data = await enrich_cv_with_github(str(new_pdf_id), extract)
                                
                                # Update CV with extracted content and GitHub data
                                update_data = {
                                    "candidateName": extract.get("personal_info", {}).get("name") or "",
                                    "resumeContent": extract
                                }
                                if github_data:
                                    update_data["githubData"] = github_data
                                
                                # Send CV received email
                                try:
                                    candidate_email = extract.get("personal_info", {}).get("email") or ""
                                    candidate_name = extract.get("personal_info", {}).get("name") or ""
                                    if candidate_email:
                                        await send_cv_received_email(
                                            recipient_email=candidate_email,
                                            candidate_name=candidate_name,
                                            position=jobName,
                                            cc_emails=[]
                                        )
                                        logger.info(f"CV received email sent to {candidate_email}")
                                        update_data["mailStatus"] = "received_email_sent"
                                except Exception as email_error:
                                    logger.error(f"Failed to send CV received email: {email_error}")
                                    # Don't fail the CV processing if email fails

                                update_pdf = cv_model.update(request, "_id", ObjectId(new_pdf_id), update_data)
                                await generate_mark(request, [update_pdf])
                                
                                successful_cvs.append(f"{original_name}.pdf")

                            except Exception as e:
                                failed_cvs.append({"filename": f"{original_name}.pdf", "error": str(e)})
                                print(f"Error processing {original_name}.pdf: {e}")

                os.remove(zip_path)

            else:
                raise HTTPException(status_code=400, detail="Only PDF or ZIP files are allowed.")
        print(f"Successfully processed CVs: {successful_cvs}")
        print(f"Failed CVs: {failed_cvs} : {len(failed_cvs)} out of {len(files)}")
        return {
            "statusCode": 200,
            "message": "Files processing completed",
            "successful_cvs": successful_cvs,
            "failed_cvs": failed_cvs,
            "total_processed": len(successful_cvs),
            "total_failed": len(failed_cvs)
        }
    except Exception as e:
        print("Error uploading pdf:", e)
        raise HTTPException(status_code=400, detail=str(e))
    
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
            
            # Get GitHub data if available
            github_data = cv.get("githubData")
            
            # Generate marks with GitHub data
            generated_marks = await gemini_extractor.generate_marks(
                cv.get("resumeContent"), 
                job_data,
                github_data
            )
            total_mark = sum(item["mark"] for item in generated_marks.values())
            cv_model.update(request, "_id", ObjectId(cv.get("id")), {"comparisonResults": generated_marks, "markGenerated": True, "finalMark": total_mark, "selectedForInterview": total_mark >= job_data['selectionMark']})
            
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

@router.get("/fetch_github")
async def fetch_github(request: Request, id: str):
    print(id)
    githubData = cv_model.get_github_data(request, id)
    print(githubData)
    return githubData


class ExportCVsRequest(BaseModel):
    cv_ids: List[str] = Field(..., description="List of CV IDs to export")


@router.post("/export_cvs_to_excel")
async def export_cvs_to_excel(request: Request, export_request: ExportCVsRequest):
    """
    Export selected CVs to Excel file.
    
    Args:
        export_request: Request containing list of CV IDs to export
        
    Returns:
        StreamingResponse: Excel file download
    """
    try:
        cv_ids = export_request.cv_ids
        
        if not cv_ids:
            raise HTTPException(status_code=400, detail="No CV IDs provided")
        
        # Fetch CV data from database
        cv_data_list = []
        for cv_id in cv_ids:
            try:
                cv_data = cv_model.find(request, "_id", ObjectId(cv_id))
                if cv_data:
                    cv_data_list.append(cv_data)
            except Exception as e:
                logger.error(f"Error fetching CV {cv_id}: {e}")
                continue
        
        if not cv_data_list:
            raise HTTPException(status_code=404, detail="No CVs found for the provided IDs")
        
        # Create Excel file
        excel_file = create_cv_excel(cv_data_list)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"CV_Export_{timestamp}.xlsx"
        
        # Return as downloadable file
        return StreamingResponse(
            excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting CVs to Excel: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export CVs: {str(e)}")