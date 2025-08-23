from fastapi import Request
from bson.objectid import ObjectId
from typing import Optional
from uuid import UUID, uuid4
from pydantic import Field, EmailStr
from pymongo import ReturnDocument

from config.database import Database
from schemas.user import User

class UserModel():
     collection: str = "users"
     
     def get_collection(self, request: Request):
          return request.app.db[self.collection]
     
     def list_users(self, request: Request) -> list:
          users = list(self.get_collection(request).find())
          for user in users:
               user["id"] = str(user["_id"]) 
          return users


     def list_teachers(self, request: Request) -> list:
          users = list(self.get_collection(request).find({'userType':'teacher'}))
          for user in users:
               user["id"] = str(user["_id"]) 
          return users


     def list_students(self, request: Request) -> list:
          users = list(self.get_collection(request).find({'userType':'student'}))
          for user in users:
               user["id"] = str(user["_id"]) 
          return users
          
     
     def find(self, request: Request, field: str, value) -> User:
          user = self.get_collection(request).find_one({field: value})
          if user:
               user["id"] = str(user["_id"])
               return user
     