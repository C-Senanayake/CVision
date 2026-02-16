import os
import webbrowser

import requests
import msal
from dotenv import load_dotenv
load_dotenv()

MS_GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"

def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value

TENANT_ID = _required_env("TENANT_ID")
APPLICATION_ID = _required_env("CLIENT_ID")
CLIENT_SECRET = _required_env("CLIENT_SECRET")
CC_EMAILS = _required_env("CC_EMAILS").split(",")  # Comma-separated list of CC emails
base_dir = os.path.dirname(os.path.abspath(__file__)) 
token_path = os.path.join(base_dir, f"./refresh_token.txt")
# SENDER_EMAIL = _required_env("OUTLOOK_EMAIL")

class GraphEmailService:
    def get_access_token(self):
        # Scopes needed for personal Outlook accounts (delegated permissions)
        scopes = [
            "https://graph.microsoft.com/Mail.Send",
            "https://graph.microsoft.com/Calendars.ReadWrite"
        ]
        
        client = msal.ConfidentialClientApplication(
            client_id=APPLICATION_ID,
            client_credential=CLIENT_SECRET,
            authority=f"https://login.microsoftonline.com/consumers"
        )
        #Check if there is a refresh token available
        refresh_token = None
        if os.path.exists(token_path):
            with open(token_path, "r") as f:
                refresh_token = f.read().strip()
        if refresh_token:
            token_response = client.acquire_token_by_refresh_token(refresh_token, scopes=scopes)
        else:
            # If no refresh token, acquire a new access token
            auth_request_url = client.get_authorization_request_url(scopes=scopes)
            webbrowser.open(auth_request_url)
            print("Please authenticate in the browser and paste the resulting URL here:")
            authorization_code = input("Enter the authorization code: ")

            if not authorization_code:
                raise RuntimeError("Authorization code is required to acquire access token")
            token_response = client.acquire_token_by_authorization_code(
                authorization_code, 
                scopes=scopes
            )
        if "access_token" in token_response:
            # Save the refresh token for future use
            if "refresh_token" in token_response:
                with open(token_path, "w") as f:
                    f.write(token_response["refresh_token"])
            return token_response["access_token"]
        else:
            raise RuntimeError(f"Failed to acquire access token: {token_response.get('error_description', 'No error description')}")
        

    async def send_email(self, subject:str, email_to: str, body: str, cc_emails: list = CC_EMAILS):
        cc_emails = CC_EMAILS
        access_token = self.get_access_token()

        url = "https://graph.microsoft.com/v1.0/me/sendMail"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        message = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "HTML",
                    "content": body
                },
                "toRecipients": [
                    {
                        "emailAddress": {"address": "cvisioned@gmail.com"}
                    }
                ],
                "ccRecipients": [{"emailAddress": {"address": email}} for email in cc_emails]
            }
        }

        response = requests.post(url, headers=headers, json=message)
        # print(f"Email send response: {response} - {response.status_code} - {response.text}")
        if response.status_code == 202:
            return {"status": "Email sent successfully"}
        else:
            return {"error": response.json()}
    
    async def send_calendar_invite(
        self,
        email_to: str,
        subject: str,
        start_datetime: str,
        end_datetime: str,
        timezone: str = "IST",
        body: str = "",
        location: str = "https://maps.app.goo.gl/DT9BJrpEjN6CoyxW7",
        attendees: list = []
    ):
        """
        Send a calendar invite from personal Outlook account.
        
        Args:
            attendee_email: Email address of the attendee
            subject: Subject of the meeting
            start_datetime: Start time in ISO format (e.g., "2026-02-20T14:00:00")
            end_datetime: End time in ISO format (e.g., "2026-02-20T15:00:00")
            timezone: Timezone - use IANA format like "Asia/Colombo", "UTC", "America/New_York", or Windows format like "Pacific Standard Time"
            body: Optional meeting description
            location: Optional meeting location
        """
        
        access_token = self.get_access_token()
        
        url = "https://graph.microsoft.com/v1.0/me/events"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        event = {
            "subject": subject,
            "body": {
                "contentType": "HTML",
                "content": body or f"<p>You are invited to: {subject}</p>"
            },
            "start": {
                "dateTime": start_datetime
            },
            "end": {
                "dateTime": end_datetime
            },
            "location": {
                "displayName": location
            },
            "attendees": [
                {
                    "emailAddress": {
                        "address": "cvisioned@gmail.com"
                    },
                    "type": "required"
                }
            ]+ [{
                    "emailAddress": {
                        "address": email
                    },
                    "type": "required"
                } for email in attendees
            ],
            "isOnlineMeeting": False,
            "responseRequested": True
        }
        
        response = requests.post(url, headers=headers, json=event)
        # print(f"Calendar invite response: {response} - {response.status_code} - {response.text}")
        if response.status_code in [200, 201]:
            return {"status": "Calendar invite sent successfully", "event": response.json()}
        else:
            return {"error": response.json(), "status_code": response.status_code}
        


graph_email_service = GraphEmailService()
