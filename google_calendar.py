from datetime import timedelta
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

def _service_from_token_json(token_json: str):
    info = json.loads(token_json)
    creds = Credentials.from_authorized_user_info(info, SCOPES)

    # refresh if needed
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    service = build("calendar", "v3", credentials=creds)
    return service, creds.to_json()  # return updated token_json after refresh


def create_calendar_event(
    token_json: str,
    summary: str,
    start_time,
    duration_mins: int,
    timezone: str,
    attendees,
    calendar_id: str,
):
    service, updated_token_json = _service_from_token_json(token_json)
    end_time = start_time + timedelta(minutes=duration_mins)

    event_body = {
        "summary": summary,
        "start": {"dateTime": start_time.isoformat(), "timeZone": timezone},
        "end": {"dateTime": end_time.isoformat(), "timeZone": timezone},
        "attendees": [{"email": email} for email in attendees if email],
        "conferenceData": {"createRequest": {"requestId": f"veeniksha-{start_time.timestamp()}"}},
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

    # Meet link extraction
    meet_link = created_event.get("hangoutLink")
    if not meet_link:
        conf = created_event.get("conferenceData") or {}
        for ep in conf.get("entryPoints", []):
            uri = ep.get("uri")
            ep_type = (ep.get("entryPointType") or "").lower()
            if uri and ("meet.google.com" in uri or ep_type == "video"):
                meet_link = uri
                break
    if not meet_link:
        meet_link = created_event.get("htmlLink") or created_event.get("location")

    return meet_link, created_event.get("id"), updated_token_json
