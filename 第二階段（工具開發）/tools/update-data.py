#!/usr/bin/env python3
"""
HomeRUN 好宅通 — 全站時效性數據更新工具

使用方式：
  1. 編輯 deploy/data-config.json 中的數值
  2. 執行 python3 update-data.py
  3. 腳本會掃描所有相關 HTML，找出與 data-config.json 不一致的地方
  4. 產出報告，告訴你哪些檔案的哪些數字需要人工確認

注意：此腳本「只做檢查、不做自動替換」，避免誤改上下文。
     確認報告內容後，再手動或用 Claude 協助修正。
"""

import json
import os
import re
import sys
from datetime import datetime

DEPLOY_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'deploy')
CONFIG_PATH = os.path.join(DEPLOY_DIR, 'data-config.json')

def load_config():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def scan_file(filepath, patterns):
    """Scan a file for all patterns, return matches with line numbers."""
    results = []
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for i, line in enumerate(lines, 1):
        for label, pattern in patterns:
            if re.search(pattern, line):
                results.append({
                    'line': i,
                    'label': label,
                    'text': line.strip()[:120]
                })
    return results

def build_check_patterns(config):
    """Build regex patterns from config values to search in HTML files."""
    checks = {}

    for key, val in config.items():
        if key.startswith('_'):
            continue
        if not isinstance(val, dict):
            continue

        files = val.get('files', [])
        patterns = []

        for field, value in val.items():
            if field in ('files', '來源', '說明', '計算基礎'):
                continue
            # Extract numbers from the value string
            # e.g. "1.775%" -> search for 1.775
            nums = re.findall(r'[\d,]+\.?\d*', str(value))
            for num in nums:
                clean_num = num.replace(',', '')
                if len(clean_num) >= 2:  # skip single digits
                    patterns.append((f"{key}.{field}={value}", re.escape(clean_num)))

        if patterns:
            checks[key] = {'files': files, 'patterns': patterns}

    return checks

def main():
    config = load_config()
    last_updated = config.get('_last_updated', 'unknown')
    next_review = config.get('_next_review', 'unknown')

    print("=" * 60)
    print("HomeRUN 好宅通 — 數據一致性檢查報告")
    print(f"Config 最後更新: {last_updated}")
    print(f"下次審閱日期: {next_review}")
    print(f"執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    checks = build_check_patterns(config)
    all_issues = []

    for category, info in checks.items():
        print(f"\n--- {category} ---")
        expected_files = info['files']
        patterns = info['patterns']

        # Check expected files
        for rel_path in expected_files:
            full_path = os.path.join(DEPLOY_DIR, rel_path)
            if not os.path.exists(full_path):
                print(f"  ⚠️  {rel_path} 不存在!")
                continue

            results = scan_file(full_path, patterns)
            if results:
                print(f"  ✅ {rel_path}: 找到 {len(results)} 處引用")
                for r in results:
                    print(f"     L{r['line']}: [{r['label']}] {r['text']}")
            else:
                print(f"  ❌ {rel_path}: 未找到相關數據 — 可能已被移除或格式變更")
                all_issues.append(f"{category} 在 {rel_path} 中找不到")

    # Also scan ALL html files for common time-sensitive patterns
    print("\n\n--- 全站掃描：可能過時的數據 ---")
    time_sensitive = [
        ("利率數字", r'\d+\.\d+%'),
        ("年份引用", r'202[0-9]\s*年'),
        ("截止日期", r'截止|到期|deadline'),
        ("央行政策", r'信用管制|央行'),
    ]

    for root, dirs, files in os.walk(DEPLOY_DIR):
        for f in files:
            if not f.endswith('.html'):
                continue
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, DEPLOY_DIR)
            results = scan_file(full_path, time_sensitive)
            rate_hits = [r for r in results if r['label'] == '利率數字']
            if rate_hits:
                print(f"  {rel_path}: {len(rate_hits)} 處利率引用")

    # Summary
    print("\n" + "=" * 60)
    if all_issues:
        print(f"⚠️  發現 {len(all_issues)} 個潛在問題：")
        for issue in all_issues:
            print(f"  - {issue}")
    else:
        print("✅ 所有預期數據均已在對應頁面中找到。")

    print(f"\n📋 下次審閱日期: {next_review}")
    print("   建議每季（或政策變動時）執行此腳本。")
    print("=" * 60)

if __name__ == '__main__':
    main()
