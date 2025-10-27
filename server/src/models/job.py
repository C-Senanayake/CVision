from fastapi import Request
from bson.objectid import ObjectId
from uuid import UUID, uuid4
from pydantic import Field, EmailStr
from pymongo import ReturnDocument
from typing import Union, Dict, Any, Optional
from config.database import Database
from schemas.job import Job,JobCreate,JobBase
from datetime import datetime, timezone
class JobModel():
     
     collection: str = "jobs"

     def get_collection(self, request: Request):
          return request.app.db[self.collection]
         
     def fetch_jobs(self, request: Request, filter_dict: Optional[dict] = None) -> JobBase:
          jobs = list(self.get_collection(request).find(filter_dict))
          for job in jobs:
               job["id"] = str(job["_id"]) 
               del job["_id"]
          return jobs

     def list_job(self, request: Request) -> list:
          job = list(self.get_collection(request).find({'userType':'teacher'}))
          for job in job:
               job["id"] = str(job["_id"]) 
          return job
          
     
     def find(self, request: Request, field: str, value) -> Job:
          job = self.get_collection(request).find_one({field: value})
          if job:
               job["id"] = str(job["_id"])
               return job
          
     def exist_job(self, request: Request, jobName: str):
          existing_job = self.get_collection(request).find_one({"jobName": jobName})
          return True if existing_job else False
          
     def create_job(self, request: Request, job: JobCreate):
          new_job = self.get_collection(request).insert_one(job.dict())
          
          if new_job:
               return new_job.inserted_id
     
     def update(self, request: Request, filter: str, value: Union[str, ObjectId], data)-> Optional[Dict[str, Any]]:
          data['updatedAt'] = datetime.now(timezone.utc)
          updated_job = self.get_collection(request).find_one_and_update(
               {filter : value}, 
               {'$set': data},
               return_document=ReturnDocument.AFTER
          )
          
          if updated_job:
               updated_job["id"] = str(updated_job["_id"])
               return updated_job
          else:
               return False
     