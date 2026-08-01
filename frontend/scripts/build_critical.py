#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Critical CSS 构建脚本（幂等，可重复运行）

功能:
1. 从 assets/css/style.css 按行区间精确抽取「首屏必需」样式
   （:root 变量 / Reset / 工具类 / 按钮 / Header·Nav / 各页 Hero 变体 /
    面包屑 / 浮动 CTA / 首屏响应式 @media）
2. 生成可读源文件 assets/css/critical.css
3. 压缩后内联进 5 个 HTML 的 <head>，并把主样式表改为非阻塞异步加载
   （preload + onload + <noscript> 兜底）

运行: python scripts/build_critical.py
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STYLE = os.path.join(ROOT, "assets", "css", "style.css")
CRIT = os.path.join(ROOT, "assets", "css", "critical.css")
HTMLS = ["index.html", "solutions.html", "pricing.html", "contact.html", "404.html"]

# 1-indexed inclusive line ranges (from style.css v2.0)
RANGES = [
    (7, 110),     # :root 自定义属性（全部 CSS 变量，必须最先）
    (112, 138),   # Reset & Base
    (139, 158),   # Utility (.container .sr-only .text-* .hl ...)
    (159, 205),   # Buttons + @media (pointer:coarse) 触摸目标
    (207, 242),   # Section Common + .eyebrow + .lead
    (244, 247),   # Grid Helpers
    (248, 256),   # Icon Helpers
    (257, 263),   # Tag
    (264, 326),   # Header / Nav / Hamburger / 移动端 nav 覆盖 + min-width 媒体
    (327, 439),   # Hero + 子页 Hero(.hero-sub) + @keyframes pulse-dot
    (440, 456),   # Stats Strip（首页首屏重叠区，部分可见）
    (773, 787),   # Floating CTA（固定右下，视口内可见）
    (1010, 1026), # 404 页面首屏 .notfound-*
    (1052, 1094), # 响应式 1100 + 980（hero/section/grid 移动端）
    (1096, 1112), # 响应式 640
    (1114, 1144), # .contact-hero（联系页首屏）
    (1243, 1248), # 联系页响应式 980
    (1263, 1339), # .price-hero + .price-hero-trust（定价页首屏）
    (1795, 1826), # 定价页响应式 1100/980/640
    (1828, 1856), # 定价页 sticky subnav
    (1948, 1957), # 移动端 nav-overlay（P2-10）
    (2012, 2018), # Skip Link（无障碍）
    (2041, 2054), # 全局 prefers-reduced-motion（防动画闪烁）
    (2059, 2083), # Breadcrumb
    (2162, 2164), # Breadcrumb-mobile min-width
]


def extract_critical():
    with open(STYLE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    out = []
    for (a, b) in RANGES:
        out.extend(lines[a - 1:b])
    return "".join(out)


def minify(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)  # 去注释
    css = re.sub(r"\s+", " ", css)                        # 折叠空白
    css = re.sub(r"\s*([{}:;,>])\s*", r"\1", css)         # 去符号周围空格
    return css.strip()


def build():
    raw = extract_critical()
    with open(CRIT, "w", encoding="utf-8") as f:
        f.write("/* ============================================================\n")
        f.write("   尚水数字 · Critical CSS（首屏内联）\n")
        f.write("   由 scripts/build_critical.py 从 style.css 抽取，禁止手改本文件\n")
        f.write("   ============================================================ */\n\n")
        f.write(raw)
    mini = minify(raw)
    return raw, mini


# 匹配主样式表链接（同步 或 已异步化两种形态都认，保证可重复重跑）
MAIN_LINK_RE = re.compile(r'<link rel="(?:stylesheet|preload)" href="assets/css/style\.css"[^>]*>')
STYLE_RE = re.compile(r'<style id="critical-css">[\s\S]*?</style>\s*')
NS_RE = re.compile(r'<noscript><link rel="stylesheet" href="assets/css/style\.css"></noscript>\s*')


def inject(html_path, mini):
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
    # 幂等：先彻底移除旧的内联块 / 异步 link / noscript 兜底
    html = STYLE_RE.sub("", html)
    html = NS_RE.sub("", html)
    m = MAIN_LINK_RE.search(html)
    if not m:
        print(f"  ⚠ 跳过 {os.path.basename(html_path)}：未找到主样式表链接")
        return None, None
    block = (
        '<style id="critical-css">' + mini + "</style>\n"
        '<link rel="preload" href="assets/css/style.css" as="style" '
        'onload="this.onload=null;this.rel=\'stylesheet\'">\n'
        '<noscript><link rel="stylesheet" href="assets/css/style.css"></noscript>'
    )
    # 在（原同步或原异步）link 位置整体替换为「内联 critical + 异步 link + noscript」
    html = html[:m.start()] + block + html[m.end():]
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    return len(mini.encode("utf-8")), len(html.encode("utf-8"))


if __name__ == "__main__":
    raw, mini = build()
    print(f"✅ 抽取 critical.css: 源 {len(raw.encode('utf-8'))} bytes / "
          f"压缩内联 {len(mini.encode('utf-8'))} bytes")
    for fn in HTMLS:
        p = os.path.join(ROOT, fn)
        if not os.path.exists(p):
            print(f"  ⚠ 不存在: {fn}")
            continue
        mb, total = inject(p, mini)
        if mb is not None:
            print(f"  ✅ {fn:<16} 内联 {mb:>6} bytes | 文件总 {total:>7} bytes")
