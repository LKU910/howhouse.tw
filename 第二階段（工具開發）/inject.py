#!/usr/bin/env python3
"""
inject.py — 從 _partials/ 注入統一的 nav、footer、analytics 到 deploy/ 所有 HTML 頁面。

使用方式：
    python inject.py              # 注入 nav + footer + analytics
    python inject.py --nav        # 只注入 nav
    python inject.py --footer     # 只注入 footer
    python inject.py --analytics  # 只注入 analytics
    python inject.py --dry        # 預覽模式，不寫入檔案

工作原理：
    1. 首次執行：用 regex 找到現有的 nav/footer，替換為 partial 內容（含標記）
       analytics 則插入在 </head> 之前
    2. 後續執行：用標記（NAV:START/END, FOOTER:START/END, ANALYTICS:START/END）定位

路徑規則：
    - deploy/ 根目錄頁面 → href 不加前綴
    - deploy/step/、deploy/guide/、deploy/quiz-result/ → href 加 ../ 前綴
"""

import os
import re
import sys
import glob

# ─── 設定 ───────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEPLOY_DIR = os.path.join(SCRIPT_DIR, 'deploy')
PARTIALS_DIR = os.path.join(SCRIPT_DIR, '_partials')

SKIP_FILES = {'google4b94b9fc9e6e305a.html'}  # 非網站頁面

# ─── 工具函式 ──────────────────────────────────────────

def find_closing_tag(html, open_tag_pos, tag_name='div'):
    """從 open_tag_pos 開始，找到對應的 closing tag 位置（含 closing tag 本身）"""
    depth = 0
    i = open_tag_pos
    open_pat = re.compile(rf'<{tag_name}[\s>]')
    close_pat = re.compile(rf'</{tag_name}>')
    while i < len(html):
        open_m = open_pat.search(html, i)
        close_m = close_pat.search(html, i)
        if close_m is None:
            return -1
        if open_m and open_m.start() < close_m.start():
            depth += 1
            i = open_m.end()
        else:
            depth -= 1
            if depth == 0:
                return close_m.end()
            i = close_m.end()
    return -1


def get_prefix(filepath):
    """根據檔案位置決定路徑前綴"""
    rel = os.path.relpath(filepath, DEPLOY_DIR)
    if os.sep in rel or '/' in rel:
        return '../'
    return ''


def render_partial(template, prefix):
    """將 {{PREFIX}} 替換為實際路徑前綴"""
    return template.replace('{{PREFIX}}', prefix)


# ─── Nav 注入 ──────────────────────────────────────────

def inject_nav(html, nav_template, prefix):
    """注入 nav partial，回傳 (new_html, changed)"""
    rendered = render_partial(nav_template, prefix)

    # 方式 1：已有標記 → 直接替換標記之間的內容
    marker_pat = re.compile(r'<!-- NAV:START -->.*?<!-- NAV:END -->', re.DOTALL)
    if marker_pat.search(html):
        new_html = marker_pat.sub(rendered.strip(), html)
        return new_html, new_html != html

    # 方式 2：首次執行 → 用 regex 找現有 nav + mobileMenu
    nav_start = html.find('<nav class="w-full px-6')
    if nav_start == -1:
        # 嘗試其他 nav 模式
        nav_start = html.find('<nav class="w-full')
    if nav_start == -1:
        return html, False

    # 往前捕捉可能的 HTML 註解（如 <!-- Nav --> 或 <!-- Navigation -->）
    pre_comment_start = nav_start
    before_nav = html[:nav_start].rstrip()
    comment_match = re.search(r'(<!--\s*(Nav|Navigation)\s*-->\s*)$', before_nav)
    if comment_match:
        pre_comment_start = before_nav[:comment_match.start()].rstrip().__len__()
        # 保留換行
        pre_comment_start = comment_match.start() + (nav_start - len(before_nav) - (len(html[:nav_start]) - len(html[:nav_start].rstrip())))

    # 找 </nav>
    nav_close = html.find('</nav>', nav_start)
    if nav_close == -1:
        return html, False
    nav_end = nav_close + len('</nav>')

    # 找 mobileMenu div（如果存在）
    mobile_end = nav_end
    after_nav = html[nav_end:]
    mobile_match = re.search(r'\s*(?:<!--\s*Mobile Menu\s*-->\s*)?<div id="mobileMenu"', after_nav)
    if mobile_match:
        mobile_div_start = nav_end + mobile_match.start()
        mobile_div_open = html.find('<div id="mobileMenu"', mobile_div_start)
        if mobile_div_open != -1:
            mobile_end = find_closing_tag(html, mobile_div_open, 'div')
            if mobile_end == -1:
                mobile_end = nav_end

    # 找到完整區塊的起點（含前面的註解和空白）
    block_start = nav_start
    # 往前找到行首
    line_start = html.rfind('\n', 0, nav_start)
    if line_start != -1:
        between = html[line_start+1:nav_start]
        if between.strip() == '' or between.strip().startswith('<!--'):
            # 檢查是否有註解行
            check_pos = line_start
            while check_pos > 0:
                prev_line_start = html.rfind('\n', 0, check_pos)
                if prev_line_start == -1:
                    break
                line_content = html[prev_line_start+1:check_pos].strip()
                if re.match(r'<!--\s*(Nav|Navigation)\s*-->', line_content):
                    block_start = prev_line_start + 1
                    break
                elif line_content == '':
                    check_pos = prev_line_start
                    continue
                else:
                    break
            if block_start == nav_start:
                block_start = line_start + 1

    # 替換
    new_html = html[:block_start] + rendered.strip() + '\n' + html[mobile_end:].lstrip('\n')
    return new_html, True


