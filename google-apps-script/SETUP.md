# Veeniksha Registration Backend Setup

This keeps the public site on GitHub Pages while using Google Apps Script as the free backend for registrations.

1. Open https://script.google.com and create a new project named **Veeniksha Registration Backend**.
2. Replace the default `Code.gs` with the contents of this repository's `google-apps-script/Code.gs`.
3. Run the `setup()` function once and approve the requested Google permissions. The function creates a Google Spreadsheet named **Veeniksha Registrations** with a `Registrations` worksheet.
4. In Apps Script choose **Deploy → New deployment → Web app**.
5. Set **Execute as: Me** and **Who has access: Anyone**.
6. Deploy, approve permissions, then copy the `/exec` web-app URL.
7. In the website's `script.js`, replace `PASTE_YOUR_GOOGLE_APPS_SCRIPT_WEB_APP_URL_HERE` with that `/exec` URL.
8. Commit/push the change to the `gh-pages` branch. GitHub Pages will update automatically.

After setup, every successful website registration:
- is appended to the Google Spreadsheet,
- sends a confirmation email to the registrant,
- sends a notification email to the Google account that owns the Apps Script project.

Keep the Apps Script deployment URL public only as an endpoint. Do not put API keys or other secrets in the GitHub Pages repository.
