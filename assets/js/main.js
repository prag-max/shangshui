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
})();
