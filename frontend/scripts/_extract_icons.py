#!/usr/bin/env python3
"""提取 index+pricing 的 symbol 并集，生成公共 partials/icons.html。
用法: python scripts/_extract_icons.py   （生成 partial 后，由 build 脚本注入）"""
import re, os, io, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def symbols(name):
    t = open(os.path.join(ROOT, name), encoding='utf-8').read()
    # 提取 <svg ...>...</svg> 块内所有 symbol 原始文本
    lib = re.search(r'<svg xmlns="http://www.w3.org/2000/svg" style="display:none".*?</svg>', t, re.S)
    if not lib:
        return {}
    block = lib.group(0)
    found = {}
    for m in re.finditer(r'<symbol id="([a-z0-9-]+)"[^>]*>.*?</symbol>', block, re.S):
        found[m.group(1)] = m.group(0)
    return found

idx = symbols('index.html')
pri = symbols('pricing.html')

# 并集，按稳定顺序
union = {}
for k in sorted(set(idx) | set(pri)):
    union[k] = idx.get(k, pri.get(k))

lines = []
lines.append('<!-- 公共 SVG icon 库（由 scripts/_extract_icons.py 从 index/pricing 提取并集生成；经 build 注入 4 页） -->')
lines.append('<svg xmlns="http://www.w3.org/2000/svg" style="display:none" aria-hidden="true" focusable="false">')
for k in sorted(union):
    lines.append('  ' + union[k])
lines.append('</svg>')

out = '\n'.join(lines) + '\n'
dest = os.path.join(ROOT, 'partials', 'icons.html')
with open(dest, 'w', encoding='utf-8') as f:
    f.write(out)

print(f'index={len(idx)} pricing={len(pri)} union={len(union)}')
print(f'generated partials/icons.html ({len(out.encode("utf-8"))} bytes)')
