from fastapi import APIRouter, Request, Response, HTTPException, status, BackgroundTasks
from fastapi.responses import HTMLResponse
from bson.json_util import dumps
from typing import Optional, List
from pydantic import EmailStr
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from bson.objectid import ObjectId

from schemas.user import User
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
