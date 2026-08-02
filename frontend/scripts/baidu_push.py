#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
百度搜索资源平台 · 主动推送（实时）脚本（部署钩子用）

为什么需要它：
  站点靠部署上线，与其等百度爬虫慢慢发现，不如**上线即主动通知百度**。
  本脚本读取 sitemap.xml 中的全部 URL，调用百度「普通收录 → 主动推送」接口，
  把 URL 实时推送给百度，显著加快新页面/改页面的收录。

用法：
  python scripts/baidu_push.py                 # 推送 sitemap 内全部 URL
  python scripts/baidu_push.py --dry-run       # 仅打印待推送 URL，不真正请求
  python scripts/baidu_push.py --sitemap-push  # 额外把 sitemap.xml 本身提交给百度

Token 与站点（二选一配置）：
  1) 环境变量（推荐，避免把 token 写进仓库）：
       export BAIDU_PUSH_TOKEN="你的推送token"
       export BAIDU_SITE="https://www.shanwater.com"
  2) 或直接修改本文件底部 PLACEHOLDER 常量（不推荐提交到 git）。

如何获取 token：
  登录 https://ziyuan.baidu.com → 搜索资源平台 → 普通收录 → 主动推送 →
  「接口调用地址」中 ?token=XXXX 的 XXXX 即为推送 token。

注意：
  - 每日配额有限（新站一般 10 条/天，随索引量提升），脚本会打印百度返回的剩余配额。
  - 与站内已有的 push.js（自动推送，需 ICP 通过后启用）互补：
    本脚本负责「部署时一次性主动推送」，push.js 负责「用户访问时的自动推送」。
"""

import os
import sys
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET

# ---------------------------------------------------------------------------
# 配置（优先环境变量；未设置则使用占位符，运行时会提示）
# ---------------------------------------------------------------------------
DEFAULT_SITE = "https://www.shanwater.com"
DEFAULT_TOKEN = "YOUR_BAIDU_PUSH_TOKEN"   # ← 替换为真实 token，或用环境变量 BAIDU_PUSH_TOKEN
SITEMAP_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sitemap.xml")

PUSH_URL_API = "http://data.zz.baidu.com/urls?site={site}&token={token}"
SITEMAP_API = "http://data.zz.baidu.com/sitemap?site={site}&token={token}"


def load_urls_from_sitemap(path):
    """解析 sitemap.xml，返回 <loc> 文本列表。"""
    if not os.path.exists(path):
        raise SystemExit(f"[错误] 找不到 sitemap：{path}")
    try:
        tree = ET.parse(path)
    except ET.ParseError as e:
        raise SystemExit(f"[错误] sitemap 解析失败：{e}")
    urls = []
    for loc in tree.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc"):
        if loc.text:
            urls.append(loc.text.strip())
    # 兜底：某些 sitemap 不带命名空间
    if not urls:
        for loc in tree.iter("loc"):
            if loc.text:
                urls.append(loc.text.strip())
    return urls


def post_to_baidu(api_url, payload):
    """向百度接口 POST 数据，返回 (http_code, body_text)。"""
    data = payload.encode("utf-8")
    req = urllib.request.Request(api_url, data=data, headers={"Content-Type": "text/plain"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.getcode(), resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:  # 网络/超时等
        return None, str(e)


def main():
    dry_run = "--dry-run" in sys.argv
    sitemap_push = "--sitemap-push" in sys.argv

    site = os.environ.get("BAIDU_SITE", DEFAULT_SITE)
    token = os.environ.get("BAIDU_PUSH_TOKEN", DEFAULT_TOKEN)

    urls = load_urls_from_sitemap(SITEMAP_PATH)
    if not urls:
        raise SystemExit("[错误] sitemap 中没有任何 <loc> URL。")

    print(f"[信息] 站点：{site}")
    print(f"[信息] 待推送 URL 数：{len(urls)}")
    for u in urls:
        print("  - " + u)

    if dry_run:
        print("\n[DRY-RUN] 未真正请求百度接口。去掉 --dry-run 执行真实推送。")
        return

    if token == DEFAULT_TOKEN:
        print("\n[警告] 未配置 BAIDU_PUSH_TOKEN，使用占位符将无法推送成功。")
        print("        请设环境变量 BAIDU_PUSH_TOKEN，或临时修改脚本底部 DEFAULT_TOKEN。")
        # 仍尝试一次，让百度返回明确错误，便于排查
    if token == DEFAULT_TOKEN and not os.environ.get("BAIDU_PUSH_TOKEN"):
        # 占位符场景：打印接口地址但跳过真实请求，避免无谓外呼
        print(f"[跳过] 接口地址示例：{PUSH_URL_API.format(site=site, token='<YOUR_TOKEN>')}")
        return

    api = PUSH_URL_API.format(site=site, token=token)
    code, body = post_to_baidu(api, "\n".join(urls))
    print(f"\n[主动推送] HTTP {code if code is not None else 'N/A（网络/超时错误，详见下方）'}")
    print(body)

    if sitemap_push:
        sm_api = SITEMAP_API.format(site=site, token=token)
        sm_url = site.rstrip("/") + "/sitemap.xml"
        c2, b2 = post_to_baidu(sm_api, sm_url)
        print(f"\n[sitemap 提交] HTTP {c2 if c2 is not None else 'N/A（网络/超时错误）'}")
        print(b2)


if __name__ == "__main__":
    main()
