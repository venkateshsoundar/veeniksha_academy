# Veena Music Academy MVP

## Overview
This MVP helps manage students, schedule sessions, track attendance, and view dashboard insights. It uses Flask + SQLite for a simple, local-first workflow and is designed to switch to Postgres later via a `DATABASE_URL` config change.

## Features
- Admin login (single account for MVP)
- Student management (create, update, deactivate)
- Schedule sessions with multi-select student picker and over-capacity warnings
- Google Calendar integration for Meet links (with manual fallback)
- Session detail management (invite + attendance statuses, remove denied students)
- Dashboard stats and session history

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
flask --app app.py init-db
python seed.py
flask --app app.py run
```

Visit `http://127.0.0.1:5000`.

## Google Calendar Setup (Optional)
1. Create a Google Cloud project.
2. Enable the Google Calendar API.
3. Configure an OAuth Consent screen for local/testing.
4. Create OAuth Client ID (Desktop app) and download `credentials.json` into the repo root.
5. Set `GOOGLE_CREDENTIALS_FILE` and `GOOGLE_TOKEN_FILE` in `.env`.
6. When you schedule a session, the OAuth flow will open in your browser to authorize. A `token.json` file will be saved locally.

If Google Calendar is not configured, you can enter a manual Meet link during scheduling.

## Switching to Postgres Later
Update `DATABASE_URL` to a Postgres connection string, e.g.:
```
DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/veeniksha
```
