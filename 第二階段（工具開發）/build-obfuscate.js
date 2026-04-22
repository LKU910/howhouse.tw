#!/usr/bin/env node
/**
 * 擇居 — JS 混淆工具
 * 將 calculator.html 中的 <script> 區塊做混淆處理
 * 跳過 JSON-LD、外部 SDK（LIFF / Firebase）、以及太短的 inline script
 *
 * 用法：node build-obfuscate.js
 * 輸出：deploy/calculator.html（就地覆蓋，所以只在 CI/deploy 時執行）
 */

const fs = require('fs');
const path = require('path');
const JavaScriptObfuscator = require('javascript-obfuscator');

const SRC = path.join(__dirname, 'deploy', 'calculator.html');

// ── 混淆設定 ─────────────────────────────────────
// 平衡保護程度與效能，不要太激進以免影響行動端速度
const OBF_OPTIONS = {
    compact: true,
    controlFlowFlattening: true,
    controlFlowFlatteningThreshold: 0.4,
    deadCodeInjection: true,
    deadCodeInjectionThreshold: 0.2,
    debugProtection: false,            // 不擋 devtools（會影響自己除錯）
    identifierNamesGenerator: 'hexadecimal',
    renameGlobals: false,              // 不改全域名（避免與 DOM id 衝突）
    selfDefending: false,              // 不加自我保護（會影響效能）
    stringArray: true,
    stringArrayThreshold: 0.75,
    stringArrayEncoding: ['base64'],
    splitStrings: true,
    splitStringsChunkLength: 10,
    transformObjectKeys: true,
    unicodeEscapeSequence: false,
    // 保留這些全域名不被重命名
    reservedNames: [
        'state', 'calculate', 'formatNumber', 'formatWanFromYuan',
        'calcMonthlyPayment', 'calcGracePayment', 'toggleSection',
        'updateAssetTotal', 'applyAssetToDownPayment', 'confirmApplyAsset',
        'updateAssessedHint', 'updateTaxDisplay', 'generatePDF',
        'renderStressTest', 'renderPriceSpectrum', 'renderLifeImpact',
        'liff', 'firebase', 'lucide', 'html2canvas', 'jspdf',
        'LineLiff', 'FirebaseSync',
        'zeju',  // analytics
    ],
    reservedStrings: [
        'firebaseConfig', 'liffId',
    ],
};

// ── 主程式 ────────────────────────────────────────
let html = fs.readFileSync(SRC, 'utf8');

// 匹配所有 <script> 區塊（含屬性）
const SCRIPT_RE = /(<script\b([^>]*)>)([\s\S]*?)(<\/script>)/gi;
let count = 0;

html = html.replace(SCRIPT_RE, (match, openTag, attrs, code, closeTag) => {
    // 跳過 JSON-LD
    if (attrs.includes('application/ld+json')) return match;
    // 跳過外部 src script
    if (attrs.includes('src=')) return match;
    // 跳過太短的 script（< 200 字元，通常是 inline 初始化）
    if (code.trim().length < 200) return match;

    try {
        const result = JavaScriptObfuscator.obfuscate(code, OBF_OPTIONS);
        count++;
        return openTag + result.getObfuscatedCode() + closeTag;
    } catch (e) {
        console.error('⚠ 混淆失敗，保留原始碼:', e.message);
        return match;
    }
});

fs.writeFileSync(SRC, html, 'utf8');
console.log(`✅ 已混淆 ${count} 個 script 區塊`);
console.log(`   檔案大小: ${(fs.statSync(SRC).size / 1024).toFixed(0)} KB`);
