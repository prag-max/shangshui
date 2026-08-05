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
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT, "assets", "css", "src")
STYLE = os.path.join(ROOT, "assets", "css", "style.css")
CRIT = os.path.join(ROOT, "assets", "css", "critical.css")
SITE = os.path.join(ROOT, "partials", "site.json")
HTMLS = ["index.html", "pricing.html", "404.html", "faq.html"]

# 公共 HTML 片段（改一处 -> 4 页全局生效）
PARTIALS = {
    "icons": os.path.join(ROOT, "partials", "icons.html"),
    "footer": os.path.join(ROOT, "partials", "footer.html"),
    "contact-pop": os.path.join(ROOT, "partials", "contact-pop.html"),
}

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
    # 先抽出字符串字面量（保护 content:" > " 等引号内内容，避免被空白压缩破坏）
    slots = []
    def _stash(m):
        slots.append(m.group(0))
        return "\x00" + str(len(slots) - 1) + "\x00"
    css = re.sub(r'"(?:[^"\\]|\\.)*"', _stash, css)
    css = re.sub(r"'(?:[^'\\]|\\.)*'", _stash, css)
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{}:;,>])\s*", r"\1", css)
    # 还原字符串字面量
    css = re.sub(r"\x00(\d+)\x00", lambda m: slots[int(m.group(1))], css)
    return css.strip()


# ---------- 3) 注入 HTML（幂等，同步加载） ----------
# 仅锚定真正的「主样式表」链接（rel=stylesheet），避免与 preload 等并行 link 混淆顺序语义。
MAIN_LINK_RE = re.compile(r'<link rel="stylesheet" href="assets/css/style(?:\.[0-9a-f]{8})?\.css(?:\?[^"]*)?"[^>]*>')
STYLE_RE = re.compile(r'<style id="critical-css">[\s\S]*?</style>\s*')
NS_RE = re.compile(r'<noscript><link rel="stylesheet" href="assets/css/style\.css"></noscript>\s*')


def inject(html_path, mini, out_dir=None):
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
    # 支持输出到独立构建目录，避免覆写源 HTML（源保留 {{site.*}} / partial 占位符）
    target = os.path.join(out_dir, os.path.basename(html_path)) if out_dir else html_path
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        f.write(html)
    return len(mini.encode("utf-8")), len(html.encode("utf-8"))


def inject_site(html_path, mapping, out_dir=None):
    """将 {{site.*}} 占位符替换为 partials/site.json 中的全局联系方式（幂等）。"""
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
    for k, v in mapping.items():
        html = html.replace("{{site.%s}}" % k, v)
    target = os.path.join(out_dir, os.path.basename(html_path)) if out_dir else html_path
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        f.write(html)


def inject_partials(html_path, out_dir=None):
    """将 <!--#footer--> / <!--#contact-pop--> 占位符替换为 partials/*.html 公共片段（幂等）。"""
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
    for name, p in PARTIALS.items():
        with open(p, "r", encoding="utf-8") as f:
            content = f.read().strip()
        html = html.replace("<!--#%s-->" % name, content)
    target = os.path.join(out_dir, os.path.basename(html_path)) if out_dir else html_path
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        f.write(html)


def main():
    # 可选：构建产物输出到独立目录（默认覆写源 HTML，保持向后兼容）
    import sys as _sys
    out_dir = None
    if "--dist" in _sys.argv:
        i = _sys.argv.index("--dist")
        out_dir = _sys.argv[i + 1] if i + 1 < len(_sys.argv) else os.path.join(ROOT, "dist")

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
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    for fn in HTMLS:
        p = os.path.join(ROOT, fn)
        if not os.path.exists(p):
            print(f"  ⚠ 不存在: {fn}")
            continue
        mb, total = inject(p, mini, out_dir=out_dir)
        if mb is not None:
            print(f"  ✅ {fn:<16} 内联 {mb:>6} bytes | 文件总 {total:>7} bytes")
    # 公共片段注入：footer / contact-pop 改 partials/*.html 一处 -> 4 页同步
    for fn in HTMLS:
        p = os.path.join(ROOT, fn)
        if os.path.exists(p):
            inject_partials(p, out_dir=out_dir)
    print(f"✅ 公共片段注入 partials -> {len(HTMLS)} 个页面")
    # 联系方式全局注入：改 partials/site.json 一处，4 个页面同步生效
    with open(SITE, "r", encoding="utf-8") as f:
        site = json.load(f)
    for fn in HTMLS:
        p = os.path.join(ROOT, fn)
        if os.path.exists(p):
            inject_site(p, site, out_dir=out_dir)
    print(f"✅ 联系方式注入 site.json -> {len(HTMLS)} 个页面")
    if out_dir:
        print(f"✅ 产物已输出到独立目录: {os.path.relpath(out_dir, ROOT)}（源 HTML 未被覆写）")


if __name__ == "__main__":
    main()
