#!/usr/bin/env python3
"""WCAG 对比度检查（针对项目 CSS tokens）。"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def lum(h):
    h = h.lstrip('#')
    r, g, b = int(h[0:2],16)/255, int(h[2:4],16)/255, int(h[4:6],16)/255
    def f(c): return c/12.92 if c<=0.03928 else ((c+0.055)/1.055)**2.4
    return 0.2126*f(r)+0.7152*f(g)+0.0722*f(b)

def ratio(a, b):
    la, lb = lum(a), lum(b)
    if la < lb: la, lb = lb, la
    return (la+0.05)/(lb+0.05)

# 项目 tokens: 文本色 vs 背景白
pairs = [
    ('--text #0F172A', '#0F172A', '#FFFFFF'),
    ('--text-secondary #475569', '#475569', '#FFFFFF'),
    ('--text-muted #64748B', '#64748B', '#FFFFFF'),
    ('--text-muted #64748B on bg-soft #F0F9FF', '#64748B', '#F0F9FF'),
    ('--text-disabled #94A3B8', '#94A3B8', '#FFFFFF'),
    ('--brand #0284C7 on white (btn-outline text)', '#0284C7', '#FFFFFF'),
    ('--brand #0284C7 on brand-light #E0F2FE (tag/active)', '#0284C7', '#E0F2FE'),
    ('white on btn-primary #0369A1', '#FFFFFF', '#0369A1'),
    ('--text-secondary on bg-alt #F8FAFC', '#475569', '#F8FAFC'),
]
for name, fg, bg in pairs:
    r = ratio(fg, bg)
    ok = 'AA' if r >= 4.5 else ('AA-large' if r >= 3.0 else 'FAIL')
    print(f'{name:<42} ratio={r:.2f}  {ok}')
