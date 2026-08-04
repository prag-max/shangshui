# -*- coding: utf-8 -*-
"""Cool blue-white color grade for the two 16:9 scene photos.

Brand-aligned grading (no new palette, tuned to existing tokens):
  - highlight lift toward  #F0F9FF (--bg-soft)
  - shadow tint toward     #0C4A6E (--brand-deep)
  - ambient glow           #BAE6FD (--brand-glow)

Overwrites source JPGs in place (quality 88) — run _gen_app_previews.py
afterwards to rebuild the WebP previews.
"""
import os
from PIL import Image, ImageEnhance

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets", "images", "APP")

TARGETS = [
    "outdoor-on-site.jpg",
    "business-hall.jpg",
]

HIGHLIGHT = (240, 249, 255)   # #F0F9FF
SHADOW = (12, 74, 110)        # #0C4A6E
STRENGTH = 0.55               # 0 = identity, 1 = full tint


def _channel_curve(ch, lo, hi):
    """Piecewise-linear per-channel remap (lo at 0, hi at 255)."""
    return ch.point(lambda v: int(lo + (hi - lo) * (v / 255.0)))


def grade_cool(im, strength=STRENGTH):
    im = im.convert("RGB")
    # gentle contrast + saturation first (photographic base)
    im = ImageEnhance.Contrast(im).enhance(1.07)
    im = ImageEnhance.Color(im).enhance(1.04)

    r, g, b = im.split()
    # per-channel tone curves: warm channels pulled down, blue pushed up,
    # both at the shadow AND highlight end -> cool cast throughout
    r2 = _channel_curve(r, 0, 242)
    g2 = _channel_curve(g, 4, 249)
    b2 = _channel_curve(b, 16, 255)
    tinted = Image.merge("RGB", (r2, g2, b2))

    # shadow tint toward --brand-deep (blend bottom of the range)
    shadow_tint = Image.new("RGB", im.size, SHADOW)
    tinted = Image.blend(tinted, shadow_tint, 0.14)

    # highlight lift toward --bg-soft
    hl_tint = Image.new("RGB", im.size, HIGHLIGHT)
    tinted = Image.blend(tinted, hl_tint, 0.10)

    return Image.blend(im, tinted, strength)


for name in TARGETS:
    path = os.path.join(SRC, name)
    if not os.path.exists(path):
        print(f"!! MISSING {name}")
        continue
    with Image.open(path) as im:
        graded = grade_cool(im)
        graded.save(path, "JPEG", quality=88, optimize=True,
                    progressive=True)
    print(f"OK  {name}  graded {im.size[0]}x{im.size[1]}")
