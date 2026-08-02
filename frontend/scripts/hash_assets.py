#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hash_assets.py — 为静态资源文件名注入内容哈希，消除强缓存导致的“发版不可控”。

背景：edgeone.json 对 /assets/* 设置了长达 1 天(CSS/JS)~7 天(图片) 的强缓存，
而资源文件名固定（style.css / main.js / *.png），改内容后浏览器/边缘节点不会主动
重新拉取，导致新版本要等缓存自然过期才生效，且存在“新 HTML + 旧 CSS/JS”版本错配。

本脚本做法：
  1. 计算每个可版本化资源的 sha256 内容哈希（取前 8 位）；
  2. 原地重命名为 name.<hash>.ext（如 style.ab12cd.css）；
  3. 在 6 个 HTML 与 fonts.css 中，把旧引用（根相对 assets/... 与 css 内相对 ../...）
     全部改写为带哈希的新名；
  4. 被绝对 URL / meta 引用的“品牌资产”不哈希，保持原文件名。

幂等：已带哈希的文件跳过；资源内容不变则哈希不变、引用不变。
可重复运行：内容变化 → 哈希变化 → 旧哈希引用被改写为新哈希引用，旧哈希文件清理。

用法：
  python scripts/hash_assets.py            # 执行哈希 + 改写引用
  python scripts/hash_assets.py --dry-run  # 仅打印计划，不改动任何文件
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys

# ---- 路径 ----
HERE = os.path.dirname(os.path.abspath(__file__))
FRONTEND = os.path.dirname(HERE)

# 待哈希的资源扩展名
HASH_EXTS = {".css", ".js", ".woff2", ".png", ".jpg", ".jpeg",
             ".svg", ".webp", ".avif", ".ico", ".gif"}

# 明确排除（被绝对 URL 或 <meta>/<link> 引用，改名会破坏外部引用）
EXCLUDE_FILES = {
    "assets/css/critical.css",        # 仅内联，未单独引用
    "assets/images/og.svg",           # og:image 绝对 URL 引用
    "assets/images/favicon.ico",
    "assets/images/favicon-16x16.png",
    "assets/images/favicon-32x32.png",
    "assets/images/apple-touch-icon.png",
    "assets/images/logo-icon.png",    # JSON-LD logo 绝对 URL 引用
}
# 排除目录（源 partial）
EXCLUDE_DIRS = {"assets/css/src"}

# 引用改写目标文件
HTML_FILES = ["index.html", "solutions.html", "pricing.html",
              "contact.html", "faq.html", "404.html"]
REWRITE_REL_CSS = ["assets/css/style.css", "assets/css/fonts.css"]

HASH_RE = re.compile(r"^(.+)\.([0-9a-f]{8})\.([^.]+)$")
HASH_LEN = 8


def sha256_8(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:HASH_LEN]


def is_excluded(rel: str) -> bool:
    rel = rel.replace(os.sep, "/")
    if rel in EXCLUDE_FILES:
        return True
    parts = rel.split("/")
    return any(p in EXCLUDE_DIRS for p in parts[:-1])


def discover_assets() -> list[str]:
    """返回所有待哈希资源的绝对路径（排除项、源 partial、未引用副本）。"""
    found = []
    for root, dirs, files in os.walk(os.path.join(FRONTEND, "assets")):
        # 不进入排除目录（按相对 FRONTEND 的完整路径判断）
        dirs[:] = [
            d for d in dirs
            if os.path.relpath(os.path.join(root, d), FRONTEND).replace(os.sep, "/")
            not in EXCLUDE_DIRS
        ]
        for fn in files:
            ext = os.path.splitext(fn)[1].lower()
            if ext not in HASH_EXTS:
                continue
            abs_p = os.path.join(root, fn)
            rel = os.path.relpath(abs_p, FRONTEND).replace(os.sep, "/")
            if is_excluded(rel):
                continue
            found.append(abs_p)
    return sorted(found)


class Asset:
    def __init__(self, abs_p: str):
        self.dir = os.path.dirname(abs_p)
        self.name = os.path.basename(abs_p)
        self.ext = os.path.splitext(self.name)[1].lower()
        self.stem = os.path.splitext(self.name)[0]  # 去扩展名后的名字
        self.abs = abs_p
        m = HASH_RE.match(self.name)
        if m:
            self.logical_stem = m.group(1)
            self.embedded_hash = m.group(2)
            self.is_hashed = True
        else:
            self.logical_stem = self.stem
            self.embedded_hash = None
            self.is_hashed = False

    @property
    def logical_name(self) -> str:
        return self.logical_stem + self.ext

    def hashed_name(self, h: str) -> str:
        return f"{self.logical_stem}.{h}{self.ext}"


def plan() -> tuple[list, dict]:
    """
    返回 (operations, mapping)
    operations: 待执行的资源处理列表
    mapping: logical_name -> 新哈希名（用于改写引用）
    """
    assets = [Asset(p) for p in discover_assets()]
    # 按 logical_name 聚合（可能同时存在 未哈希源 + 已哈希旧副本）
    groups: dict[str, list[Asset]] = {}
    for a in assets:
        groups.setdefault(a.logical_name, []).append(a)

    operations = []
    mapping = {}
    for logical, items in groups.items():
        source = next((a for a in items if not a.is_hashed), None)
        hashed = [a for a in items if a.is_hashed]
        if source is None:
            # 只有已哈希副本：无需处理（引用应已带哈希）
            if hashed:
                mapping[logical] = hashed[0].name
            continue
        h = sha256_8(source.abs)
        new_name = source.hashed_name(h)
        operations.append({
            "logical": logical,
            "source": source,
            "new_name": new_name,
            "old_hashed": [a for a in hashed if a.name != new_name],
        })
        mapping[logical] = new_name
    return operations, mapping


def build_rewrites(operations: list, mapping: dict) -> dict[str, list[tuple[str, str]]]:
    """
    为每种目标文件构建 (old, new) 替换对。
    覆盖两种引用写法：
      - 根相对：assets/...            （HTML 内常见）
      - 目录相对：../... / sub/...     （CSS 内 url() 常见）
    old 同时包含“未哈希原名”与“旧哈希名”（内容变更场景）。
    """
    targets = [os.path.join(FRONTEND, f) for f in HTML_FILES]
    targets += [os.path.join(FRONTEND, f) for f in REWRITE_REL_CSS]

    result: dict[str, list[tuple[str, str]]] = {t: [] for t in targets}
    for t in targets:
        tdir = os.path.dirname(t)
        for op in operations:
            new_abs = os.path.join(
                os.path.dirname(op["source"].abs), op["new_name"])
            new_root = "assets/" + os.path.relpath(new_abs, FRONTEND).replace(os.sep, "/")
            new_rel = os.path.relpath(new_abs, tdir).replace(os.sep, "/")
            # 旧形式：未哈希原名
            old_root = "assets/" + os.path.relpath(op["source"].abs, FRONTEND).replace(os.sep, "/")
            old_rel = os.path.relpath(op["source"].abs, tdir).replace(os.sep, "/")
            for old in {old_root, old_rel}:
                result[t].append((old, new_root if old == old_root else new_rel))
            # 旧形式：旧哈希名（内容变更时）
            for old_a in op["old_hashed"]:
                old_abs = os.path.join(os.path.dirname(op["source"].abs), old_a.name)
                old_root_h = "assets/" + os.path.relpath(old_abs, FRONTEND).replace(os.sep, "/")
                old_rel_h = os.path.relpath(old_abs, tdir).replace(os.sep, "/")
                for old in {old_root_h, old_rel_h}:
                    result[t].append((old, new_root if old == old_root_h else new_rel))
    # 去重，保持顺序
    for t in result:
        seen = set()
        uniq = []
        for old, new in result[t]:
            if old == new:
                continue
            key = (old, new)
            if key in seen:
                continue
            seen.add(key)
            uniq.append((old, new))
        result[t] = uniq
    return result


def safe_remove(path: str) -> bool:
    """删除文件；失败时给出警告而非中断构建。

    注：本脚本的删除场景只针对「内容变更后产生的旧哈希副本」这类构建产物，
    不会触碰源文件。返回是否成功删除。
    """
    try:
        os.remove(path)
        return True
    except OSError as e:
        print(f"  ⚠ 无法删除旧哈希副本 {os.path.basename(path)}: {e}")
        return False


def _ctx_replace(text: str, old: str, new: str) -> tuple[str, int]:
    """仅在真实引用上下文中替换路径，避免误伤注释 / JSON-LD / data-* 字面量。

    匹配的上下文：href="..."  src="..."  url(...)  url("...")  url('...')。
    """
    pat = re.compile(
        r'(href="|src="|url\(\s*["\']?)'
        + re.escape(old)
        + r'(["\']?\s*\)|")'
    )
    return pat.subn(lambda m: m.group(1) + new + m.group(2), text)


def apply(operations: list, rewrites: dict, dry_run: bool):
    changed_files = set()

    # 阶段一：先改写引用（仅匹配 href=/src=/url() 上下文，此时资源仍用原名存在）
    for t, pairs in rewrites.items():
        if not pairs or not os.path.exists(t):
            continue
        with open(t, "r", encoding="utf-8") as f:
            text = f.read()
        orig = text
        for old, new in pairs:
            if old in text:
                text, n = _ctx_replace(text, old, new)
                if n:
                    changed_files.add(t)
        if not dry_run and text != orig:
            with open(t, "w", encoding="utf-8") as f:
                f.write(text)

    # 阶段二：再原子改名资源（引用已指向新名，原文件改名不会破坏引用）
    renamed = 0
    deleted = 0
    for op in operations:
        src = op["source"]
        src_abs = src.abs
        dst_abs = os.path.join(src.dir, op["new_name"])
        if dry_run:
            print(f"  [hash] {src.logical_name} -> {op['new_name']}")
            continue
        # os.replace 为原子改名（非删除操作），目标已存在则覆盖，保证多次运行幂等。
        if os.path.abspath(src_abs) != os.path.abspath(dst_abs) and os.path.exists(src_abs):
            os.replace(src_abs, dst_abs)
            renamed += 1
        # 【P1 修复】删除内容变更后产生的旧哈希副本，避免仓库/产物中堆积孤儿文件。
        for old_a in op["old_hashed"]:
            old_abs = old_a.abs
            if os.path.abspath(old_abs) == os.path.abspath(dst_abs):
                continue
            if os.path.exists(old_abs) and safe_remove(old_abs):
                deleted += 1

    if dry_run:
        n_rewrite = sum(1 for t in rewrites if rewrites[t])
        print(f"  [rewrite] 将改写 {len(rewrites)} 个目标文件中 {n_rewrite} 个；重命名 {len(operations)} 个资源")
    else:
        print(f"  改写引用的文件: {len(changed_files)}")
        for t in sorted(changed_files):
            print(f"    - {os.path.relpath(t, FRONTEND)}")
        print(f"  重命名资源: {renamed}；删除旧哈希副本: {deleted}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="仅打印计划，不改动文件")
    args = ap.parse_args()

    print("=== hash_assets.py ===")
    print(f"前端根目录: {FRONTEND}")
    ops, mapping = plan()
    if not ops:
        print("无待哈希资源（均已带哈希或无需处理）。")
        return
    print(f"待处理资源: {len(ops)}")
    rewrites = build_rewrites(ops, mapping)
    apply(ops, rewrites, args.dry_run)
    if args.dry_run:
        print("（dry-run 完成，未做任何改动）")
    else:
        print("完成。资源已带内容哈希，引用已同步改写。")


if __name__ == "__main__":
    main()
