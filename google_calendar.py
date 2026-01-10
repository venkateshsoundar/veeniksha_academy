from datetime import timedelta
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/calendar"
]


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
            # Allow configuring OAuth behavior via environment:
            # - GOOGLE_OAUTH_PORT: set a fixed port (e.g., 8080) to register as a redirect URI for Web clients
            # - GOOGLE_OAUTH_CONSOLE: set to '1' or 'true' to use a console (copy/paste) flow instead of local server
            port = int(os.getenv("GOOGLE_OAUTH_PORT", "0"))
            use_console = os.getenv("GOOGLE_OAUTH_CONSOLE", "0").lower() in ("1", "true", "yes")
            if use_console:
                creds = flow.run_console()
            else:
                creds = flow.run_local_server(port=port)
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

    # Extract Meet link robustly: prefer hangoutLink, then conferenceData entryPoints (video), then htmlLink/location
    meet_link = created_event.get("hangoutLink")
    if not meet_link:
        conf = created_event.get("conferenceData") or {}
        for ep in conf.get("entryPoints", []) if conf else []:
            uri = ep.get("uri")
            ep_type = ep.get("entryPointType", "").lower()
            if uri and ("meet.google.com" in uri or ep_type == "video"):
                meet_link = uri
                break
    if not meet_link:
        meet_link = created_event.get("htmlLink") or created_event.get("location")

    if not meet_link:
        # Helpful debug output when no Meet link was returned
        print("Google Calendar event created without Meet link; event body:", created_event)

    event_id = created_event.get("id")
    return meet_link, event_id
