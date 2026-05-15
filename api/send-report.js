/**
 * Vercel Serverless Function: /api/send-report
 * 接收前端傳來的 PDF (base64) + email，透過 Resend API 寄出
 */

module.exports = async function handler(req, res) {
    // CORS
    res.setHeader('Access-Control-Allow-Origin', 'https://howhouse.tw');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
        return res.status(200).end();
    }

    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    const { email, pdfBase64, summary } = req.body;

    if (!email || !pdfBase64) {
        return res.status(400).json({ error: 'Missing email or pdfBase64' });
    }

    // 驗證 email 格式
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        return res.status(400).json({ error: 'Invalid email format' });
    }

    // 限制 PDF 大小（5MB base64 ≈ 3.75MB 檔案）
    if (pdfBase64.length > 5 * 1024 * 1024) {
        return res.status(400).json({ error: 'PDF too large' });
    }

    const RESEND_API_KEY = process.env.RESEND_API_KEY;
    if (!RESEND_API_KEY) {
        console.error('RESEND_API_KEY not configured');
        return res.status(500).json({ error: 'Email service not configured' });
    }

    // 組 email HTML
    const price = summary?.price || '—';
    const monthly = summary?.monthly || '—';
    const downPaymentPct = summary?.downPaymentPct || '—';

    const htmlContent = `
<!DOCTYPE html>
<html lang="zh-TW">
<head><meta charset="UTF-8"></head>
<body style="margin:0; padding:0; background:#F7F5F2; font-family:'Helvetica Neue',Arial,'Noto Sans TC',sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#F7F5F2; padding:40px 0;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff; border-radius:12px; overflow:hidden; box-shadow:0 2px 12px rgba(0,0,0,0.06);">

    <!-- Header -->
    <tr><td style="background:#3D3D3D; padding:32px 40px;">
        <h1 style="margin:0; font-size:22px; font-weight:700; color:#D4A96A; letter-spacing:0.1em;">擇居</h1>
        <p style="margin:6px 0 0; font-size:12px; color:#aaa; letter-spacing:0.15em;">先擇，後居</p>
    </td></tr>

    <!-- Body -->
    <tr><td style="padding:40px;">
        <h2 style="margin:0 0 8px; font-size:20px; color:#3D3D3D; font-weight:600;">你的財務診斷報告</h2>
        <p style="margin:0 0 24px; font-size:14px; color:#888; line-height:1.6;">
            附件是你剛才在擇居跑出來的完整報告。<br>
            建議存起來，跟家人或另一半一起看。
        </p>

        <!-- Summary Card -->
        <table width="100%" cellpadding="0" cellspacing="0" style="background:#FAF8F5; border-radius:10px; border:1px solid #E8E2DA;">
        <tr><td style="padding:24px;">
            <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                    <td style="font-size:13px; color:#999; padding-bottom:4px;">房屋總價</td>
                    <td style="font-size:13px; color:#999; padding-bottom:4px;" align="right">每月房貸</td>
                </tr>
                <tr>
                    <td style="font-size:28px; font-weight:700; color:#3D3D3D;">${price} 萬</td>
                    <td style="font-size:28px; font-weight:700; color:#B8956A;" align="right">${monthly} 元</td>
                </tr>
                <tr>
                    <td colspan="2" style="padding-top:12px; font-size:13px; color:#999;">
                        自備款 ${downPaymentPct}%
                    </td>
                </tr>
            </table>
        </td></tr>
        </table>

        <!-- CTA -->
        <table width="100%" cellpadding="0" cellspacing="0" style="margin-top:32px;">
        <tr><td align="center">
            <a href="https://howhouse.tw/calculator.html" style="
                display:inline-block; padding:14px 36px; border-radius:10px;
                background:#8A6820; color:#ffffff; text-decoration:none;
                font-size:14px; font-weight:500; letter-spacing:0.08em;">
                回到擇居，重新試算
            </a>
        </td></tr>
        </table>

        <p style="margin:32px 0 0; font-size:13px; color:#bbb; line-height:1.8;">
            數字會變，利率會調。這份報告是你在這個時間點的財務快照。<br>
            條件改變的時候，歡迎隨時回來重新跑一次。
        </p>
    </td></tr>

    <!-- Footer -->
    <tr><td style="background:#FAFAFA; padding:24px 40px; border-top:1px solid #F0EEEB;">
        <p style="margin:0; font-size:11px; color:#bbb; line-height:1.8;">
            擇居｜先擇，後居<br>
            <a href="https://howhouse.tw" style="color:#B8956A; text-decoration:none;">howhouse.tw</a><br><br>
            本報告僅供參考，不構成投資或財務建議。<br>
            <a href="https://howhouse.tw/privacy.html" style="color:#B8956A; text-decoration:none;">隱私政策</a>
            &nbsp;·&nbsp;
            如需退訂，請回覆此信件告知。
        </p>
    </td></tr>

</table>
</td></tr>
</table>
</body>
</html>`;

    try {
        const response = await fetch('https://api.resend.com/emails', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${RESEND_API_KEY}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                from: '擇居 <report@howhouse.tw>',
                to: [email],
                subject: '你的財務診斷報告｜擇居',
                html: htmlContent,
                attachments: [{
                    filename: '擇居_財務診斷報告.pdf',
                    content: pdfBase64,
                }],
            }),
        });

        const data = await response.json();

        if (!response.ok) {
            console.error('Resend API error:', data);
            return res.status(response.status).json({
                error: 'Email sending failed',
                detail: data.message || 'Unknown error'
            });
        }

        return res.status(200).json({ success: true, id: data.id });
    } catch (err) {
        console.error('Send email error:', err);
        return res.status(500).json({ error: 'Internal server error' });
    }
}
