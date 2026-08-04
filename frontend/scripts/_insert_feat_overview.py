# -*- coding: utf-8 -*-
p = r"F:\website\frontend\index.html"
t = open(p, encoding="utf-8").read()

# 分区编号顺移（从大到小递增，避免撞号）
replacements = [
    ("<!-- ======== ⑧ 合作伙伴 ======== -->",                       "<!-- ======== ⑩ 合作伙伴 ======== -->"),
    ("<!-- ======== ⑦ Bottom CTA ======== -->",                      "<!-- ======== ⑨ Bottom CTA ======== -->"),
    ("<!-- ======== ⑥ 客户案例（脱敏） ======== -->",                  "<!-- ======== ⑧ 客户案例（脱敏） ======== -->"),
    ("<!-- ======== ⑥ 功能模块展示 ======== -->",                     "<!-- ======== ⑦ 功能模块展示 ======== -->"),
    ("<!-- ======== ⑤ 核心价值 ======== -->",                         "<!-- ======== ⑥ 核心价值 ======== -->"),
    ("<!-- ======== ④ 小水厂的难处，我们懂 ======== -->",              "<!-- ======== ⑤ 小水厂的难处，我们懂 ======== -->"),
]
for old, new in replacements:
    n = t.count(old)
    assert n == 1, f"expected 1 match, got {n}: {old[:50]}"
    t = t.replace(old, new)
print("✅ 6 处分区编号顺移完成")

# 在已重编号为 ⑤ 的小水厂的难处之前插入新模块
anchor = "<!-- ======== ⑤ 小水厂的难处，我们懂 ======== -->"
assert anchor in t

new_section = """<!-- ======== ④ 全链路功能架构 ======== -->
<section class="section" id="features-overview">
  <div class="container">
    <div class="text-center reveal">
      <div class="section-label">功能架构</div>
      <h2 class="section-title">全链路功能，一目了然</h2>
      <p class="section-sub">围绕"抄表→计费→收费"三大核心，九大模块协同支撑，覆盖水司营收管理全流程。</p>
    </div>

    <div class="feat-arch reveal">
      <div class="feat-main">
        <div class="feat-card feat-card--main reveal reveal-delay-1">
          <span class="feat-card__tag">核心 01</span>
          <div class="feat-card__head">
            <span class="feat-card__icon"><svg viewBox="0 0 256 256" fill="currentColor"><use href="#ph-clipboard-text"/></svg></span>
            <div class="feat-card__title"><h3>抄表管理</h3></div>
          </div>
          <p class="feat-card__value">数据准确 · 效率提升</p>
          <ul class="feat-card__list">
            <li>移动端现场录入（APP）</li>
            <li>抄表复核与校验审核</li>
            <li>异常水量自动预警</li>
            <li>抄表计划与线路规划</li>
            <li>抄表轨迹全程留痕</li>
          </ul>
        </div>

        <div class="feat-arrow reveal reveal-delay-2" aria-hidden="true">→</div>

        <div class="feat-card feat-card--main reveal reveal-delay-2">
          <span class="feat-card__tag">核心 02</span>
          <div class="feat-card__head">
            <span class="feat-card__icon"><svg viewBox="0 0 256 256" fill="currentColor"><use href="#ph-calculator"/></svg></span>
            <div class="feat-card__title"><h3>计费管理</h3></div>
          </div>
          <p class="feat-card__value">算得清楚 · 差错趋零</p>
          <ul class="feat-card__list">
            <li>开账计费（基本/排污/阶梯）</li>
            <li>阶梯水价自动核算</li>
            <li>损耗分摊透明可查</li>
            <li>账单自动生成与推送</li>
          </ul>
        </div>

        <div class="feat-arrow reveal reveal-delay-3" aria-hidden="true">→</div>

        <div class="feat-card feat-card--main reveal reveal-delay-3">
          <span class="feat-card__tag">核心 03</span>
          <div class="feat-card__head">
            <span class="feat-card__icon"><svg viewBox="0 0 256 256" fill="currentColor"><use href="#ph-currency-cny"/></svg></span>
            <div class="feat-card__title"><h3>收费管理</h3></div>
          </div>
          <p class="feat-card__value">应收尽收 · 账目清晰</p>
          <ul class="feat-card__list">
            <li>窗口收费（现金/扫码/POS）</li>
            <li>银行代扣与多渠道缴费</li>
            <li>票据管理（已收/未收开票）</li>
            <li>欠费分级催缴</li>
          </ul>
        </div>
      </div>

      <div class="feat-support">
        <h3 class="feat-support__title">全链路支撑 · 六大辅助模块</h3>
        <div class="feat-support__grid">
          <div class="feat-mini">
            <span class="feat-mini__icon"><svg viewBox="0 0 256 256" fill="currentColor"><use href="#ph-user"/></svg></span>
            <div>
              <h4>用户管理</h4>
              <p>立户 · 档案 · 优惠</p>
            </div>
          </div>
          <div class="feat-mini">
            <span class="feat-mini__icon"><svg viewBox="0 0 256 256" fill="currentColor"><use href="#ph-arrows-left-right"/></svg></span>
            <div>
              <h4>账务处理</h4>
              <p>减免 · 冲正 · 呆坏账</p>
            </div>
          </div>
          <div class="feat-mini">
            <span class="feat-mini__icon"><svg viewBox="0 0 256 256" fill="currentColor"><use href="#ph-receipt"/></svg></span>
            <div>
              <h4>票据管理</h4>
              <p>票号生命周期</p>
            </div>
          </div>
          <div class="feat-mini">
            <span class="feat-mini__icon"><svg viewBox="0 0 256 256" fill="currentColor"><use href="#ph-wrench"/></svg></span>
            <div>
              <h4>表务管理</h4>
              <p>换表 · 库存 · 开关阀</p>
            </div>
          </div>
          <div class="feat-mini">
            <span class="feat-mini__icon"><svg viewBox="0 0 256 256" fill="currentColor"><use href="#ph-chart-bar"/></svg></span>
            <div>
              <h4>报表中心</h4>
              <p>应收 · 实收 · 抄表分析</p>
            </div>
          </div>
          <div class="feat-mini">
            <span class="feat-mini__icon"><svg viewBox="0 0 256 256" fill="currentColor"><use href="#ph-gear"/></svg></span>
            <div>
              <h4>业务参数</h4>
              <p>价格 · 权限 · 计费规则</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

"""

t = t.replace(anchor, new_section + anchor, 1)
open(p, "w", encoding="utf-8").write(t)
print("✅ 新模块已插入")