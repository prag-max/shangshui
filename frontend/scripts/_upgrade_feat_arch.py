# -*- coding: utf-8 -*-
"""④ 模块升级：旧 feat-arch → 全新 arch 架构图（含 HTML + components.css + pages.css）"""
import re, os

ROOT = r"F:\website\frontend"

# ============ 1) index.html ④ section 整体替换 ============
new_section_html = '''<section class="section" id="features-overview">
  <div class="container">
    <div class="text-center reveal">
      <div class="section-label">功能架构</div>
      <h2 class="section-title">全链路功能，一目了然</h2>
      <p class="section-sub">围绕"抄表→计费→收费"三大核心，九大模块协同支撑，覆盖水司营收管理全流程。</p>
    </div>

    <div class="arch reveal">
      <div class="arch__top">
        <div class="arch-zone arch-zone--left reveal reveal-delay-1">
          <div class="arch-end">
            <span class="arch-end__icon"><svg viewBox="0 0 256 256" fill="currentColor"><use href="#ph-buildings"/></svg></span>
            <div>
              <h4>PC 管理端</h4>
              <span class="arch-end__count">9 项功能</span>
            </div>
          </div>
          <ul class="arch-chips">
            <li>用户管理</li>
            <li>抄表管理</li>
            <li>计费管理</li>
            <li>收费管理</li>
            <li>账务处理</li>
            <li>票据管理</li>
            <li>表务管理</li>
            <li>报表中心</li>
            <li>业务参数</li>
          </ul>
        </div>

        <div class="arch-link arch-link--l" aria-hidden="true"></div>

        <div class="arch-hub reveal reveal-delay-2">
          <div class="arch-hub__ring" aria-hidden="true"></div>
          <span class="arch-hub__logo"><svg viewBox="0 0 256 256" fill="currentColor"><use href="#ph-buildings-fill"/></svg></span>
          <h3>营收管理平台</h3>
          <p class="arch-hub__sub">9 大模块 · 50 子模块 · 136 功能页面</p>
          <span class="arch-hub__meta">三端统一 · 数据互通</span>
        </div>

        <div class="arch-link arch-link--r" aria-hidden="true"></div>

        <div class="arch-zone arch-zone--right reveal reveal-delay-3">
          <div class="arch-end">
            <span class="arch-end__icon"><svg viewBox="0 0 256 256" fill="currentColor"><use href="#ph-device-mobile"/></svg></span>
            <div>
              <h4>抄表员 APP</h4>
              <span class="arch-end__count">9 项功能</span>
            </div>
          </div>
          <ul class="arch-chips">
            <li>抄表录入</li>
            <li>抄表轨迹</li>
            <li>抄表复核</li>
            <li>追加抄表</li>
            <li>异常上报</li>
            <li>数据下载</li>
            <li>数据上传</li>
            <li>抄表统计</li>
            <li>收费统计</li>
          </ul>
        </div>
      </div>

      <div class="arch-link arch-link--b" aria-hidden="true"></div>

      <div class="arch__bottom reveal reveal-delay-2">
        <div class="arch-zone arch-zone--bottom">
          <div class="arch-end">
            <span class="arch-end__icon"><svg viewBox="0 0 256 256" fill="currentColor"><use href="#ph-chat-circle"/></svg></span>
            <div>
              <h4>用户公众号</h4>
              <span class="arch-end__count">8 项功能</span>
            </div>
          </div>
          <ul class="arch-chips arch-chips--row">
            <li>水费查询</li>
            <li>在线缴费</li>
            <li>账单推送</li>
            <li>欠费提醒</li>
            <li>停水通知</li>
            <li>自助报数</li>
            <li>用水记录</li>
            <li>用户绑定</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</section>'''

html_path = os.path.join(ROOT, "index.html")
t = open(html_path, encoding="utf-8").read()
start = t.find('<section class="section" id="features-overview">')
end = t.find("</section>", start) + len("</section>")
assert start != -1 and end != -1, "④ section 未找到"
old_section = t[start:end]
assert "feat-arch" in old_section, "未找到旧 feat-arch 内容"
t = t[:start] + new_section_html + t[end:]
open(html_path, "w", encoding="utf-8").write(t)
print("✅ index.html ④ section 已替换为全新架构图")

