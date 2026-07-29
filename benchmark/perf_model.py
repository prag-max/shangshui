import json

# ---- Resource sizes (bytes) ----
# Current (uncompressed, served as-is)
cur = {
    "html": 24768,
    "css":  28323,
    "js":   4795,
    "hero": 23216,   # avif, LCP element (browser prefers avif)
    "logo": 15401,   # same URL reused; counts once
}
# Optimized: minify + gzip(text). images already compressed (avif/webp) -> gzip ~= identity
opt = {
    "html": int(cur["html"]*0.30),        # gzip
    "css":  int(cur["css"]*0.82*0.22),    # minify -18% then gzip 22%
    "js":   int(cur["js"]*0.60*0.35),     # minify -40% then gzip 35%
    "hero": cur["hero"],                  # avif already optimal
    "logo": int(cur["logo"]*0.85),        # png gzip
}

# ---- Network profiles: (label, effective RTT ms incl TLS, downlink KB/s) ----
profiles = [
    ("Slow 3G",      400, 50),     # RTT 400ms, ~400kbps
    ("Fast 3G",      200, 200),    # RTT 200ms, ~1.6Mbps
    ("4G",           100, 1400),   # RTT 100ms, ~11Mbps
    ("Broadband",    30,  6000),   # RTT 30ms, ~50Mbps
]
SERVER = 25  # ms origin processing; edge ~10ms (folded into RTT-ish)

def tput(sz_b, kbps):  # seconds to transfer
    return sz_b / (kbps*1024)

def scenario(name, sizes, cache_hit, label):
    rows=[]
    print(f"\n### {label}  (cache={'HIT' if cache_hit else 'MISS'})")
    print(f"{'metric':10} | " + " | ".join(f"{p[0]:>10}" for p in profiles))
    # TTFB = RTT + server ; on cache hit, browser still needs HTML (navigation), reuse conn
    ttfb={p[0]: p[1]/1000 + SERVER/1000 for p in profiles}
    # FCP ~ after HTML + render-blocking CSS ready (H2 parallel after TTFB)
    fcp={}
    lcp={}
    for (pn,rtt,kbps) in profiles:
        s=rtt/1000+SERVER/1000
        # transfer times (parallel after TTFB on H2)
        th=tput(sizes["html"],kbps); tc=tput(sizes["css"],kbps)
        tj=tput(sizes["js"],kbps);  thx=tput(sizes["hero"],kbps); tl=tput(sizes["logo"],kbps)
        if cache_hit:
            # cache: only HTML revalidated (tiny); css/js/hero/logo from disk cache ~0
            fcp[pn]=s+0.02
            lcp[pn]=s+0.05+thx
            ttfb[pn]=s
        else:
            fcp[pn]=s+max(th,tc)            # HTML parsed + CSSOM ready (parallel)
            lcp[pn]=s+max(th,tc)+max(tj,thx,tl)  # paint after CSS + hero arrived
    print(f"{'TTFB(ms)':10} | " + " | ".join(f"{ttfb[p[0]]*1000:>10.0f}" for p in profiles))
    print(f"{'FCP(ms)':10} | " + " | ".join(f"{fcp[p[0]]*1000:>10.0f}" for p in profiles))
    print(f"{'LCP(ms)':10} | " + " | ".join(f"{lcp[p[0]]*1000:>10.0f}" for p in profiles))
    print(f"{'CLS':10} | " + " | ".join(f"{'0':>10}" for p in profiles))
    tot=sum(sizes.values())
    print(f"{'bytes':10} | " + " | ".join(f"{tot/1024:>9.1f}K" for p in profiles))

scenario("cur", cur, False, "BASELINE  first visit (no gzip, no cache)")
scenario("opt", opt, False, "OPTIMIZED first visit (minify+gzip, H2)")
scenario("opt", opt, True,  "OPTIMIZED repeat visit (cache HIT)")