# ─── Analytics 注入 ────────────────────────────────────

def inject_analytics(html, analytics_template, prefix):
    """注入 analytics partial 到 </head> 前面，回傳 (new_html, changed)"""
    rendered = render_partial(analytics_template, prefix)

    # 方式 1：已有標記 → 直接替換標記之間的內容
    marker_pat = re.compile(r'<!-- ANALYTICS:START -->.*?<!-- ANALYTICS:END -->', re.DOTALL)
    if marker_pat.search(html):
        new_html = marker_pat.sub(rendered.strip(), html)
        return new_html, new_html != html

    # 方式 2：首次執行 → 插入到 </head> 之前
    head_close = html.find('</head>')
    if head_close == -1:
        return html, False

    # 找到 </head> 那一行的起始，保留原本的縮排
    line_start = html.rfind('\n', 0, head_close)
    indent = html[line_start+1:head_close] if line_start != -1 else ''
    # 若該行前面只有空白，使用其縮排；否則用預設縮排
    if indent.strip():
        indent = ''  # 表示 </head> 不在獨立一行，用無縮排插入

    insertion = rendered.strip() + '\n' + indent
    new_html = html[:head_close] + insertion + html[head_close:]
    return new_html, True


# ─── Footer 注入 ───────────────────────────────────────

def inject_footer(html, footer_template, prefix):
    """注入 footer partial，回傳 (new_html, changed)"""
    rendered = render_partial(footer_template, prefix)

    # 方式 1：已有標記
    marker_pat = re.compile(r'<!-- FOOTER:START -->.*?<!-- FOOTER:END -->', re.DOTALL)
    if marker_pat.search(html):
        new_html = marker_pat.sub(rendered.strip(), html)
        return new_html, new_html != html

    # 方式 2：首次執行 → 找 <footer...>...</footer>
    footer_match = re.search(r'<footer[\s>]', html)
    if not footer_match:
        return html, False

    footer_start = footer_match.start()
    footer_close = find_closing_tag(html, footer_start, 'footer')
    if footer_close == -1:
        return html, False

    # 往前找行首和可能的註解
    block_start = footer_start
    line_start = html.rfind('\n', 0, footer_start)
    if line_start != -1:
        check_pos = line_start
        while check_pos > 0:
            prev_line_start = html.rfind('\n', 0, check_pos)
            if prev_line_start == -1:
                break
            line_content = html[prev_line_start+1:check_pos].strip()
            if re.match(r'<!--\s*Footer\s*-->', line_content):
                block_start = prev_line_start + 1
                break
            elif line_content == '':
                check_pos = prev_line_start
                continue
            else:
                break
        if block_start == footer_start:
            block_start = line_start + 1

    new_html = html[:block_start] + rendered.strip() + '\n' + html[footer_close:].lstrip('\n')
    return new_html, True


# ─── 主程式 ────────────────────────────────────────────

def collect_html_files():
    """收集所有需要注入的 HTML 檔案（deploy/ + 子資料夾）"""
    return sorted(
        glob.glob(os.path.join(DEPLOY_DIR, '*.html')) +
        glob.glob(os.path.join(DEPLOY_DIR, 'step', '*.html')) +
        glob.glob(os.path.join(DEPLOY_DIR, 'guide', '*.html')) +
        glob.glob(os.path.join(DEPLOY_DIR, 'quiz-result', '*.html'))
    )