# ============ 2) components.css：feat-arch 区块 → arch 区块 ============
new_arch_css = '''/* ---------- 架构图 · 三端协同（全链路功能架构） ---------- */
.arch {
  position: relative;
  display: flex;
  flex-direction: column;
  padding: 52px 44px 46px;
  border-radius: 32px;
  border: 1px solid rgba(2, 132, 199, 0.12);
  background:
    radial-gradient(620px 320px at 50% -5%, rgba(6, 182, 212, 0.09), transparent 70%),
    radial-gradient(520px 280px at 8% 45%, rgba(2, 132, 199, 0.06), transparent 70%),
    radial-gradient(520px 280px at 92% 45%, rgba(2, 132, 199, 0.06), transparent 70%),
    linear-gradient(180deg, #FFFFFF 0%, #F7FBFF 100%);
  overflow: hidden;
}
.arch::before {
  content: '';
  position: absolute; inset: 0;
  background-image: radial-gradient(rgba(2, 132, 199, 0.12) 1px, transparent 1px);
  background-size: 24px 24px;
  opacity: 0.45;
  pointer-events: none;
  -webkit-mask-image: radial-gradient(ellipse at center, #000 25%, transparent 72%);
  mask-image: radial-gradient(ellipse at center, #000 25%, transparent 72%);
}

.arch__top {
  position: relative; z-index: 1;
  display: flex; align-items: center; justify-content: center;
  gap: 20px;
}
.arch__bottom {
  position: relative; z-index: 1;
  display: flex; justify-content: center;
}

.arch-hub {
  position: relative; flex: 0 0 auto;
  width: 320px; padding: 36px 28px 30px;
  border-radius: 26px;
  background: linear-gradient(135deg, #0284C7 0%, #06B6D4 60%, #0EA5E9 100%);
  color: #fff; text-align: center;
  box-shadow: 0 22px 55px rgba(2, 132, 199, 0.35), 0 6px 20px rgba(6, 182, 212, 0.28);
}
.arch-hub__ring {
  position: absolute; inset: -10px; border-radius: 34px;
  border: 1.5px solid rgba(6, 182, 212, 0.4);
  animation: archRing 3s ease-in-out infinite;
  pointer-events: none;
}
@keyframes archRing {
  0%, 100% { transform: scale(1); opacity: 0.7; }
  50% { transform: scale(1.045); opacity: 0.35; }
}
.arch-hub__logo {
  display: inline-flex; align-items: center; justify-content: center;
  width: 52px; height: 52px; margin-bottom: 16px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.18);
  border: 1px solid rgba(255, 255, 255, 0.35);
  color: #fff;
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
}
.arch-hub__logo svg { width: 26px; height: 26px; }
.arch-hub h3 {
  font-size: 1.4rem; color: #fff;
  margin-bottom: 8px; letter-spacing: 0.02em;
}
.arch-hub__sub {
  font-size: 0.8rem; color: rgba(255, 255, 255, 0.85);
  margin-bottom: 16px; letter-spacing: 0.04em;
}
.arch-hub__meta {
  display: inline-block;
  font-size: 0.72rem; font-weight: 600; letter-spacing: 0.1em;
  color: #fff; background: rgba(255, 255, 255, 0.16);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: var(--radius-pill); padding: 5px 14px;
}

.arch-zone {
  position: relative;
  flex: 0 0 auto; width: 264px;
  background: #fff; border: 1px solid var(--border);
  border-radius: 20px; padding: 22px 20px 20px;
  box-shadow: 0 14px 40px rgba(15, 23, 42, 0.06);
}
.arch-zone::before {
  content: '';
  position: absolute; top: 0; left: 22px; right: 22px; height: 3px;
  border-radius: 0 0 6px 6px;
  background: linear-gradient(90deg, var(--brand), var(--cyan));
}
.arch-end { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
.arch-end__icon {
  flex: 0 0 auto; width: 44px; height: 44px; border-radius: 13px;
  display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, var(--brand), var(--cyan));
  color: #fff; box-shadow: 0 6px 16px rgba(2, 132, 199, 0.28);
}
.arch-end__icon svg { width: 22px; height: 22px; }
.arch-end h4 { font-size: 1.02rem; margin: 0 0 3px; color: var(--text); }
.arch-end__count {
  display: inline-block; font-size: 0.7rem; font-weight: 600;
  color: var(--brand-dark); background: var(--brand-light);
  border-radius: var(--radius-pill); padding: 2px 9px; letter-spacing: 0.04em;
}

.arch-chips { list-style: none; margin: 0; padding: 0; display: grid; gap: 8px; }
.arch-chips li {
  display: flex; align-items: center; gap: 9px;
  font-size: var(--text-sm); color: var(--text-secondary);
  background: var(--bg-alt); border: 1px solid var(--border-light);
  border-radius: 10px; padding: 8px 12px;
  transition: transform var(--duration-fast) var(--ease-out),
              border-color var(--duration-fast) var(--ease-out),
              background var(--duration-fast) var(--ease-out),
              box-shadow var(--duration-fast) var(--ease-out);
}
.arch-chips li::before {
  content: '';
  flex: 0 0 auto; width: 6px; height: 6px; border-radius: 50%;
  background: linear-gradient(135deg, var(--brand), var(--cyan));
}
.arch-chips li:hover {
  transform: translateX(4px); background: #fff;
  border-color: var(--brand-light); box-shadow: var(--shadow-sm);
}
.arch-zone--right .arch-chips li:hover { transform: translateX(-4px); }
.arch-chips--row { grid-template-columns: repeat(4, 1fr); }
.arch-chips--row li { justify-content: center; text-align: center; }

.arch-link {
  position: relative; flex: 1 1 auto; max-width: 170px; min-width: 32px;
  height: 2px; border-radius: 2px;
  background: linear-gradient(90deg, rgba(2, 132, 199, 0.18), rgba(6, 182, 212, 0.65));
}
.arch-link::before {
  content: '';
  position: absolute; top: 50%; left: -2px;
  width: 8px; height: 8px; margin-top: -4px; border-radius: 50%;
  background: var(--cyan);
  box-shadow: 0 0 10px rgba(6, 182, 212, 0.9);
  animation: archFlow 2.4s linear infinite;
}
.arch-link--r::before { animation-name: archFlowRev; }
.arch-link--b {
  flex: none; width: 2px; height: 46px; margin: 6px auto;
  background: linear-gradient(180deg, rgba(2, 132, 199, 0.18), rgba(6, 182, 212, 0.65));
}
.arch-link--b::before {
  left: 50%; top: -2px; margin-left: -4px; margin-top: 0;
  animation-name: archFlowDown;
}
@keyframes archFlow {
  0% { left: -2px; opacity: 0; }
  12% { opacity: 1; }
  88% { opacity: 1; }
  100% { left: calc(100% - 6px); opacity: 0; }
}
@keyframes archFlowRev {
  0% { left: calc(100% - 6px); opacity: 0; }
  12% { opacity: 1; }
  88% { opacity: 1; }
  100% { left: -2px; opacity: 0; }
}
@keyframes archFlowDown {
  0% { top: -2px; opacity: 0; }
  12% { opacity: 1; }
  88% { opacity: 1; }
  100% { top: calc(100% - 6px); opacity: 0; }
}
'''

