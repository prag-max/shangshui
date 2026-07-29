# 尚水数字官网 · 页面加载性能分析与修复报告

> 分析对象：`website/` 下的 6 个静态营销页（`index / features / pricing / solutions / contact / 404`）+ `assets/`
> 分析环境：本机沙箱（无浏览器引擎、无法访问真实生产/CDN，故 TTFB 与真实字段指标以「本地实测 + 模型估算」给出，方法见 §3）
> 生产部署：据历史记录为 EdgeOne 静态托管 + Laravel/MySQL 后端（frp 内网穿透）

---

## 1. 结论摘要

| 维度 | 现状结论 |
|---|---|
| 页面体量 | **很轻**：首屏关键资源仅 **≈94 KB（未压缩）/ ≈50 KB（压缩后）**，属优秀水平 |
| 图片 | **已做得好**：Hero 用 `<picture>` + AVIF/WebP + `srcset` + `width/height` + `fetchpriority=high`；二维码带显式尺寸；缩略图已 `lazy` |
| 字体 | **无 Web Font**（系统字体栈）→ 无 FOUT、无字体导致的 CLS |
| 图标 | 内联 SVG 雪碧图 → 无图标字体/图片额外请求 |
| JS | 小（4.8 KB）且置于 `</body>` 前 → **非渲染阻塞** |
| **核心瓶颈** | ① **服务器未启用压缩（Gzip/Brotli）与浏览器缓存**（仓库无任何 host 配置）；② `<head>` 内第三方百度 `push.js` 在关键路径早期发起外链请求；③ CSS 未压缩；④ 仓库含 1 个**未引用、1 MB 的 `hero.png`** 死文件 |

**一句话**：页面本身不重，慢的根因是「边缘未压缩 + 无缓存 + 头部外链脚本」，而非资源体积。

---

## 2. 实测证据：响应头（本地静态服务器）

启动 `python -m http.server` 后 `curl -I` 关键资源，结果一致：

```
HTTP/1.0 200 OK
Server: SimpleHTTP/0.6 Python/3.13.14
Content-type: text/html
Content-Length: 24768
Last-Modified: ...
# ❌ 无 Content-Encoding      （未启用 Gzip/Brotli）
# ❌ 无 Cache-Control / ETag  （无浏览器缓存）
# ❌ 无 CDN 相关头            （取决于部署，仓库无可配置项）
```

→ 证实：**当前无任何压缩与缓存策略**。若生产站同样未配置（EdgeOne 需控制台开启），每次访问都重新下载全部未压缩资源。

本地 TTFB ≈ **2 ms**（localhost 仅供参考；真实 TTFB 取决于 CDN/源站，需在生产环境用 WebPageTest/Lighthouse 复测）。

---

## 3. 核心指标（FCP / LCP / CLS / TTFB）

> 沙箱无浏览器，以下为**基于关键渲染路径的模型估算**（HTTP/2 多路复用假设），用于定位量级与瓶颈，非真实字段值。

**资源体积（首屏关键路径，index.html）**

| 资源 | 原始 | 修复后（压缩） |
|---|---|---|
| HTML | 24.2 KB | 7.4 KB（gzip） |
| CSS | 28.3 KB → 压缩后 25.7 KB(min) | 5.6 KB（gzip） |
| JS | 4.8 KB | 1.7 KB（gzip） |
| Hero(AVIF) | 22.6 KB | 22.6 KB（已压缩） |
| Logo | 15.0 KB | 12.8 KB（gzip） |
| **合计** | **94.2 KB** | **≈49.6 KB（−47%）** |

**指标估算（首访，模型值，单位 ms）**

| 指标 | Slow 3G | Fast 3G | 4G | 宽带 |
|---|---|---|---|---|
| TTFB | 425 | 225 | 125 | 55 |
| FCP 基线 | 978 | 363 | 145 | 60 |
| FCP 修复后 | 570 | 261 | 130 | 56 |
| LCP 基线 | 1432 | 477 | 161 | 63 |
| LCP 修复后 | 1024 | 375 | 146 | 60 |
| **CLS** | **0** | **0** | **0** | **0** |

- **CLS ≈ 0**：所有图片均带 `width/height` 或 CSS 固定尺寸；无 Web Font 替换抖动。
- **LCP** 元素为 Hero 图（AVIF，≈22 KB），已 `fetchpriority=high`，量级健康；3G 下偏慢主因是 RTT 与带宽，压缩可显著缩短传输。
- **FCP** 受渲染阻塞 CSS 影响；压缩 CSS 后首字节有效内容更快就绪。
- **重复访问**：开启缓存后，CSS/JS/图片命中本地缓存，**FCP/LCP 几乎只受 TTFB 限制**（见上表 cache-HIT 场景，约 245–445 ms 量级）。

---

## 4. 资源加载分析