def main():
    args = set(sys.argv[1:])
    dry_run = '--dry' in args

    # 若沒指定任何 flag，預設全部都做
    specific = {'--nav', '--footer', '--analytics'} & args
    if not specific:
        do_nav = do_footer = do_analytics = True
    else:
        do_nav = '--nav' in args
        do_footer = '--footer' in args
        do_analytics = '--analytics' in args

    # 讀取 partial 檔案
    nav_template = footer_template = analytics_template = ''
    if do_nav:
        with open(os.path.join(PARTIALS_DIR, 'nav.html'), 'r', encoding='utf-8') as f:
            nav_template = f.read()
    if do_footer:
        with open(os.path.join(PARTIALS_DIR, 'footer.html'), 'r', encoding='utf-8') as f:
            footer_template = f.read()
    if do_analytics:
        with open(os.path.join(PARTIALS_DIR, 'analytics.html'), 'r', encoding='utf-8') as f:
            analytics_template = f.read()

    # 收集所有 HTML 檔案
    html_files = collect_html_files()

    print(f'📂 找到 {len(html_files)} 個 HTML 檔案')
    if dry_run:
        print('🔍 預覽模式（不寫入）\n')
    else:
        print()

    nav_count = 0
    footer_count = 0
    analytics_count = 0
    errors = []

    for filepath in html_files:
        filename = os.path.relpath(filepath, DEPLOY_DIR)
        basename = os.path.basename(filepath)

        if basename in SKIP_FILES:
            print(f'  ⏭  {filename}: 跳過（非網站頁面）')
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            html = f.read()

        prefix = get_prefix(filepath)
        original = html

        # 注入 nav
        nav_changed = False
        if do_nav:
            html, nav_changed = inject_nav(html, nav_template, prefix)
            if nav_changed:
                nav_count += 1

        # 注入 footer
        footer_changed = False
        if do_footer:
            html, footer_changed = inject_footer(html, footer_template, prefix)
            if footer_changed:
                footer_count += 1

        # 注入 analytics
        analytics_changed = False
        if do_analytics:
            html, analytics_changed = inject_analytics(html, analytics_template, prefix)
            if analytics_changed:
                analytics_count += 1

        # 報告
        status = []
        if nav_changed:
            status.append('nav')
        if footer_changed:
            status.append('footer')
        if analytics_changed:
            status.append('analytics')

        if status:
            marker = '✓' if not dry_run else '👁'
            print(f'  {marker} {filename}: 更新 {", ".join(status)}  (prefix="{prefix}")')
            if not dry_run:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(html)
        else:
            print(f'  — {filename}: 無變更')

    # 摘要
    print(f'\n{"═" * 50}')
    print(f'✅ 完成！')
    if do_nav:
        print(f'   Nav 更新：{nav_count} 個檔案')
    if do_footer:
        print(f'   Footer 更新：{footer_count} 個檔案')
    if do_analytics:
        print(f'   Analytics 更新：{analytics_count} 個檔案')
    if dry_run:
        print(f'   ⚠️  預覽模式，未寫入任何檔案')

    # 驗證
    if not dry_run:
        print(f'\n🔍 驗證中...')
        verify_errors = verify(html_files, do_nav, do_footer, do_analytics)
        if verify_errors:
            print(f'\n⚠️  發現 {len(verify_errors)} 個問題：')
            for err in verify_errors:
                print(f'   ❌ {err}')
        else:
            print(f'   ✅ 全部通過！')


def verify(html_files, check_nav, check_footer, check_analytics=False):
    """驗證所有頁面的 nav/footer/analytics 是否正確"""
    errors = []
    for filepath in html_files:
        filename = os.path.relpath(filepath, DEPLOY_DIR)
        basename = os.path.basename(filepath)
        if basename in SKIP_FILES:
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            html = f.read()

        # step、guide、quiz-result 子頁面可能沒有 nav/footer（走自己的佈局），不驗證
        rel = os.path.relpath(filepath, DEPLOY_DIR)
        is_sub_layout = any(rel.startswith(d + os.sep) or rel.startswith(d + '/')
                            for d in ('quiz-result',))

        if check_nav and not is_sub_layout:
            if '<!-- NAV:START -->' not in html:
                errors.append(f'{filename}: 缺少 NAV:START 標記')
            elif '<!-- NAV:END -->' not in html:
                errors.append(f'{filename}: 缺少 NAV:END 標記')
            elif html.count('<!-- NAV:START -->') > 1:
                errors.append(f'{filename}: 有多個 NAV:START 標記')

        if check_footer and not is_sub_layout:
            if '<!-- FOOTER:START -->' not in html:
                errors.append(f'{filename}: 缺少 FOOTER:START 標記')
            elif '<!-- FOOTER:END -->' not in html:
                errors.append(f'{filename}: 缺少 FOOTER:END 標記')
            elif html.count('<!-- FOOTER:START -->') > 1:
                errors.append(f'{filename}: 有多個 FOOTER:START 標記')

        # analytics 所有頁面都要有
        if check_analytics:
            if '<!-- ANALYTICS:START -->' not in html:
                errors.append(f'{filename}: 缺少 ANALYTICS:START 標記')
            elif '<!-- ANALYTICS:END -->' not in html:
                errors.append(f'{filename}: 缺少 ANALYTICS:END 標記')
            elif html.count('<!-- ANALYTICS:START -->') > 1:
                errors.append(f'{filename}: 有多個 ANALYTICS:START 標記')

        # 檢查路徑前綴
        prefix = get_prefix(filepath)
        if check_nav and '<!-- NAV:START -->' in html:
            nav_section = re.search(r'<!-- NAV:START -->(.+?)<!-- NAV:END -->', html, re.DOTALL)
            if nav_section:
                nav_html = nav_section.group(1)
                if prefix == '../':
                    if 'href="index.html' in nav_html:
                        errors.append(f'{filename}: nav 中有缺少 ../ 前綴的連結')
                else:
                    if 'href="../' in nav_html:
                        errors.append(f'{filename}: nav 中有多餘的 ../ 前綴')

    return errors


if __name__ == '__main__':
    main()
