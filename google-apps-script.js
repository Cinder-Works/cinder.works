// ============================================================
// Google Apps Script — Email Capture for cinder.works
// ============================================================
//
// SETUP:
// 1. Go to https://script.google.com
// 2. Open project "Cinder Email Capture" (or create new + paste this)
// 3. Deploy → Manage deployments → edit EXISTING web app → New version
//    (do NOT "New deployment" — that mints a new URL and breaks the site)
// 4. Execute as: Me · Who has access: Anyone
//
// Sheet: "Cinder Emails" (Drive) — columns Timestamp | Email | Source
// Site posts: { email, source: location.pathname }
// ============================================================

function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    var email = (data.email || '').toString().trim();
    var source = (data.source || '').toString().trim();

    // Basic email validation
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return ContentService
        .createTextOutput(JSON.stringify({ success: false, error: 'Invalid email' }))
        .setMimeType(ContentService.MimeType.JSON);
    }

    // Get or create the spreadsheet
    var sheetName = 'Cinder Emails';
    var files = DriveApp.getFilesByName(sheetName);
    var ss;

    if (files.hasNext()) {
      ss = SpreadsheetApp.open(files.next());
    } else {
      ss = SpreadsheetApp.create(sheetName);
      var fresh = ss.getActiveSheet();
      fresh.appendRow(['Timestamp', 'Email', 'Source']);
      fresh.getRange('A1:C1').setFontWeight('bold');
    }

    var sheet = ss.getActiveSheet();
    ensureSourceHeader_(sheet);

    // Check for duplicate (column B = Email)
    var existingEmails = sheet.getRange('B:B').getValues().flat();
    if (existingEmails.indexOf(email) !== -1) {
      return ContentService
        .createTextOutput(JSON.stringify({ success: true, note: 'Already subscribed' }))
        .setMimeType(ContentService.MimeType.JSON);
    }

    // Append timestamp, email, source (pathname / attribution)
    sheet.appendRow([new Date().toISOString(), email, source]);

    return ContentService
      .createTextOutput(JSON.stringify({ success: true }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ success: false, error: err.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

/** Ensure row 1 is Timestamp | Email | Source without wiping data. */
function ensureSourceHeader_(sheet) {
  var header = sheet.getRange(1, 1, 1, 3).getValues()[0];
  var a = (header[0] || '').toString();
  var b = (header[1] || '').toString();
  var c = (header[2] || '').toString();
  if (!a && !b) {
    sheet.getRange(1, 1, 1, 3).setValues([['Timestamp', 'Email', 'Source']]);
    sheet.getRange('A1:C1').setFontWeight('bold');
    return;
  }
  if (c.toLowerCase() !== 'source') {
    sheet.getRange(1, 3).setValue('Source').setFontWeight('bold');
  }
  if (a.toLowerCase() !== 'timestamp') {
    sheet.getRange(1, 1).setValue('Timestamp').setFontWeight('bold');
  }
  if (b.toLowerCase() !== 'email') {
    sheet.getRange(1, 2).setValue('Email').setFontWeight('bold');
  }
}

// Handle CORS preflight (GET requests)
function doGet(e) {
  return ContentService
    .createTextOutput(JSON.stringify({ status: 'ok', service: 'Cinder Email Capture', columns: ['Timestamp', 'Email', 'Source'] }))
    .setMimeType(ContentService.MimeType.JSON);
}
