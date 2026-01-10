Title: UI: Veeniksha theme, animations & OAuth improvements

Summary:
- Add a vibrant Veeniksha UI theme (colors, gradients, animated ornaments), improved header layout, and richer hover/entrance animations.
- Add two decorative SVG ornaments and responsive background animations.
- Improve Google Calendar OAuth flow support: configurable OAuth port (`GOOGLE_OAUTH_PORT`), console flow option (`GOOGLE_OAUTH_CONSOLE`), more robust Meet link extraction, and README updates.
- Add `credentials.json`/`token.json` to `.gitignore` and ensure they're not tracked.

Testing performed:
- Manual smoke tests: created students and scheduled sessions; OAuth authorization flow and Meet link creation verified when authorized.
- Visual QA: verified UI at desktop and mobile widths; validated animations, header alignment, and spacing.

Notes & follow-ups:
- `DEFAULT_MEET_LINK` support is available to use a fixed Meet URL (documented in README) — not recommended if you want per-event Meet links.
- Currently the code prints event body if no Meet link is returned for debugging; can be removed for production.
- Consider adding a logo/hero image and a theme toggle (light/dark) in a follow-up PR.

How to review:
1. Visit the branch: `feat/ui-theme` on GitHub: https://github.com/venkateshsoundar/veeniksha_academy/tree/feat/ui-theme
2. Check the changed files (UI and google_calendar improvements): `static/styles.css`, `templates/base.html`, `google_calendar.py`, `README.md`, `app.py`.
3. Run the app locally and test the schedule flow and OAuth behavior:
   - Delete `token.json` to force re-auth: `rm token.json` or `Remove-Item token.json` (PowerShell).
   - You can use `GOOGLE_OAUTH_CONSOLE=1` for console flow, or set `GOOGLE_OAUTH_PORT=8080` and register the redirect URI for Web credentials.

Suggested PR Body (paste into GitHub PR page):

**Summary**
- Add a vibrant Veeniksha UI theme (colors, gradients, animated ornaments), improved header layout, and richer hover/entrance animations.
- Add two decorative SVG ornaments and responsive background animations.
- Improve Google Calendar OAuth flow support: configurable OAuth port, console flow option, more robust Meet link extraction, and README updates.
- Add `credentials.json`/`token.json` to `.gitignore` and remove them from tracking if present.

**Testing**
- Manual smoke tests performed: scheduling sessions, OAuth authorization flow and Meet link creation (when authorized).
- UI verified on desktop and mobile widths.

**Notes**
- `DEFAULT_MEET_LINK` support is available for a fixed Meet URL (documented in README).
- Debug output prints the full event body when no Meet link is returned; remove in production if desired.

---

If you'd like, I can also open the PR page and paste this body into the form for you or create the PR automatically if you provide GitHub authentication (or if `gh` is available).