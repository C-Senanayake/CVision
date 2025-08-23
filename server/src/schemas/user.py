from bson import ObjectId
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class User(BaseModel):
    id: str
    firstName: str
    lastName: str
    email: EmailStr
    userType: str
    emailActive: bool
    isDeleted: bool
    title: Optional[str] = None
    role: Optional[str] = None
    createdAt: Optional[datetime] = None

    class Config:
        schema_extra = {
            "example": {
                "firstName": "Dinith",
                "lastName": "Kumudika",
                "email": "dinith1999@gmail.com",
                "userType": "student",
                "emailActive": False,
                "isDeleted": False,
                "title": "Dr",
                "role": "Lecturer"
            }
        }


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    class Config:
        schema_extra = {
            "example": {
                "email": "dinith1999@gmail.com",
                "password": "Dinith@123"
            }
        }


class UserBase(BaseModel):
    firstName: str
    lastName: str
    email: EmailStr
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    class Config:
        schema_extra = {
            "example": {
                "firstName": "Dinith",
                "lastName": "Kumudika",
                "email": "dinith1999@gmail.com"
            }
        }


class UserCreate(UserBase):
    emailActive: bool = False
    verificationCode: str = None
    isDeleted: bool = False
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    class Config:
        schema_extra = {
            "example": {
                "firstName": "Dinith",
                "lastName": "Kumudika",
                "email": "dinith1999@gmail.com",
                "password": "$2a$10$8KkORxP4/YpPBarYGKd6VO6aohKYAaDQC/9ZYZImj0Yf71VHGfGEG",
                "userType": "student",
                "emailActive": False,
                "verificationCode": "",
                "isDeleted": False,
                "createdAt": "",
                "updatedAt": ""
            }
        }
