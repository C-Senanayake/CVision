from bson import ObjectId
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, timezone

class Job(BaseModel):
    id: str
    jobName: str
    jobDescription: Optional[str] = None
    division: str
    criteria: Optional[object] = None
    isDeleted: bool = False
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: Optional[datetime] = None
    class Config:
        json_schema_extra = {
            "example": {
                "jobName": "Software Engineer Intern",
                "jobDescription": "",
                "division": "Software",
                "criteria": {
                    "A/L": 0.1,
                    "GPA": 0.3,
                },
                "isDeleted": False,
            }
        }

class JobBase(BaseModel):
    jobName: str
    jobDescription: Optional[str] = None
    division: str
    criteria: Optional[object] = None
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: Optional[datetime] = None
    class Config:
        json_schema_extra = {
            "example": {
                "jobName": "Software Engineer Intern",
                "jobDescription": "",
                "division": "Software",
                "criteria": {
                    "A/L": 0.1,
                    "GPA": 0.3,
                }
            }
        }


class JobCreate(BaseModel):
    jobName: str
    jobDescription: Optional[str] = None
    division: str
    criteria: Optional[object] = None
    isDeleted: bool = False
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "jobName": "Software Engineer Intern",
                "jobDescription": "",
                "division": "Software",
                "criteria": {
                    "A/L": 0.1,
                    "GPA": 0.3,
                },
                "isDeleted": False,
                "createdAt": "",
                "updatedAt": ""
            }
        }
