#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一次性脚本：将单体 style.css 按现有章节横幅机械拆分为 4 个源 partial。

拆分后：
  assets/css/src/tokens.css      —— 文件头 + CSS 变量(:root)
  assets/css/src/base.css        —— Reset/Base/Utility/Buttons/Section/Helpers
  assets/css/src/components.css  —— Header/Hero/Cards/Footer/... 全站组件
  assets/css/src/pages.css       —— Pricing/Contact/FAQ/404/Breadcrumb 等页面样式

style.css 此后由 build_critical.py 从 src/ 拼接生成（不再手改）。
所有内容均原样保留，仅按横幅位置切分，拼接后与原文功能等价。

运行: python scripts/split_css.py
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets", "css", "src")
STYLE = os.path.join(ROOT, "assets", "css", "style.css")


def find_line(lines, predicate):
    for i, ln in enumerate(lines):
        if predicate(ln.strip()):
            return i
    raise RuntimeError("未找到切割锚点: " + predicate.__name__)


def main():
    os.makedirs(SRC, exist_ok=True)
    with open(STYLE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    i_reset = find_line(lines, lambda s: s == "/* ---------- Reset & Base ---------- */")
    i_header = find_line(lines, lambda s: s == "/* ---------- Header ---------- */")
    # Pricing 大章节横幅：以 /* === 开头、且下一行含 "PRICING"
    i_pricing = None
    for i, ln in enumerate(lines):
        if ln.strip().startswith("/* =") and i + 1 < len(lines) and "PRICING" in lines[i + 1]:
            i_pricing = i
            break
    if i_pricing is None:
        raise RuntimeError("未找到 Pricing 章节横幅")

    parts = {
        "tokens.css": (0, i_reset),
        "base.css": (i_reset, i_header),
        "components.css": (i_header, i_pricing),
        "pages.css": (i_pricing, len(lines)),
    }

    banner = "/* 源 partial —— 由 scripts/split_css.py 从 style.css 切分；修改请编辑本目录文件，再运行 build_critical.py 重新生成 style.css */\n\n"
    for name, (a, b) in parts.items():
        with open(os.path.join(SRC, name), "w", encoding="utf-8") as f:
            f.write(banner)
            f.writelines(lines[a:b])
        print(f"  ✅ src/{name}: 行 {a + 1}–{b}  ({b - a} 行)")

    print("\n拆分完成。下一步运行 scripts/build_critical.py 重新生成 style.css。")


if __name__ == "__main__":
    main()
