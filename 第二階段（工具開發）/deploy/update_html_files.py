#!/usr/bin/env python3
"""
Script to:
1. Add <link rel="stylesheet" href="common.css"> after styles.css
2. Add <link rel="prefetch"> for next/prev steps and key pages
"""

import os
import re
from pathlib import Path

def get_html_files(root_dir):
    """Get all HTML files in the directory and subdirectories."""
    html_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    return sorted(html_files)

def is_step_file(filepath):
    """Check if file is a step file."""
    return '/step/' in filepath or '\\step\\' in filepath

def get_step_number(filepath):
    """Extract step number from filepath."""
    match = re.search(r'/step/(\d+)\.html', filepath)
    if not match:
        match = re.search(r'\\step\\(\d+)\.html', filepath)
    if match:
        return int(match.group(1))
    return None

def get_relative_path(from_file, to_file):
    """Get relative path from one file to another."""
    from_dir = os.path.dirname(from_file)
    to_dir = os.path.dirname(to_file)

    # Count directory levels
    from_depth = from_dir.count(os.sep)
    to_depth = to_dir.count(os.sep)

    if from_depth == to_depth:
        # Same directory
        return os.path.basename(to_file)
    elif from_depth > to_depth:
        # From is deeper, go up
        up_count = from_depth - to_depth
        return '../' * up_count + os.path.basename(to_file)
    else:
        # From is shallower, go down
        rel = os.path.relpath(to_file, from_dir)
        return rel

def add_common_css_link(content, filepath):
    """Add common.css link after styles.css."""
    # Determine the correct relative path
    if is_step_file(filepath):
        common_css_path = '../common.css'
    else:
        common_css_path = 'common.css'

    # Look for styles.css link
    styles_pattern = r'(<link\s+rel="stylesheet"\s+href="[^"]*styles\.css"[^>]*>)'

    if re.search(styles_pattern, content):
        # Add common.css link right after styles.css
        new_link = f'    <link rel="stylesheet" href="{common_css_path}">'
        content = re.sub(
            styles_pattern,
            r'\1\n' + new_link,
            content
        )
        return content
    return content

def add_prefetch_links(content, filepath):
    """Add prefetch links for next/prev steps or key pages."""
    prefetch_links = []

    step_num = get_step_number(filepath)

    if step_num is not None:
        # This is a step file
        # Prefetch next step
        if step_num < 18:
            next_step = step_num + 1
            prefetch_links.append(f'    <link rel="prefetch" href="{next_step:02d}.html">')

        # Prefetch previous step
        if step_num > 1:
            prev_step = step_num - 1
            prefetch_links.append(f'    <link rel="prefetch" href="{prev_step:02d}.html">')

    elif 'index.html' in filepath:
        # Prefetch key pages from index
        prefetch_links = [
            '    <link rel="prefetch" href="builders.html">',
            '    <link rel="prefetch" href="trends.html">',
            '    <link rel="prefetch" href="step/01.html">'
        ]

    elif 'builders.html' in filepath:
        # Prefetch index from builders
        prefetch_links = [
            '    <link rel="prefetch" href="index.html">'
        ]

    if not prefetch_links:
        return content

    # Find the closing </head> tag and insert before it
    head_close_pattern = r'(\s*)</head>'

    if re.search(head_close_pattern, content):
        prefetch_html = '\n'.join(prefetch_links) + '\n'
        content = re.sub(
            head_close_pattern,
            prefetch_html + r'\1</head>',
            content
        )
        return content

    return content

def process_file(filepath):
    """Process a single HTML file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Add common.css link
    content = add_common_css_link(content, filepath)

    # Add prefetch links
    content = add_prefetch_links(content, filepath)

    # Write back only if changed
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    root_dir = '/sessions/loving-tender-ritchie/mnt/好宅通/deploy'

    html_files = get_html_files(root_dir)

    # Filter out files we don't want to modify
    skip_patterns = ['google', '404.html']
    html_files = [f for f in html_files if not any(pattern in f for pattern in skip_patterns)]

    print(f"Found {len(html_files)} HTML files to process")

    modified_count = 0
    for filepath in html_files:
        if process_file(filepath):
            modified_count += 1
            rel_path = os.path.relpath(filepath, root_dir)
            print(f"  Modified: {rel_path}")

    print(f"\nTotal modified: {modified_count}/{len(html_files)}")

if __name__ == '__main__':
    main()
