from datetime import datetime
from fastapi import APIRouter, Request, Response, HTTPException, status, BackgroundTasks, Body
from fastapi.responses import HTMLResponse
from bson.json_util import dumps
from typing import Optional, List
from pydantic import EmailStr
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from bson.objectid import ObjectId

from schemas.user import User,UserBase
from models.user import UserModel


router = APIRouter()
user_model = UserModel()


@router.get('/', response_description="Get users", response_model=List[User])
async def read_users(request: Request, limit: Optional[int] = None):
     users = user_model.list_users(request)
     
     if users:
          return users 
     raise HTTPException(
          status_code=status.HTTP_404_NOT_FOUND, 
          detail="no users found"
     )

# register new user
@router.post("/register", response_description="Create new user", response_model=UserBase)
async def register(request: Request, payload: UserBase) -> UserBase:
    print("TYPE::",type)
    print("PAYLOAD::",payload)
        
    payload.createdAt = datetime.utcnow()
    payload.updatedAt = payload.createdAt
        
    
    new_user_id = user_model.create_user(request, payload)
    
    return JSONResponse(
        status_code=status.HTTP_200_OK
    )

