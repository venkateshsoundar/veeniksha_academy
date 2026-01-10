# Changelog

All notable changes to this project will be documented in this file.

## [v0.1.0] - 2026-01-10
### Added
- New Veeniksha UI theme with vibrant colors, gradients, and animated decorative ornaments.
- Improved header layout, centered title and navigation, and richer hover/entrance animations.
- Google Calendar OAuth improvements: configurable OAuth port (`GOOGLE_OAUTH_PORT`), console flow (`GOOGLE_OAUTH_CONSOLE`), and more robust Meet link extraction.
- `DEFAULT_MEET_LINK` support (optional) and README documentation.
- Artifacts from smoke test: `artifacts/students_post.html`, `artifacts/sessions_post.html`, `artifacts/session_4.html` (showing created session and Meet link).

### Changed
- Updated README with setup instructions and OAuth notes.

### Notes
- Delete `token.json` to force re-authorization when changing OAuth settings.
