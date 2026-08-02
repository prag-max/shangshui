/* ============================================================
   尚水数字 · 供水营收系统官网 - 交互脚本 v2.0
   优化: ARIA状态管理 / 焦点陷阱 / rAF节流 / reduced-motion
   ============================================================ */
(function () {
  'use strict';

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---- Mobile Nav + Overlay + ARIA ---- */
  const ham = document.querySelector('.hamburger');
  const navLinks = document.querySelector('.nav-links');
  if (ham && navLinks) {
    ham.setAttribute('aria-expanded', 'false');
    ham.setAttribute('aria-controls', 'navlinks');
    let navOverlay = document.querySelector('.nav-overlay');
    if (!navOverlay) {
      navOverlay = document.createElement('div');
      navOverlay.className = 'nav-overlay';
      navOverlay.setAttribute('aria-hidden', 'true');
      document.body.appendChild(navOverlay);
    }
    const setNav = (open) => {
      navLinks.classList.toggle('open', open);
      ham.classList.toggle('active', open);
      ham.setAttribute('aria-expanded', open ? 'true' : 'false');
      navOverlay.classList.toggle('show', open);
      navOverlay.setAttribute('aria-hidden', open ? 'false' : 'true');
      document.body.classList.toggle('nav-open', open);
      if (!open) {
        setTimeout(() => { if (ham.offsetParent !== null) ham.focus(); }, 50);
      }
    };
    ham.addEventListener('click', () => setNav(!navLinks.classList.contains('open')));
    navOverlay.addEventListener('click', () => setNav(false));
    navLinks.querySelectorAll('a').forEach(a => {
      a.addEventListener('click', () => setNav(false));
    });
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape' && navLinks.classList.contains('open')) setNav(false);
    });
  }

  /* ---- Header Scroll Effect (rAF throttled + passive) ---- */
  const header = document.querySelector('.site-header');
  if (header) {
    let ticking = false;
    const updateHeader = () => {
      header.classList.toggle('scrolled', window.scrollY > 10);
      ticking = false;
    };
    window.addEventListener('scroll', () => {
      if (!ticking) {
        requestAnimationFrame(updateHeader);
        ticking = true;
      }
    }, { passive: true });
  }

  /* ---- Scroll Spy: Active Nav Link ---- */
  const navAnchors = document.querySelectorAll('.nav-links a[href^="#"]');
  const homeLink = document.querySelector('.nav-links a[href="index.html"]');
  if (navAnchors.length) {
    const sectionMap = {};
    const sections = [];
    navAnchors.forEach(a => {
      const id = a.getAttribute('href').slice(1);
      const sec = document.getElementById(id);
      if (sec) { sectionMap[id] = a; sections.push(sec); }
    });
    if (sections.length) {
      const visible = {};
      const observer = new IntersectionObserver(entries => {
        entries.forEach(e => { visible[e.target.id] = e.isIntersecting; });
        let activeId = null;
        for (let i = 0; i < sections.length; i++) {
          if (visible[sections[i].id]) { activeId = sections[i].id; break; }
        }
        document.querySelectorAll('.nav-links a').forEach(a => a.classList.remove('active'));
        if (activeId && sectionMap[activeId]) {
          sectionMap[activeId].classList.add('active');
        } else if (homeLink) {
          homeLink.classList.add('active');
        }
      }, { rootMargin: '-45% 0px -50% 0px', threshold: 0 });
      sections.forEach(s => observer.observe(s));
    }
  }

  /* ---- Scroll Reveal Animation (with variant support) ---- */
  const revealEls = document.querySelectorAll('.reveal');
  if (revealEls.length) {
    if (prefersReducedMotion) {
      revealEls.forEach(el => el.classList.add('visible'));
    } else {
      const revealObserver = new IntersectionObserver(entries => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            revealObserver.unobserve(entry.target);
          }
        });
      }, { threshold: 0.15, rootMargin: '0px 0px -40px 0px' });
      revealEls.forEach(el => revealObserver.observe(el));
    }
  }

  /* ---- Count Up Animation (rAF-based + reduced-motion) ---- */
  function animateCount(el, target, duration) {
    const suffix = el.getAttribute('data-suffix') || '';
    const prefix = el.getAttribute('data-prefix') || '';
    if (prefersReducedMotion) {
      el.textContent = prefix + target + suffix;
      return;
    }
    const start = performance.now();
    function step(now) {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = Math.round(target * eased);
      el.textContent = prefix + current + suffix;
      if (progress < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  const statEls = document.querySelectorAll('.stat-num[data-count]');
  if (statEls.length) {
    const countObserver = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const el = entry.target;
          const target = parseInt(el.getAttribute('data-count'), 10);
          if (target && !el._counted) {
            el._counted = true;
            animateCount(el, target, 2000);
          }
          countObserver.unobserve(el);
        }
      });
    }, { threshold: 0.5 });
    statEls.forEach(el => countObserver.observe(el));
  }

  /* ---- Smooth Count Up (for simple display) ---- */
  document.querySelectorAll('.count-up[data-target]').forEach(el => {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting && !el._counted) {
          el._counted = true;
          const target = parseInt(el.getAttribute('data-target'), 10);
          animateCount(el, target, 2000);
          observer.unobserve(el);
        }
      });
    }, { threshold: 0.5 });
    observer.observe(el);
  });

  /* ---- Lightbox with Focus Trap ---- */
  const lb = document.getElementById('lightbox');
  const lbImg = document.getElementById('lightboxImg');
  if (lb && lbImg) {
    let lbTrigger = null;

    function getFocusable() {
      return lb.querySelectorAll('button, [href], input, [tabindex]:not([tabindex="-1"])');
    }

    function openLightbox(src, cap) {
      lbTrigger = document.activeElement;
      lb.classList.add('loading');
      lbImg.onload = () => lb.classList.remove('loading');
      lbImg.alt = cap || '系统界面大图';
      const capEl = lb.querySelector('.lightbox-cap');
      if (capEl) capEl.textContent = cap || '';
      lbImg.src = src;
      lb.classList.add('open');
      lb.setAttribute('aria-hidden', 'false');
      document.body.classList.add('lb-lock');
      setTimeout(() => {
        const focusable = getFocusable();
        if (focusable.length > 0) focusable[0].focus();
      }, 100);
    }

    function closeLightbox() {
      lb.classList.remove('open', 'loading');
      lb.setAttribute('aria-hidden', 'true');
      document.body.classList.remove('lb-lock');
      setTimeout(() => { if (!lb.classList.contains('open')) lbImg.src = ''; }, 300);
      if (lbTrigger && typeof lbTrigger.focus === 'function') {
        lbTrigger.focus();
      }
    }

    document.querySelectorAll('.mod-shot, .feature-shot').forEach(btn => {
      btn.addEventListener('click', () => {
        const src = btn.getAttribute('data-zoom');
        if (src) {
          const cap = btn.getAttribute('data-cap');
          const innerImg = btn.querySelector('img');
          const alt = (innerImg && innerImg.alt) || cap || '系统界面大图';
          openLightbox(src, alt);
        }
      });
    });
    lb.addEventListener('click', e => {
      if (e.target === lb || e.target.classList.contains('lightbox-cap')) closeLightbox();
    });
    const lbClose = lb.querySelector('.lightbox-close');
    if (lbClose) lbClose.addEventListener('click', closeLightbox);

    document.addEventListener('keydown', e => {
      if (!lb.classList.contains('open')) return;
      if (e.key === 'Escape') { closeLightbox(); return; }
      if (e.key === 'Tab') {
        const focusable = getFocusable();
        if (focusable.length === 0) return;
        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault(); last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault(); first.focus();
        }
      }
    });

    // Preload images on hover/touch
    document.querySelectorAll('.mod-shot, .feature-shot').forEach(btn => {
      const src = btn.getAttribute('data-zoom');
      if (!src) return;
      btn.addEventListener('mouseenter', function pre() {
        if (!btn._pre) { btn._pre = new Image(); btn._pre.src = src; }
      }, { once: true });
      btn.addEventListener('touchstart', function pre() {
        if (!btn._pre) { btn._pre = new Image(); btn._pre.src = src; }
      }, { once: true, passive: true });
    });
  }

  /* ---- Card Image Skeleton (hide shimmer once image loads) ---- */
  document.querySelectorAll('.card-img img').forEach(img => {
    const wrap = img.closest('.card-img');
    if (!wrap) return;
    const markLoaded = () => wrap.classList.add('is-loaded');
    if (img.complete && img.naturalWidth > 0) {
      markLoaded();
    } else {
      img.addEventListener('load', markLoaded, { once: true });
      img.addEventListener('error', markLoaded, { once: true });
    }
  });

  /* ---- Back to Top ---- */
  const toTop = document.createElement('button');
  toTop.className = 'back-to-top';
  toTop.setAttribute('aria-label', '返回顶部');
  toTop.innerHTML = '<svg viewBox="0 0 256 256" aria-hidden="true"><path fill="currentColor" d="M216,168a8,8,0,0,1-11.31,0L128,91.31,51.31,168a8,8,0,0,1-11.32-11.32l84-84a8,8,0,0,1,11.32,0l84,84A8,8,0,0,1,216,168Z"/></svg>';
  document.body.appendChild(toTop);
  let topTicking = false;
  const onScrollTop = () => {
    toTop.classList.toggle('show', window.scrollY > 500);
    topTicking = false;
  };
  window.addEventListener('scroll', () => {
    if (!topTicking) { requestAnimationFrame(onScrollTop); topTicking = true; }
  }, { passive: true });
  onScrollTop();
  toTop.addEventListener('click', () => {
    if (prefersReducedMotion) {
      window.scrollTo(0, 0);
    } else {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  });

  /* ---- Comparison table: scroll shadow + hint fade ---- */
  document.querySelectorAll('.table-wrap').forEach(wrap => {
    if (wrap.scrollWidth > wrap.clientWidth + 4) {
      wrap.classList.add('table-wrap--scroll');
      const hint = document.createElement('p');
      hint.className = 'tbl-scroll-hint';
      hint.textContent = '← 左右滑动查看完整对比 →';
      wrap.insertAdjacentElement('afterend', hint);
      let hintVisible = true;
      wrap.addEventListener('scroll', () => {
        if (hintVisible && wrap.scrollLeft > 20) {
          hint.style.opacity = '0';
          hint.style.transition = 'opacity 0.3s';
          hintVisible = false;
        } else if (!hintVisible && wrap.scrollLeft <= 20) {
          hint.style.opacity = '';
          hintVisible = true;
        }
      }, { passive: true });
    }
  });

  /* ---- Form Real-time Validation ---- */
  const form = document.getElementById('inquiry-form');
  if (form) {
    const phoneInput = form.querySelector('#c-phone');
    const emailInput = form.querySelector('#c-email');

    if (phoneInput) {
      phoneInput.setAttribute('pattern', '^1[3-9]\\d{9}$');
      phoneInput.addEventListener('blur', function () {
        const val = this.value.trim();
        if (val && !/^1[3-9]\d{9}$/.test(val)) {
          this.closest('.field').classList.add('has-error');
          const err = this.closest('.field').querySelector('.field-error');
          if (err) err.textContent = '请输入有效的手机号码（11位）';
        } else {
          this.closest('.field').classList.remove('has-error');
        }
      });
    }

    if (emailInput) {
      emailInput.addEventListener('blur', function () {
        const val = this.value.trim();
        if (val && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val)) {
          this.closest('.field').classList.add('has-error');
          const err = this.closest('.field').querySelector('.field-error');
          if (err) err.textContent = '请输入有效的邮箱地址';
        } else {
          this.closest('.field').classList.remove('has-error');
        }
      });
    }

    // Clear error on input
    form.querySelectorAll('input, textarea').forEach(input => {
      input.addEventListener('input', function () {
        this.closest('.field')?.classList.remove('has-error');
      });
    });
  }

  /* ---- Footer Year ---- */
  const yearEl = document.getElementById('year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();

})();
