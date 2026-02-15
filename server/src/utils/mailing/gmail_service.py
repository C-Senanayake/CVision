from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr, BaseModel
import os
from dotenv import load_dotenv
load_dotenv()

# For Gmail accounts, you need to:
# 1. Enable 2-Step Verification at: https://myaccount.google.com/security
# 2. Create an App Password at: https://myaccount.google.com/apppasswords
# 3. Use the app password (16 characters without spaces) as MAIL_PASSWORD

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("GMAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("GMAIL_PASSWORD"),  # Use App Password from Google
    MAIL_SERVER=os.getenv("GMAIL_SERVER", "smtp.gmail.com"),  # Gmail SMTP server
    MAIL_PORT=int(os.getenv("GMAIL_PORT", "587")),  # Gmail uses port 587 for TLS
    MAIL_FROM=os.getenv("GMAIL_FROM", "cvisioned@gmail.com"),
    MAIL_FROM_NAME=os.getenv("GMAIL_FROM_NAME", "CVision"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

class GmailEmailService:
    async def send_email(self, subject: str, email_to: str, body: str):
        print(f"Preparing to send email to {email_to} with subject '{subject}'")
        message = MessageSchema(
            subject=subject,
            recipients=[email_to],
            body=body,
            subtype=MessageType.plain # Use MessageType.html if sending HTML content
        )

        fm = FastMail(conf)
        await fm.send_message(message)
        return JSONResponse(status_code=200, content={"message": "email has been sent"}) 

gmail_service = GmailEmailService()