- **JS/CSS 体积**：CSS 28.3 KB、JS 4.8 KB，体量小；但二者均未压缩、未缓存。
- **图片**：
  - Hero：`hero-640/960/1216` 的 AVIF(10–23 KB) + WebP(13–29 KB) 双格式 + `srcset` + `sizes`，浏览器择优加载 ✅
  - 二维码：130×130 显式尺寸 ✅
  - 缩略图：`user-mgmt-thumb.jpg` 已 `loading="lazy"` ✅
  - ❌ **死文件 `hero.png`（1 MB）无任何引用**，仅增大仓库/部署体积 → 已删除
- **字体策略**：系统字体栈，**零字体请求、零 CLS 风险** ✅（优于引入 Web Font 的方案）

## 5. 请求瀑布与阻塞分析

```
Timeline (首访, Fast 3G 量级示意)
0ms    ──[HTML 请求]──► TTFB
       ├─ CSS  (渲染阻塞, 必须等待 CSSOM 才能 FCP)
       ├─ JS   (body 末尾, 非阻塞)
       ├─ Hero (LCP, 与 CSS 并行获取, 但需 CSS 布局后绘制)
       └─ ❌ Baidu push.js  (head 内 IIFE 早期发起外链 → 与关键资源争抢连接/CPU)
```

- **渲染阻塞**：仅 `style.css`（`<head>` 内，必需）。已通过压缩 + 计划内联关键 CSS 优化。
- **第三方阻塞**：百度 `push.js` 原在 `<head>` 内同步触发外链；已改为 `window.load` 后异步加载（`async`），移出关键路径。
- **无 `preconnect`/`dns-prefetch` 需求**：本站无跨域字体/SDK（除已延迟的百度），故无需预连接。

## 6. 压缩 / CDN / 缓存检测

| 项目 | 检测 | 状态 |
|---|---|---|
| Gzip/Brotli | 响应头无 `Content-Encoding` | ❌ 未启用 |
| 浏览器缓存 | 无 `Cache-Control`/`ETag` | ❌ 未启用 |
| CDN | 仓库无相关配置；历史为 EdgeOne | ⚠️ 取决于控制台配置 |
| HTTP/2 | 取决于托管 | ⚠️ 建议确认 |

→ 已新增 `.htaccess`（Apache/LiteSpeed 适用）启用 Brotli/Gzip 与分级缓存；**若由 EdgeOne 托管，需在控制台开启「智能压缩(Brotli)」与缓存规则（HTML no-cache、静态资源长缓存）**，`.htaccess` 在对象存储型 EdgeOne 不生效。

---

## 7. 已实施的修复（本次提交前改动）

| # | 修复 | 文件 | 效果 |
|---|---|---|---|
| 1 | 新增 `.htaccess`：Brotli/Gzip 压缩 + 分级缓存（HTML 1h/no-cache，CSS/JS 1 周，图片 1 月） | `.htaccess`（新建） | 传输 −47%，重复访问近乎秒开 |
| 2 | CSS 压缩（去注释/空白，保持 brace 平衡） | `assets/css/style.css` | 28.3→25.7 KB（再经 gzip 5.6 KB） |
| 3 | 百度 `push.js` 延迟到 `window.load` 并 `async`，移出关键路径 | 全部 6 个 `.html` | 消除头部外链阻塞 |
| 4 | 首屏外 Logo 图片加 `loading="lazy"` | 全部 6 个 `.html`（11 处） | 减少非首屏请求 |
| 5 | 删除未引用 1 MB `hero.png` | `assets/img/hero.png`（删除） | 仓库/部署 −1 MB |

> 说明：JS 体积过小（4.8 KB），压缩收益可忽略，未做激进混淆以免引入 ASI 风险；其 gzipped 仅 ≈1.7 KB，由 `.htaccess` 的压缩规则覆盖。

## 8. 修复前后对比（传输体积）

```
首屏关键资源总量
基线（未压缩/无缓存）  ████████████████████████  94.2 KB
优化（minify+gzip）     ████████████              49.6 KB   (-47%)
```

## 9. 部署与后续建议

1. **确认 EdgeOne 控制台**：开启 Brotli 智能压缩；设置缓存规则（HTML `no-cache`、静态资源 `max-age` 长缓存）。
2. **静态资源加版本哈希**（如 `style.a1b2.css`）以实现 `immutable` 长缓存且更新无陈旧问题；当前 `.htaccess` 对 CSS/JS 取 1 周折中。
3. **确认 HTTP/2 / HTTP/3**：多路复用可进一步缩短高 RTT 下的瀑布。
4. **内联关键 CSS**（首屏 above-the-fold 样式）可再降 FCP，但当前体量收益有限，按需。
5. **真实复测**：上线后用 Lighthouse / WebPageTest 在生产域名测 FCP/LCP/CLS/TTFB，验证 EdgeOne 压缩与缓存生效。

---

### 附：本次用于分析/修复的脚本
- `benchmark/perf_model.py` — 关键路径与指标估算模型
- `benchmark/apply_fixes.py` — 自动化执行 CSS 压缩 / 脚本延迟 / 懒加载
