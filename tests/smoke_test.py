import re
import time
import datetime
import requests

BASE = "http://127.0.0.1:5000"
ARTIFACTS_DIR = "artifacts"

s = requests.Session()

print("Creating test student...")
r = s.post(f"{BASE}/students/new", data={"full_name": "Smoke Tester", "email": "smoke+1@example.com"})
if r.status_code not in (200, 302):
    print("Failed to create student", r.status_code, r.text[:200])
    raise SystemExit(1)

print("Fetching students list to find student id...")
r = s.get(f"{BASE}/students")
if r.status_code != 200:
    print("Failed to load students page", r.status_code)
    raise SystemExit(1)

# Find first edit link (students ordered by created_at desc, so newest first)
m = re.search(r'href="/students/(\d+)/edit"', r.text)
if not m:
    print("Could not find student id on students page")
    raise SystemExit(1)
student_id = m.group(1)
print("Found student id:", student_id)

start_time = (datetime.datetime.utcnow() + datetime.timedelta(days=1)).replace(second=0, microsecond=0).isoformat()
print("Scheduling a session at", start_time)

r = s.post(
    f"{BASE}/schedule",
    data={
        "start_time": start_time,
        "duration_mins": "60",
        "topic": "Smoke Test",
        "timezone": "Asia/Kolkata",
        "student_ids": student_id,
    },
    allow_redirects=True,
)

if r.status_code not in (200, 302):
    print("Failed to schedule session", r.status_code, r.text[:300])
    raise SystemExit(1)

print("Scheduled. Looking for Meet link on sessions page...")
r = s.get(f"{BASE}/sessions")
if r.status_code != 200:
    print("Failed to load sessions page", r.status_code)
    raise SystemExit(1)

# Look for Join Meet link
m = re.search(r'href="(https?://meet\.google\.com/[^"]+)"', r.text)
if m:
    meet = m.group(1)
    print("Success — Meet link found on sessions page:", meet)
else:
    # fallback: find session detail link and inspect it
    m2 = re.search(r'href="/sessions/(\d+)"', r.text)
    if not m2:
        print("No session links found on sessions page")
        raise SystemExit(1)
    session_id = m2.group(1)
    print("Fetching session detail for id", session_id)
    r2 = s.get(f"{BASE}/sessions/{session_id}")
    if r2.status_code != 200:
        print("Failed to load session detail", r2.status_code)
        raise SystemExit(1)
    m3 = re.search(r'href="(https?://meet\.google\.com/[^"]+)"', r2.text)
    if m3:
        meet = m3.group(1)
        print("Success — Meet link found in session details:", meet)
    else:
        print("No Meet link found. Saving session HTML to artifacts/smoke_session.html for inspection.")
        import os
        os.makedirs(ARTIFACTS_DIR, exist_ok=True)
        open(os.path.join(ARTIFACTS_DIR, "smoke_session.html"), "w", encoding="utf-8").write(r2.text)
        raise SystemExit(1)

print("Smoke test completed.")