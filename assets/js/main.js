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
})();
