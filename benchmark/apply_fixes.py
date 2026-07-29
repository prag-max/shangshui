import re, glob, os

# ---------- 1) Minify CSS (safe) ----------
css_path = "assets/css/style.css"
css = open(css_path, encoding="utf-8").read()
before = len(css.encode("utf-8"))
css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)          # strip comments
css = re.sub(r'[ \t]+', ' ', css)                         # collapse spaces/tabs
css = re.sub(r'\s*([{}:;,>])\s*', r'\1', css)            # strip space around delimiters
css = re.sub(r';}', '}', css)
css = css.strip()
bal = css.count('{') == css.count('}')
assert bal, "CSS brace imbalance after minify!"
open(css_path, "w", encoding="utf-8").write(css)
after = len(css.encode("utf-8"))
print(f"[CSS] minified {before} -> {after} bytes ({(1-after/before)*100:.0f}% smaller), brace_balance={bal}")

# ---------- 2) Defer Baidu push.js to window load (all pages) ----------
old = re.compile(
    r"<script>\s*\(function\(\)\{var bp=document\.createElement\(.script.\);bp\.src=.//push\.zhanzhang\.baidu\.com/push\.js.;.*?\}\)\(\);\s*</script>",
    re.S)
new = ('  <script>\n'
       '    window.addEventListener(\'load\', function () {\n'
       "      var bp = document.createElement('script');\n"
       "      bp.src = 'https://push.zhanzhang.baidu.com/push.js';\n"
       "      bp.async = true;\n"
       "      document.body.appendChild(bp);\n"
       "    });\n"
       '  </script>')
n_pages = 0
for f in glob.glob("*.html"):
    html = open(f, encoding="utf-8").read()
    if 'push.zhanzhang.baidu.com' not in html:
        continue
    html2, k = old.subn(new, html)
    if k:
        open(f, "w", encoding="utf-8").write(html2)
        n_pages += 1
        print(f"[Baidu] deferred in {f}")
print(f"[Baidu] total pages updated: {n_pages}")

# ---------- 3) Lazy-load below-fold logo images ----------
lazy_added = 0
for f in glob.glob("*.html"):
    html = open(f, encoding="utf-8").read()
    if 'class="logo-img"' not in html:
        continue
    def addlazy(m):
        global lazy_added
        tag = m.group(0)
        if 'loading=' in tag:
            return tag
        lazy_added += 1
        return tag.replace('class="logo-img"', 'class="logo-img" loading="lazy"', 1)
    html2 = re.sub(r'<img[^>]*class="logo-img"[^>]*>', addlazy, html)
    if html2 != html:
        open(f, "w", encoding="utf-8").write(html2)
print(f"[lazy] logo imgs given loading=lazy: {lazy_added}")
