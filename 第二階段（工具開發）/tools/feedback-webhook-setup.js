/**
 * 擇居 — 決策性格回饋 Google Apps Script
 *
 * 部署步驟：
 * 1. 到 https://script.google.com 建立新專案
 * 2. 貼上這段程式碼
 * 3. 點選「部署 → 新增部署作業」
 * 4. 類型選「網頁應用程式」
 * 5. 存取權設為「所有人」
 * 6. 部署後複製 URL
 * 7. 把 URL 貼到 quiz.html 的 FEEDBACK_WEBHOOK 變數
 *
 * Google Sheet 會自動建立，欄位如下：
 * 時間戳記 | 人格類型 | 回饋 | A分 | B分 | C分 | D分 | 裝置
 */

const SHEET_NAME = '決策性格回饋';

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    let sheet = ss.getSheetByName(SHEET_NAME);

    // 第一次執行：自動建立工作表 + 表頭
    if (!sheet) {
      sheet = ss.insertSheet(SHEET_NAME);
      sheet.appendRow([
        '時間戳記', '人格類型', '回饋',
        'A 決策風格', 'B 思考模式', 'C 風險態度', 'D 掌控感',
        '裝置'
      ]);
      sheet.getRange(1, 1, 1, 8).setFontWeight('bold');
    }

    const scores = data.scores || {};
    const device = (data.userAgent || '').includes('Mobile') ? '手機' : '桌面';

    sheet.appendRow([
      data.timestamp || new Date().toISOString(),
      data.persona || '',
      data.feedback || '',
      scores.A || 0,
      scores.B || 0,
      scores.C || 0,
      scores.D || 0,
      device
    ]);

    return ContentService
      .createTextOutput(JSON.stringify({ status: 'ok' }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ status: 'error', message: err.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

// GET 請求用於測試
function doGet() {
  return ContentService
    .createTextOutput('擇居回饋 webhook 運作中')
    .setMimeType(ContentService.MimeType.TEXT);
}
