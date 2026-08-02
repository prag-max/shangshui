#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一次性脚本：在 assets/css/src/*.css 中插入 critical 锚点标记。

标记规则（仅圈定首屏必需样式，其余交由完整 style.css 异步后加载）：
  /* @critical */   ...首屏规则...   /* @endcritical */

build_critical.py 抽取所有 @critical..@endcritical 之间的文本作为 critical CSS。
锚点随代码移动，版本稳定，不再依赖行号。

运行: python scripts/mark_critical.py
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets", "css", "src")


def mark_whole(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    lines.insert(0, "/* @critical */\n")
    # 末尾插入结束标记（保留原末尾换行）
    if lines and not lines[-1].endswith("\n"):
        lines[-1] += "\n"
    lines.append("/* @endcritical */\n")
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print(f"  ✅ 整文件标记: {os.path.basename(path)}")


def mark_regions(path, regions):
    """regions: list of (start_anchor, end_anchor) —— 在 start 前插入 @critical，
    在 end 前插入 @endcritical（end 为下一区段横幅，保证区间精确闭合）。"""
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    inserts = []
    for start_a, end_a in regions:
        si = next((i for i, ln in enumerate(lines) if start_a in ln), -1)
        ei = next((i for i, ln in enumerate(lines) if end_a in ln), -1)
        if si < 0 or ei < 0:
            raise RuntimeError(f"锚点未找到 in {os.path.basename(path)}: {start_a!r}/{end_a!r}")
        if ei <= si:
            raise RuntimeError(f"区间非法 in {os.path.basename(path)}: {start_a!r}..{end_a!r}")
        inserts.append((si, "/* @critical */\n"))
        inserts.append((ei, "/* @endcritical */\n"))
    for i, mk in sorted(inserts, reverse=True):
        lines.insert(i, mk)
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print(f"  ✅ 区间标记: {os.path.basename(path)} ({len(regions)} 段)")


def strip_markers(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    out = [ln for ln in lines if ("@critical" not in ln and "@endcritical" not in ln)]
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(out)


def main():
    # 先清除旧标记，保证可重复运行
    for name in ["tokens.css", "base.css", "components.css", "pages.css"]:
        strip_markers(os.path.join(SRC, name))

    # tokens / base：整文件均为首屏变量与基础样式
    mark_whole(os.path.join(SRC, "tokens.css"))
    mark_whole(os.path.join(SRC, "base.css"))

    # components：Header..Stats（含 Hero） + Floating CTA
    mark_regions(os.path.join(SRC, "components.css"), [
        ("/* ---------- Header ---------- */", "/* ---------- Cards Grid ---------- */"),
        ("/* ---------- Floating CTA ---------- */", "/* ---------- Lightbox ---------- */"),
    ])

    # pages：响应式首屏 + 各页 Hero + 定价 sticky subnav + 移动端 nav-overlay + 减弱动画
    # 注意：响应式 media 块与 contact-hero 必须合并为同一连续区段，
    # 否则两者共用 "Contact Page" 锚点会产生嵌套标记导致 region 丢失。
    mark_regions(os.path.join(SRC, "pages.css"), [
        ("@media (max-width: 1100px) {", ".contact-section {"),
        ("/* ---------- Price Hero ---------- */", "/* ---------- Quick Match ---------- */"),
        ("/* ---------- Pricing Sub Nav", "/* ---------- Card Features List"),
        ("/* ---------- Mobile Nav Overlay", "/* ---------- Back to Top"),
        ("@media (prefers-reduced-motion: reduce) {", "@media (max-width: 1024px) {"),
    ])
    print("\n标记完成。运行 scripts/build_critical.py 重新生成 style.css 与 critical。")


if __name__ == "__main__":
    main()
