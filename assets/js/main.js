/* 供水营收系统官网 · 交互脚本 */
(function () {
  // 移动端导航
  var ham = document.querySelector('.hamburger');
  var links = document.querySelector('.nav-links');
  if (ham && links) {
    ham.addEventListener('click', function () {
      links.classList.toggle('open');
      var s = ham.querySelectorAll('span');
      ham.classList.toggle('active');
    });
    links.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () { links.classList.remove('open'); });
    });
  }
  // 页脚年份
  var y = document.getElementById('year');
  if (y) y.textContent = new Date().getFullYear();
  // 报价表 版本切换（高亮当前列）
  document.querySelectorAll('[data-tier]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var t = btn.getAttribute('data-tier');
      document.querySelectorAll('[data-tier]').forEach(function (b) { b.classList.remove('active'); });
      btn.classList.add('active');
      document.querySelectorAll('table.tbl').forEach(function (tbl) {
        tbl.querySelectorAll('tr').forEach(function (tr) {
          var cell = tr.querySelector('[data-col="' + t + '"]');
          tr.querySelectorAll('td,th').forEach(function (c) { c.style.background = ''; });
          if (cell) cell.style.background = '#eef4ff';
        });
      });
    });
  });

  // 报价页：展开 / 收起完整功能对比表
  document.querySelectorAll('[data-expand]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var id = btn.getAttribute('data-expand');
      var el = document.getElementById(id);
      if (!el) return;
      var hidden = el.hasAttribute('hidden');
      if (hidden) {
        el.removeAttribute('hidden');
        btn.textContent = btn.getAttribute('data-text-less') || '收起完整功能对比';
      } else {
        el.setAttribute('hidden', '');
        btn.textContent = btn.getAttribute('data-text-more') || '查看完整全部功能对比';
        // 收起后让按钮保持在视野内
        btn.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    });
  });

  // 首页内锚点导航高亮（scroll-spy）：滚动到 #product 时“产品介绍”高亮
  var navAnchors = document.querySelectorAll('.nav-links a[href^="#"]');
  if (navAnchors.length) {
    var homeLink = document.querySelector('.nav-links a[href="index.html"]');
    var map = {}, secs = [];
    navAnchors.forEach(function (a) {
      var id = a.getAttribute('href').slice(1);
      var sec = document.getElementById(id);
      if (sec) { map[id] = a; secs.push(sec); }
    });
    if (secs.length) {
      var visible = {};
      function applySpy() {
        var activeId = null;
        for (var i = 0; i < secs.length; i++) {
          if (visible[secs[i].id]) { activeId = secs[i].id; break; }
        }
        document.querySelectorAll('.nav-links a').forEach(function (a) { a.classList.remove('active'); });
        if (activeId && map[activeId]) {
          map[activeId].classList.add('active');
        } else if (homeLink) {
          homeLink.classList.add('active');
        }
      }
      var obs = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) { visible[e.target.id] = e.isIntersecting; });
        applySpy();
      }, { rootMargin: '-45% 0px -50% 0px', threshold: 0 });
      secs.forEach(function (s) { obs.observe(s); });
    }
  }

  // 功能卡片截图弹窗（Lightbox）
  var lb = document.getElementById('lightbox');
  var lbImg = document.getElementById('lightboxImg');
  if (lb && lbImg) {
    // 预加载：鼠标悬停 / 触摸即提前缓存大图，点击时秒出
    document.querySelectorAll('.mod-shot').forEach(function (btn) {
      var src = btn.getAttribute('data-zoom');
      function prefetch() {
        if (src && !btn._pre) { btn._pre = new Image(); btn._pre.src = src; }
      }
      btn.addEventListener('mouseenter', prefetch, { once: true });
      btn.addEventListener('touchstart', prefetch, { once: true, passive: true });
    });
    function openLightbox(src, cap) {
      lb.classList.add('loading');
      lbImg.onload = function () { lb.classList.remove('loading'); };
      lbImg.alt = (cap || '系统界面大图');
      var capEl = lb.querySelector('.lightbox-cap');
      if (capEl) capEl.textContent = cap || '';
      lbImg.src = src;
      lb.classList.add('open');
      lb.setAttribute('aria-hidden', 'false');
      document.body.classList.add('lb-lock');
    }
    function closeLightbox() {
      lb.classList.remove('open', 'loading');
      lb.setAttribute('aria-hidden', 'true');
      document.body.classList.remove('lb-lock');
      // 延迟清空，避免关闭动画时图片闪烁
      setTimeout(function () { if (!lb.classList.contains('open')) lbImg.src = ''; }, 300);
    }
    document.querySelectorAll('.mod-shot').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var src = btn.getAttribute('data-zoom');
        if (src) openLightbox(src, btn.getAttribute('data-cap'));
      });
    });
    // 点击遮罩空白处关闭（点击图片本身不关闭）
    lb.addEventListener('click', function (e) {
      if (e.target === lb || e.target.classList.contains('lightbox-cap')) closeLightbox();
    });
    lb.querySelector('.lightbox-close').addEventListener('click', closeLightbox);
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && lb.classList.contains('open')) closeLightbox();
    });
  }
})();
