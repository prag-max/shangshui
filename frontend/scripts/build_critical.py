#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Critical CSS 构建脚本（幂等，可重复运行）

关键改进（相较旧版）：
1. 【消除行号耦合】critical CSS 不再依赖 style.css 的"物理行号区间"，
   改为抽取源码中 /* @critical */ ... /* @endcritical */ 锚点之间的文本。
   锚点随代码移动，版本稳定，增删样式不会静默错位。
2. 【消除异步/同步冲突】主样式表统一以「同步 <link>」注入。
   critical 已内联首屏，同步加载主表不会阻塞首屏渲染，
   且与本地 file:// 直接打开页面完全兼容（旧版 preload+onload 在 file:// 下会失效）。
3. 【CSS 源拆分】style.css 由 assets/css/src/*.css 四个 partial 拼接生成，
   修改样式请编辑 src/ 下 partial（已用 @critical 标记首屏区段），再运行本脚本。

抽取规则（在 src partial 中已用 @critical 标好）：:root 变量、reset/base、
工具类、按钮、Header/Nav、Hero/Stats、Floating CTA、各页 Hero、定价 sticky
subnav、移动端 nav-overlay、全局 prefers-reduced-motion，以及含首屏响应式的
@media 块。

运行: python scripts/build_critical.py
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT, "assets", "css", "src")
STYLE = os.path.join(ROOT, "assets", "css", "style.css")
CRIT = os.path.join(ROOT, "assets", "css", "critical.css")
HTMLS = ["index.html", "solutions.html", "pricing.html", "contact.html", "404.html", "faq.html"]

SRC_FILES = ["tokens.css", "base.css", "components.css", "pages.css"]


# ---------- 1) 拼接生成 style.css ----------
def concat_style():
    parts = []
    for name in SRC_FILES:
        p = os.path.join(SRC_DIR, name)
        if not os.path.exists(p):
            raise RuntimeError(f"缺少源 partial: {p}")
        with open(p, "r", encoding="utf-8") as f:
            parts.append(f.read().strip())
    out = "\n\n".join(parts) + "\n"
    with open(STYLE, "w", encoding="utf-8") as f:
        f.write(out)
    return len(out.encode("utf-8"))


# ---------- 2) 基于 @critical 锚点的 critical 抽取（无行号依赖） ----------
START = "/* @critical */"
END = "/* @endcritical */"


def extract_critical(css):
    parts = []
    i = 0
    while True:
        s = css.find(START, i)
        if s < 0:
            break
        e = css.find(END, s + len(START))
        if e < 0:
            break
        parts.append(css[s + len(START):e])
        i = e + len(END)
    return "".join(parts)


def minify(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{}:;,>])\s*", r"\1", css)
    return css.strip()


# ---------- 3) 注入 HTML（幂等，同步加载） ----------
MAIN_LINK_RE = re.compile(r'<link rel="(?:stylesheet|preload)" href="assets/css/style(?:\.[0-9a-f]{8})?\.css"[^>]*>')
STYLE_RE = re.compile(r'<style id="critical-css">[\s\S]*?</style>\s*')
NS_RE = re.compile(r'<noscript><link rel="stylesheet" href="assets/css/style\.css"></noscript>\s*')


def inject(html_path, mini):
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
    html = STYLE_RE.sub("", html)
    html = NS_RE.sub("", html)
    m = MAIN_LINK_RE.search(html)
    if not m:
        print(f"  ⚠ 跳过 {os.path.basename(html_path)}：未找到主样式表链接")
        return None, None
    block = (
        '<style id="critical-css">' + mini + "</style>\n"
        + m.group(0)
    )
    html = html[: m.start()] + block + html[m.end():]
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    return len(mini.encode("utf-8")), len(html.encode("utf-8"))


if __name__ == "__main__":
    size = concat_style()
    print(f"✅ 拼接 style.css: {size} bytes（源 = src/*.css）")
    with open(STYLE, "r", encoding="utf-8") as f:
        css = f.read()
    if css.count(START) == 0:
        raise RuntimeError("未在 src partial 中找到 @critical 锚点，请先运行 scripts/mark_critical.py")
    raw = extract_critical(css)
    mini = minify(raw)
    with open(CRIT, "w", encoding="utf-8") as f:
        f.write(mini)
    print(f"✅ 抽取 critical.css: 源 {len(raw.encode('utf-8'))} bytes / 压缩内联 {len(mini.encode('utf-8'))} bytes")
    for fn in HTMLS:
        p = os.path.join(ROOT, fn)
        if not os.path.exists(p):
            print(f"  ⚠ 不存在: {fn}")
            continue
        mb, total = inject(p, mini)
        if mb is not None:
            print(f"  ✅ {fn:<16} 内联 {mb:>6} bytes | 文件总 {total:>7} bytes")
