const SHEET_NAME = 'Registrations';

function setup() {
  const props = PropertiesService.getScriptProperties();
  let spreadsheetId = props.getProperty('SPREADSHEET_ID');
  let ss;

  if (spreadsheetId) {
    ss = SpreadsheetApp.openById(spreadsheetId);
  } else {
    ss = SpreadsheetApp.create('Veeniksha Registrations');
    props.setProperty('SPREADSHEET_ID', ss.getId());
  }

  let sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) sheet = ss.insertSheet(SHEET_NAME);

  if (sheet.getLastRow() === 0) {
    sheet.appendRow([
      'Timestamp','Name','Email','Phone','Country','Age Group',
      'Learning Level','Preferred Schedule','Message','Source'
    ]);
    sheet.setFrozenRows(1);
  }

  Logger.log('Spreadsheet: ' + ss.getUrl());
  Logger.log('Spreadsheet ID: ' + ss.getId());
}

function doPost(e) {
  try {
    const lock = LockService.getScriptLock();
    lock.waitLock(10000);
    try {
      const data = JSON.parse(e.postData.contents || '{}');
      validate_(data);

      const props = PropertiesService.getScriptProperties();
      const spreadsheetId = props.getProperty('SPREADSHEET_ID');
      if (!spreadsheetId) throw new Error('Run setup() once before using the web app.');

      const ss = SpreadsheetApp.openById(spreadsheetId);
      let sheet = ss.getSheetByName(SHEET_NAME);
      if (!sheet) sheet = ss.insertSheet(SHEET_NAME);

      sheet.appendRow([
        new Date(), clean_(data.name), clean_(data.email), clean_(data.phone),
        clean_(data.country), clean_(data.ageGroup), clean_(data.level),
        clean_(data.schedule), clean_(data.message), 'Veeniksha Website'
      ]);

      sendConfirmation_(data);
      sendOwnerNotification_(data);

      return json_({ ok: true, message: 'Registration received successfully.' });
    } finally {
      lock.releaseLock();
    }
  } catch (err) {
    return json_({ ok: false, message: err.message || 'Unable to submit registration.' });
  }
}

function validate_(data) {
  if (!data.name || !data.email) throw new Error('Name and email are required.');
  const email = String(data.email).trim();
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) throw new Error('Please enter a valid email address.');
}

function clean_(value) {
  return String(value || '').trim().replace(/^([=+\-@])/, "'$1");
}

function sendConfirmation_(data) {
  const subject = 'Veeniksha Registration Received';
  const body = [
    'Dear ' + clean_(data.name) + ',',
    '',
    'Thank you for registering with Veeniksha Veena & Music Classes.',
    'We have received your details and will contact you shortly regarding class options, availability, and next steps.',
    '',
    'Preferred schedule: ' + (clean_(data.schedule) || 'Not specified'),
    'Learning level: ' + (clean_(data.level) || 'Not specified'),
    '',
    'Warm regards,',
    'Veeniksha Veena & Music Classes',
    'Canada: +1 825 962 9211',
    'WhatsApp: +91 959 766 6121'
  ].join('\n');

  MailApp.sendEmail({ to: clean_(data.email), subject: subject, body: body, name: 'Veeniksha' });
}

function sendOwnerNotification_(data) {
  const ownerEmail = Session.getEffectiveUser().getEmail();
  if (!ownerEmail) return;
  const subject = 'New Veeniksha Registration - ' + clean_(data.name);
  const body = [
    'A new registration was submitted from the Veeniksha website.',
    '',
    'Name: ' + clean_(data.name),
    'Email: ' + clean_(data.email),
    'Phone: ' + clean_(data.phone),
    'Country: ' + clean_(data.country),
    'Age Group: ' + clean_(data.ageGroup),
    'Level: ' + clean_(data.level),
    'Preferred Schedule: ' + clean_(data.schedule),
    'Message: ' + clean_(data.message)
  ].join('\n');

  MailApp.sendEmail({ to: ownerEmail, subject: subject, body: body, name: 'Veeniksha Website' });
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
