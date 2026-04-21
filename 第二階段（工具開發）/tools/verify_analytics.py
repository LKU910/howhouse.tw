#!/usr/bin/env python3
"""
verify_analytics.py — 驗證 deploy/ 所有 HTML 頁面都有正確注入 analytics 追蹤。

使用方式：
    python tools/verify_analytics.py          # 只檢查，有問題 exit code 1
    python tools/verify_analytics.py --fix    # 自動執行 inject.py --analytics 修復

每次大規模部署前跑一次，避免新頁面忘了加追蹤。
"""

import os
import re
import sys
import glob

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
DEPLOY_DIR = os.path.join(ROOT_DIR, 'deploy')

# 要檢查的必要標記與 script
REQUIRED_CHECKS = [
    ('ANALYTICS partial 標記', r'<!-- ANALYTICS:START -->'),
    ('GA4 Measurement ID', r'G-977GTZY37F'),
    ('Clarity Project ID', r'wezb0r47zq'),
    ('Vercel insights script', r'_vercel/insights/script\.js'),
    ('擇居統一追蹤封裝', r'zeju-analytics\.js'),
]

SKIP_FILES = {'google4b94b9fc9e6e305a.html'}


def collect_html_files():
    """收集所有需要檢查的 HTML 檔案"""
    return sorted(
        glob.glob(os.path.join(DEPLOY_DIR, '*.html')) +
        glob.glob(os.path.join(DEPLOY_DIR, 'step', '*.html')) +
        glob.glob(os.path.join(DEPLOY_DIR, 'guide', '*.html')) +
        glob.glob(os.path.join(DEPLOY_DIR, 'quiz-result', '*.html'))
    )


def verify_file(filepath):
    """回傳缺少的檢查項清單。空清單代表完全通過。"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            html = f.read()
    except Exception as e:
        return [f'讀取失敗：{e}']

    missing = []
    for label, pattern in REQUIRED_CHECKS:
        if not re.search(pattern, html):
            missing.append(label)

    # 額外檢查：路徑前綴正確（step/guide/quiz-result 應用 ../ 前綴）
    rel = os.path.relpath(filepath, DEPLOY_DIR)
    is_subfolder = os.sep in rel or '/' in rel
    zeju_script = re.search(r'src="([^"]*zeju-analytics\.js)"', html)
    if zeju_script:
        src = zeju_script.group(1)
        if is_subfolder and not src.startswith('../'):
            missing.append(f'zeju-analytics.js 缺少 ../ 前綴（實際：{src}）')
        elif not is_subfolder and src.startswith('../'):
            missing.append(f'zeju-analytics.js 多餘的 ../ 前綴（實際：{src}）')

    return missing


def main():
    fix_mode = '--fix' in sys.argv[1:]
    html_files = collect_html_files()

    print('═' * 60)
    print(f'  擇居 Analytics 覆蓋率驗證')
    print('═' * 60)
    print(f'📂 掃描 {len(html_files)} 個 HTML 檔案\n')

    missing_report = {}
    ok_count = 0

    for filepath in html_files:
        rel = os.path.relpath(filepath, DEPLOY_DIR)
        if os.path.basename(filepath) in SKIP_FILES:
            print(f'  ⏭  {rel} (跳過)')
            continue

        missing = verify_file(filepath)
        if missing:
            missing_report[rel] = missing
            print(f'  ❌ {rel}')
            for m in missing:
                print(f'       缺少：{m}')
        else:
            ok_count += 1

    print('\n' + '═' * 60)
    print(f'  結果：{ok_count} / {len(html_files)} 通過')
    print('═' * 60)

    if not missing_report:
        print('✅ 全站追蹤覆蓋率 100%。可以安心部署。')
        return 0

    print(f'⚠️  {len(missing_report)} 個檔案有問題\n')

    if fix_mode:
        print('🔧 嘗試用 inject.py 自動修復…\n')
        inject_script = os.path.join(ROOT_DIR, 'inject.py')
        ret = os.system(f'cd "{ROOT_DIR}" && python3 inject.py --analytics')
        if ret == 0:
            print('\n修復完成，請重跑 verify_analytics.py 確認。')
        return 1

    print('提示：用 `python tools/verify_analytics.py --fix` 自動執行 inject.py 修復')
    return 1


if __name__ == '__main__':
    sys.exit(main())
