import os
from pathlib import Path
from typing import Dict, Any
from utils.mailing.ms_graph import graph_email_service

# Get the templates directory path
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
base_dir = os.path.dirname(os.path.abspath(__file__)) 
file_path = os.path.join(base_dir, f"./templates")

def load_template(template_name: str) -> str:
    """Load an HTML email template from the templates directory."""
    template_path = Path(file_path) / template_name
    if not template_path.exists():
        raise FileNotFoundError(f"Template {template_name} not found at {template_path}")
    
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


def render_template(template_content: str, variables: Dict[str, Any]) -> str:
    """Replace template variables with actual values."""
    rendered = template_content
    for key, value in variables.items():
        placeholder = f"{{{{{key}}}}}"
        rendered = rendered.replace(placeholder, str(value))
    return rendered


async def send_cv_received_email(
    recipient_email: str,
    candidate_name: str,
    position: str,
    cc_emails: list = []
) -> Dict[str, Any]:
    """
    Send an email acknowledging CV receipt.
    
    Args:
        recipient_email: Candidate's email address
        candidate_name: Name of the candidate
        position: Position applied for
        
    Returns:
        Response from email service
    """
    try:
        template = load_template("cv_received_template.html")
        
        email_body = render_template(template, {
            "email": recipient_email,
            "name": candidate_name,
            "position": position
        })
        
        subject = f"Application Received - {position}"
        
        await graph_email_service.send_email(
            subject=subject,
            email_to=recipient_email,
            body=email_body,
            cc_emails=cc_emails
        )
        
        return {
            "status": "success",
            "message": f"CV received email sent to {recipient_email}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to send CV received email: {str(e)}"
        }


async def send_cv_selected_email(
    recipient_email: str,
    candidate_name: str,
    position: str,
    cc_emails: list = []
) -> Dict[str, Any]:
    """
    Send an email notifying candidate of selection.
    
    Args:
        recipient_email: Candidate's email address
        candidate_name: Name of the candidate
        position: Position selected for
        
    Returns:
        Response from email service
    """
    try:
        template = load_template("cv_selected_template.html")
        
        email_body = render_template(template, {
            "email": recipient_email,
            "name": candidate_name,
            "position": position
        })
        
        subject = f"Congratulations! You've Been Selected - {position}"
        
        await graph_email_service.send_email(
            subject=subject,
            email_to=recipient_email,
            body=email_body,
            cc_emails=cc_emails
        )
        
        return {
            "status": "success",
            "message": f"Selection email sent to {recipient_email}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to send selection email: {str(e)}"
        }


async def send_interview_scheduled_email(
    recipient_email: str,
    candidate_name: str,
    position: str,
    event: str,
    location: str,
    start_datetime: str,
    end_datetime: str,
    attendees: list = []
) -> Dict[str, Any]:
    """
    Send an email with interview schedule details.
    
    Args:
        recipient_email: Candidate's email address
        candidate_name: Name of the candidate
        position: Position for interview
        event: Type of interview (e.g., "Technical Interview")
        date: Interview date (e.g., "February 20, 2026")
        time: Interview time (e.g., "2:00 PM - 3:00 PM")
        location: Interview location (e.g., "Conference Room A" or "Zoom Meeting")
        
    Returns:
        Response from email service
    """
    try:
        template = load_template("interview_scheduled_template.html")
        
        email_body = render_template(template, {
            "name": candidate_name,
            "email": recipient_email,
            "position": position,
            "event": event,
            "start_datetime": start_datetime,
            "location": location,
        })
        
        subject = f"Interview Scheduled - {position}"
        
        await graph_email_service.send_calendar_invite(
            subject=subject,
            email_to=recipient_email,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            body=email_body,
            attendees=attendees
        )
        
        return {
            "status": "success",
            "message": f"Interview schedule email sent to {recipient_email}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to send interview schedule email: {str(e)}"
        }


async def send_cv_rejection_email(
    recipient_email: str,
    candidate_name: str,
    position: str,
    cc_emails: list = []
) -> Dict[str, Any]:
    """
    Send a rejection email to candidate.
    
    Args:
        recipient_email: Candidate's email address
        candidate_name: Name of the candidate
        position: Position applied for
        
    Returns:
        Response from email service
    """
    try:
        template = load_template("cv_rejection_template.html")
        
        email_body = render_template(template, {
            "email": recipient_email,
            "name": candidate_name,
            "position": position
        })
        
        subject = f"Application Update - {position}"
        
        await graph_email_service.send_email(
            subject=subject,
            email_to=recipient_email,
            body=email_body,
            cc_emails=cc_emails
        )
        
        return {
            "status": "success",
            "message": f"Rejection email sent to {recipient_email}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to send rejection email: {str(e)}"
        }
