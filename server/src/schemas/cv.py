from bson import ObjectId
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, timezone

class Cv(BaseModel):
    id: str
    cvName: str
    candidateName: Optional[str] = None
    jobId: Optional[str] = None
    jobName: Optional[str] = None
    division: Optional[str] = None
    resumeContent: Optional[object] = None
    comparisonResults: Optional[object] = None
    markGenerated: Optional[bool] = False
    finalMark: Optional[float] = 0.0
    selectedForInterview: Optional[bool] = False
    mailStatus: Optional[str] = None
    interviewEvent: Optional[object] = None
    isDeleted: bool = False
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: Optional[datetime] = None
    class Config:
        json_schema_extra = {
            "example": {
                "cvName": "Chamath.cv",
                "candidateName": "Chamath",
                "jobId": "1222",
                "jobName": "Intern Software Engineer",
                "division": "Software",
                "resumeContent": {
                    "Name": "Chamath"
                },
                "interviewEvent": {
                    "interviewName": "Technical Interview",
                    "interviewLocation": "https://maps.app.goo.gl/DT9BJrpEjN6CoyxW7",
                    "interviewAttendees": ["chamath@example.com", "hr@example.com"],
                    "interviewStartDatetime": "2026-02-20T14:00:00",
                    "interviewEndDatetime": "2026-02-20T15:00:00"
                },
                "isDeleted": False
            }
        }

class cvBase(BaseModel):
    cvName: str
    candidateName: Optional[str] = None
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: Optional[datetime] = None
    class Config:
        json_schema_extra = {
            "example": {
                "cvName": "Chamath.cv",
                "candidateName": "Chamath"
            }
        }


class cvCreate(BaseModel):
    cvName: str
    jobId: Optional[str] = None
    jobName: Optional[str] = None
    division: Optional[str] = None
    comparisonResults: Optional[object] = None
    finalMark: Optional[float] = 0.0
    selectedForInterview: Optional[bool] = False
    mailStatus: Optional[str] = None
    interviewEvent: Optional[object] = None
    markGenerated: Optional[bool] = False
    isDeleted: bool = False
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "cvName": "Chamath.pdf",
                "jobId": "1222",
                "jobName": "Intern Software Engineer",
                "division": "Software",
                "isDeleted": False,
                "createdAt": "",
                "updatedAt": ""
            }
        }
