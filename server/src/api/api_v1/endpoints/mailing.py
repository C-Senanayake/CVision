from fastapi import APIRouter, HTTPException, Request
from pathlib import Path
import os
from pydantic import BaseModel, EmailStr, Field
from config.config import settings
import logging
from urllib.parse import urlparse
# from server.src.utils.mailing.gmail_service import gmail_service
from models.cv import CvModel
from utils.mailing.email_templates import (
    send_cv_received_email,
    send_cv_selected_email,
    send_interview_scheduled_email,
    send_cv_rejection_email
)
from bson.objectid import ObjectId
logger = logging.getLogger(__name__)

router = APIRouter()
cv_model = CvModel()
# Email template endpoints
class CVSchema(BaseModel):
    id: str
    recipient_email: EmailStr
    candidate_name: str
    position: str
    cc_emails: list = []

@router.post("/send-cv-received-email")
async def send_cv_received_email_endpoint(email_request: CVSchema):
    """Send CV received acknowledgment email to candidate."""
    try:
        result = await send_cv_received_email(
            recipient_email=email_request.recipient_email,
            candidate_name=email_request.candidate_name,
            position=email_request.position,
            cc_emails=email_request.cc_emails
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")


@router.post("/send-cv-selected-email")
async def send_cv_selected_email_endpoint(request: Request,email_request: list[CVSchema]):
    """Send selection notification email to candidate."""
    successfully_sent_emails = []
    failed_emails = []
    for email in email_request:
        try:
            result = await send_cv_selected_email(
                recipient_email=email.recipient_email,
                candidate_name=email.candidate_name,
                position=email.position,
                cc_emails=email.cc_emails
            )
            if result:
                successfully_sent_emails.append(email.recipient_email)
                cv_model.update(request, "_id", ObjectId(email.id), {'mailStatus': 'selection_email_sent'})
            else:
                failed_emails.append(email.recipient_email)
        except Exception as e:
            failed_emails.append(email.recipient_email)
    
    return {"successfully_sent_emails": successfully_sent_emails, "failed_emails": failed_emails}


class InterviewScheduledEmailSchema(BaseModel):
    id: str
    recipient_email: EmailStr
    candidate_name: str
    position: str
    event: str = Field(..., description="Event type (e.g., 'Technical Interview')")
    start_datetime: str = Field(..., description="Interview start datetime (e.g., '2026-02-20T14:00:00')")
    end_datetime: str = Field(..., description="Interview end datetime (e.g., '2026-02-20T15:00:00')")
    location: str = "https://maps.app.goo.gl/DT9BJrpEjN6CoyxW7"
    attendees: list = Field(default_factory=list, description="List of additional attendees (email addresses)")

@router.post("/send-interview-scheduled-email")
async def send_interview_scheduled_email_endpoint(request: Request, email_request: InterviewScheduledEmailSchema):
    """Send interview schedule email to candidate."""
    try:
        result = await send_interview_scheduled_email(
            recipient_email=email_request.recipient_email,
            candidate_name=email_request.candidate_name,
            position=email_request.position,
            event=email_request.event,
            start_datetime=email_request.start_datetime,
            end_datetime=email_request.end_datetime,
            location=email_request.location,
            attendees=email_request.attendees
        )
        update_data = {
            'mailStatus': 'interview_scheduled_email_sent',
            'interviewEvent': {
                'interviewName': email_request.event,
                'interviewLocation': email_request.location,
                'interviewAttendees': email_request.attendees,
                'interviewStartDatetime': email_request.start_datetime,
                'interviewEndDatetime': email_request.end_datetime
            }
        }
        if result:
            cv_model.update(request, "_id", ObjectId(email_request.id), update_data)
            return result
        else:
            raise HTTPException(status_code=500, detail="Failed to send interview scheduled email")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

@router.post("/send-cv-rejection-email")
async def send_cv_rejection_email_endpoint(request: Request, email_request: list[CVSchema]):
    """Send rejection email to candidate."""
    successfully_sent_emails = []
    failed_emails = []
    for email in email_request:
        try:
            result = await send_cv_rejection_email(
                recipient_email=email.recipient_email,
                candidate_name=email.candidate_name,
                position=email.position,
                cc_emails=email.cc_emails
            )
            if result:
                successfully_sent_emails.append(email.recipient_email)
                cv_model.update(request, "_id", ObjectId(email.id), {'mailStatus': 'rejection_email_sent'})
            else:
                failed_emails.append(email.recipient_email)
        except Exception as e:
            failed_emails.append(email.recipient_email)
    
    return {"successfully_sent_emails": successfully_sent_emails, "failed_emails": failed_emails}
    
# @router.post("/send-email-gmail/")
# async def send_email_endpoint(email_request: EmailSchema):
#     try:
#         await gmail_service.send_email_background(email_request.subject, email_request.recipient, email_request.body)
#         return {"message": "Email sending initiated in the background"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Email sending failed: {str(e)}")