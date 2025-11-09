from fastapi import Request
from bson.objectid import ObjectId
from uuid import UUID, uuid4
from pydantic import Field, EmailStr
from pymongo import ReturnDocument
from typing import Union, Dict, Any, Optional
from config.database import Database
from schemas.cv import cvCreate, Cv
from datetime import datetime, timezone
class CvModel():
     collection: str = "cvs"
     
     def get_collection(self, request: Request):
          return request.app.db[self.collection]
     
     def fetch_cvs(self, request: Request, filter_dict: Optional[dict] = None) -> Cv:
          cvs = list(self.get_collection(request).find(filter_dict))
          for cv in cvs:
               cv["id"] = str(cv["_id"]) 
               del cv["_id"]
          return cvs
     
     def list_cvs(self, request: Request) -> list:
          cvs = list(self.get_collection(request).find())
          for cv in cvs:
               cv["id"] = str(cv["_id"]) 
          return cv


     def list_cv(self, request: Request) -> list:
          cvs = list(self.get_collection(request).find({'userType':'teacher'}))
          for cv in cvs:
               cv["id"] = str(cv["_id"]) 
          return cv
          
     
     def find(self, request: Request, field: str, value) -> Cv:
          cv = self.get_collection(request).find_one({field: value})
          if cv:
               cv["id"] = str(cv["_id"])
               return cv
          
     def create_cv(self, request: Request, cv: cvCreate):
          new_cv = self.get_collection(request).insert_one(cv)
          
          if new_cv:
               return new_cv.inserted_id
     
     def update(self, request: Request, filter: str, value: Union[str, ObjectId], data)-> Optional[Dict[str, Any]]:
          data['updatedAt'] = datetime.now(timezone.utc)
          updated_cv = self.get_collection(request).find_one_and_update(
               {filter : value}, 
               {'$set': data},
               return_document=ReturnDocument.AFTER
          )
          
          if updated_cv:
               updated_cv["id"] = str(updated_cv["_id"])
               return updated_cv
          else:
               return False
          
     def get_github_data(self, request: Request, cv_id: str) -> Optional[Dict[str, Any]]:
          cv = self.get_collection(request).find_one(
               {"_id": ObjectId(cv_id)},
               {"githubData": 1}
          )
          return cv.get("githubData") if cv else None


# Standalone functions for GitHub integration (no request dependency)
class CV:
     """Static methods for CV operations without Request dependency"""
     
     @staticmethod
     def get_cv_by_id(cv_id: str) -> Optional[Dict[str, Any]]:
          """
          Get CV document by ID
          
          Args:
               cv_id: MongoDB ObjectId as string
               
          Returns:
               CV document or None
          """
          db = Database.get_db()
          cv = db["cvs"].find_one({"_id": ObjectId(cv_id)})
          return cv
     
     @staticmethod
     def update_github_data(cv_id: str, github_data: Dict[str, Any]) -> bool:
          """
          Update CV document with GitHub enrichment data
          
          Args:
               cv_id: MongoDB ObjectId as string
               github_data: GitHub data dictionary
               
          Returns:
               True if successful, False otherwise
          """
          db = Database.get_db()
          result = db["cvs"].update_one(
               {"_id": ObjectId(cv_id)},
               {
                    "$set": {
                         "githubData": github_data,
                         "updatedAt": datetime.now(timezone.utc)
                    }
               }
          )
          return result.modified_count > 0 or result.matched_count > 0

     