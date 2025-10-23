from bson import ObjectId
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class Pdf(BaseModel):
    id: str
    pdfName: str
    candidateName: Optional[str] = None
    jobDescriptionId: Optional[str] = None
    resumeContent: Optional[object] = None
    isDeleted: bool
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    class Config:
        json_schema_extra = {
            "example": {
                "pdfName": "Chamath.pdf",
                "candidateName": "Chamath",
                "jobDescriptionId": "1222",
                "resumeContent": {
                    "Name": "Chamath"
                },
                "isDeleted": False
            }
        }

class PdfBase(BaseModel):
    pdfName: str
    candidateName: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    class Config:
        json_schema_extra = {
            "example": {
                "pdfName": "Chamath.pdf",
                "candidateName": "Chamath"
            }
        }


class PdfCreate(BaseModel):
    isDeleted: bool = False
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "pdfName": "Chamath.pdf",
                "candidateName": "Chamath",
                "jobDescriptionId": "1222",
                "resumeContent": {
                    "Name": "Chamath"
                },
                "isDeleted": False,
                "createdAt": "",
                "updatedAt": ""
            }
        }