css_path = os.path.join(ROOT, "assets", "css", "src", "components.css")
css = open(css_path, encoding="utf-8").read()
m1 = css.find("/* ---------- Features Architecture (全链路功能架构) ---------- */")
m2 = css.find("/* ---------- Features Grid ---------- */")
assert m1 != -1 and m2 != -1 and m2 > m1, "components.css 区块标记未找到"
css = css[:m1] + new_arch_css.strip() + "\n\n" + css[m2:]
open(css_path, "w", encoding="utf-8").write(css)
print("✅ components.css feat-arch 区块已替换为 arch 区块")

# ============ 3) pages.css 响应式规则替换 ============
pp = os.path.join(ROOT, "assets", "css", "src", "pages.css")
p = open(pp, encoding="utf-8").read()

# 3.1 1100 断点
old_1100 = """  .feat-card { padding: 24px 18px 22px; }
  .feat-card--main { padding-top: 40px; }
  .feat-card__head { gap: 10px; }
  .feat-card__icon { width: 44px; height: 44px; border-radius: 12px; }
  .feat-card__icon svg { width: 22px; height: 22px; }
  .feat-support__grid { grid-template-columns: repeat(3, 1fr); }"""
new_1100 = """  .arch { padding: 40px 28px 38px; }
  .arch-hub { width: 290px; padding: 32px 22px 26px; }
  .arch-zone { width: 236px; padding: 20px 16px 18px; }
  .arch-chips li { padding: 7px 10px; }"""
assert old_1100 in p, "1100 断点 feat 规则未找到"
p = p.replace(old_1100, new_1100)

# 3.2 980 断点追加（三端改上下布局）
old_980_anchor = "  .flow--steps .flow-arrow { padding: 9px 0; font-size: 1.1rem; }"
new_980 = old_980_anchor + """
  .arch__top { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; align-items: start; }
  .arch-hub { grid-column: 1 / -1; grid-row: 1; justify-self: center; width: min(100%, 360px); }
  .arch-zone--left { grid-column: 1; grid-row: 2; width: auto; }
  .arch-zone--right { grid-column: 2; grid-row: 2; width: auto; }
  .arch-link--l, .arch-link--r { display: none; }
  .arch-link--b { height: 30px; margin: 4px auto; }"""
assert old_980_anchor in p, "980 断点锚点未找到"
p = p.replace(old_980_anchor, new_980)

# 3.3 640 断点替换
old_640 = """  .feat-main { grid-template-columns: 1fr; gap: 10px; margin-bottom: 28px; }
  .feat-arrow { transform: rotate(90deg); padding: 4px 0; font-size: 1.4rem; }
  .feat-card--main { padding: 22px 18px; }
  .feat-support { padding: 20px 18px; }
  .feat-support__grid { grid-template-columns: repeat(2, 1fr); gap: 10px; }
  .feat-mini { padding: 12px 10px; }"""
new_640 = """  .arch { padding: 26px 16px 24px; border-radius: 24px; }
  .arch__top { grid-template-columns: 1fr; gap: 14px; }
  .arch-zone--left { grid-column: 1; grid-row: 2; }
  .arch-zone--right { grid-column: 1; grid-row: 3; }
  .arch-hub { width: 100%; padding: 28px 18px 24px; }
  .arch-hub h3 { font-size: 1.2rem; }
  .arch-chips--row { grid-template-columns: repeat(2, 1fr); }
  .arch-zone { padding: 18px 14px 16px; }"""
assert old_640 in p, "640 断点 feat 规则未找到"
p = p.replace(old_640, new_640)

open(pp, "w", encoding="utf-8").write(p)
print("✅ pages.css 响应式规则已更新")

print("\n全部完成")
