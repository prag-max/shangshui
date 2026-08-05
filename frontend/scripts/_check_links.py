#!/usr/bin/env python3
"""上线前断链检查：扫描所有 HTML 的本地 href/src 引用，报告缺失文件。"""
import re, glob, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_PREFIX = ('http', 'mailto', 'tel:', '#', 'data:', 'javascript:', '//')

def norm(href):
    # 去 query/hash
    href = href.split('?')[0].split('#')[0]
    if href.startswith('/'):
        href = href.lstrip('/')
    return href

def main():
    missing = []
    checked = 0
    for f in glob.glob(os.path.join(ROOT, '**', '*.html'), recursive=True):
        rel = os.path.relpath(f, ROOT).replace('\\', '/')
        try:
            t = open(f, encoding='utf-8').read()
        except Exception as e:
            print(f'[READ-FAIL] {rel}: {e}')
            continue
        for m in re.finditer(r'(?:href|src)="([^"]+)"', t):
            href = m.group(1)
            if href.startswith(SKIP_PREFIX):
                continue
            target = norm(href)
            if not target:
                continue
            checked += 1
            p = os.path.join(ROOT, target.replace('/', os.sep))
            if not os.path.exists(p):
                missing.append((rel, href))

    lines = []
    lines.append('[OK] checked %d local refs' % checked)
    if not missing:
        lines.append('[PASS] no broken links')
    else:
        lines.append('[FAIL] %d broken links:' % len(missing))
        for f, h in missing:
            lines.append('  %s -> %s' % (f, h))
    out = '\n'.join(lines)
    print(out)
    # 双保险：同时写文件（PowerShell 控制台有时吞 stdout）
    try:
        with open(os.path.join(ROOT, 'scripts', '_check_links_out.txt'), 'w', encoding='utf-8') as fp:
            fp.write(out)
    except Exception:
        pass
    return 1 if missing else 0

if __name__ == '__main__':
    sys.exit(main())
