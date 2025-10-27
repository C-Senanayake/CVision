from fastapi import FastAPI, APIRouter, Request, HTTPException, Query
from bson.objectid import ObjectId
from schemas.job import Job,JobCreate
from models.job import JobModel
from typing import Optional, Any

router = APIRouter()
job_model = JobModel()

@router.post("/create_job")
async def create_job(request: Request, job: JobCreate):
    try:
        job_id = job_model.create_job(request, job)
        if job_id:
            return {"job_id": str(job_id)}
        else:
            raise HTTPException(status_code=400, detail="Error creating job")
    except Exception as e:
        print("Error creating job:", e)
        error_message = str(e)
        if "duplicate" in error_message.lower():
            raise HTTPException(status_code=400, detail="Job with this name already exists")
        
        raise HTTPException(status_code=400, detail="Error creating job")

@router.get("/fetch_jobs")
async def fetch_jobs(request: Request, 
    jobName: Optional[str] = Query(None),
    division: Optional[str] = Query(None)):
    filter_dict = {}
    if division:
        filter_dict["division"] = division
    if jobName is not None:
        filter_dict["jobName"] = jobName
    filter_dict["isDeleted"] = False
    try:
        jobs =  job_model.fetch_jobs(request, filter_dict)
        if jobs:
            return {"jobs": jobs}
        else:
            raise HTTPException(status_code=400, detail="Error fetching jobs")
    except Exception as e:
        print("Error fetching jobs:", e)
        raise HTTPException(status_code=400, detail="Error fetching jobs")
    
@router.delete("/delete_job")
async def delete_job(request: Request, id: str):
    try:
        updated_job = job_model.update(request, "_id", ObjectId(id), {"isDeleted": True})
        if updated_job:
            return 
    except Exception as e:
        print("Error deleting jobs:", e)
        raise HTTPException(status_code=400, detail="Error deleting jobs")

@router.put("/update_job")
async def update_job(request: Request, job: dict):
    try:
        updated_job = job_model.update(request, "_id", ObjectId(job.get("id")), job)
        if updated_job:
            return 
    except Exception as e:
        print("Error updating jobs:", e)
        raise HTTPException(status_code=400, detail="Error updating jobs")