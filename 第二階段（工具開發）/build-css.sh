#!/bin/bash
# 擇居 - 重新產生 Tailwind CSS
# 使用時機：當你在 HTML 中新增了之前沒用過的 Tailwind class 時
# 前置需求：npm install tailwindcss@3
#
# 用法：在擇居資料夾根目錄執行
#   ./build-css.sh

cd "$(dirname "$0")"

npx tailwindcss \
  -i input.css \
  -o deploy/tailwind.css \
  --config tailwind.config.js \
  --minify

echo "✅ tailwind.css 已更新 ($(wc -c < deploy/tailwind.css) bytes)"

# ── JS 混淆（僅在 Vercel CI 環境執行） ──
if [ "$VERCEL" = "1" ] || [ "$CI" = "true" ]; then
  echo "🔒 正在混淆 calculator.html JS..."
  node build-obfuscate.js
fi
