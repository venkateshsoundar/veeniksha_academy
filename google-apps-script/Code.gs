const SHEET_NAME = 'Website Registrations';
const ACADEMY_NAME = 'Veeniksha Veena & Music Academy';
const OWNER_EMAIL = 'YOUR_VEENIKSHA_EMAIL@gmail.com';

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents || '{}');
    if (data.website) return json_({ ok: true });

    const ss = SpreadsheetApp.getActiveSpreadsheet();
    let sheet = ss.getSheetByName(SHEET_NAME);
    if (!sheet) {
      sheet = ss.insertSheet(SHEET_NAME);
      sheet.appendRow([
        'Timestamp',
        'Full Name',
        'Email Address',
        'Phone / WhatsApp Number',
        'Country / Time Zone',
        'Age Group',
        'Have you learned Veena before?',
        'Preferred Days',
        'Preferred Time (Your Time Zone)',
        'Learning Goals / Message',
        'Source'
      ]);
      sheet.setFrozenRows(1);
    }

    sheet.appendRow([
      new Date(),
      data.studentName || '',
      data.email || '',
      data.phone || '',
      data.country || '',
      data.ageGroup || '',
      data.experience || '',
      data.preferredDays || '',
      data.timing || '',
      data.goals || '',
      data.source || 'Website'
    ]);

    if (data.email) {
      const subject = 'Welcome to Veeniksha — registration received';
      const html = `<div style="font-family:Arial,sans-serif;color:#172033;max-width:620px;margin:auto"><div style="background:#071b3a;color:white;padding:28px;border-radius:18px 18px 0 0"><h1 style="margin:0;font-family:Georgia,serif">Veeniksha Veena & Music Academy</h1><p style="color:#e7b85d;margin:6px 0 0">Traditional music. Personal guidance. Global learning.</p></div><div style="padding:28px;border:1px solid #eadfce;border-top:0"><p>Dear ${escapeHtml_(data.studentName || 'Student')},</p><p>Thank you for registering with Veeniksha. We have received your details and will contact you shortly to discuss your learning level, preferred days, timing and next steps.</p><p>Warm regards,<br><b>Mrs. Monisha</b><br>Veeniksha Veena & Music Academy</p></div></div>`;
      GmailApp.sendEmail(data.email, subject, 'Thank you for registering with Veeniksha Veena & Music Academy.', { htmlBody: html, name: ACADEMY_NAME });
    }

    if (OWNER_EMAIL && !OWNER_EMAIL.startsWith('YOUR_')) {
      GmailApp.sendEmail(
        OWNER_EMAIL,
        'New Veeniksha registration — ' + (data.studentName || 'Student'),
        JSON.stringify(data, null, 2),
        { name: ACADEMY_NAME }
      );
    }

    return json_({ ok: true });
  } catch (err) {
    return json_({ ok: false, error: String(err) });
  }
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

function escapeHtml_(s) {
  return String(s).replace(/[&<>'"]/g, c => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', "'":'&#39;', '"':'&quot;' }[c]));
}