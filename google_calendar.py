from datetime import timedelta
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/calendar.events"]


def get_calendar_service(credentials_file: str, token_file: str):
    creds = None
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_file):
                raise RuntimeError("Google credentials file not found.")
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_file, "w", encoding="utf-8") as token:
            token.write(creds.to_json())
    return build("calendar", "v3", credentials=creds)


def create_calendar_event(
    summary: str,
    start_time,
    duration_mins: int,
    timezone: str,
    attendees,
    credentials_file: str,
    token_file: str,
    calendar_id: str,
):
    service = get_calendar_service(credentials_file, token_file)
    end_time = start_time + timedelta(minutes=duration_mins)

    event_body = {
        "summary": summary,
        "start": {"dateTime": start_time.isoformat(), "timeZone": timezone},
        "end": {"dateTime": end_time.isoformat(), "timeZone": timezone},
        "attendees": [{"email": email} for email in attendees if email],
        "conferenceData": {
            "createRequest": {
                "requestId": f"veeniksha-{start_time.timestamp()}"
            }
        },
    }

    created_event = (
        service.events()
        .insert(
            calendarId=calendar_id,
            body=event_body,
            conferenceDataVersion=1,
            sendUpdates="all",
        )
        .execute()
    )

    meet_link = created_event.get("hangoutLink")
    event_id = created_event.get("id")
    return meet_link, event_id
