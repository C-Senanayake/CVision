from fastapi import Request
from bson.objectid import ObjectId
from uuid import UUID, uuid4
from pydantic import Field, EmailStr
from pymongo import ReturnDocument
from typing import Union, Dict, Any, Optional
from config.database import Database
from schemas.pdf import Pdf,PdfBase

class PdfModel():
     collection: str = "pdfs"
     
     def get_collection(self, request: Request):
          return request.app.db[self.collection]
     
     def list_pdfs(self, request: Request) -> list:
          pdf = list(self.get_collection(request).find())
          for pdf in pdf:
               pdf["id"] = str(pdf["_id"]) 
          return pdf


     def list_pdf(self, request: Request) -> list:
          pdf = list(self.get_collection(request).find({'userType':'teacher'}))
          for pdf in pdf:
               pdf["id"] = str(pdf["_id"]) 
          return pdf
          
     
     def find(self, request: Request, field: str, value) -> Pdf:
          pdf = self.get_collection(request).find_one({field: value})
          if pdf:
               pdf["id"] = str(pdf["_id"])
               return pdf
          
     def create_pdf(self, request: Request, pdf: PdfBase):
          new_pdf = self.get_collection(request).insert_one(pdf)
          
          if new_pdf:
               return new_pdf.inserted_id
     
     def update(self, request: Request, filter: str, value: Union[str, ObjectId], data)-> Optional[Dict[str, Any]]:
          print("filters", filter)
          print("data", data)
          updated_pdf = self.get_collection(request).find_one_and_update(
               {filter : value}, 
               {'$set': data},
               return_document=ReturnDocument.AFTER
          )
          
          print("updated pdf", updated_pdf)
          if updated_pdf:
               updated_pdf["id"] = str(updated_pdf["_id"])
               return updated_pdf
          else:
               return False
     