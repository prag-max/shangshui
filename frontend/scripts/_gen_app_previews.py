# -*- coding: utf-8 -*-
"""Generate optimized WebP previews for the APP (meter-reader) phone screenshots."""
import os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets", "images", "APP")
OUT = os.path.join(SRC, "preview")
os.makedirs(OUT, exist_ok=True)

# (source, output, target width) — phone screenshots 430, scene photos 960
MAPPING = [
    ("meter-reading-statistics.jpg", "meter-reading-statistics.webp", 430),
    ("charge-summary.jpg", "charge-summary.webp", 430),
    ("meter-data-entry.png", "meter-data-entry.webp", 430),
    ("wechat-pay.png", "wechat-pay.webp", 430),
    ("outdoor-on-site.jpg", "outdoor-on-site.webp", 960),
    ("business-hall.jpg", "business-hall.webp", 960),
    ("pocket-micro-hall.jpg", "pocket-micro-hall.webp", 960),
]

QUALITY = 80


def flatten_rgb(im):
    """Composite transparency onto white before converting to RGB (PNG alpha)."""
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGB", im.size, (255, 255, 255))
        bg.paste(im, mask=im.split()[-1])
        return bg
    return im.convert("RGB")


for src_name, out_name, width in MAPPING:
    src_path = os.path.join(SRC, src_name)
    out_path = os.path.join(OUT, out_name)
    if not os.path.exists(src_path):
        print(f"!! MISSING {src_name}")
        continue
    with Image.open(src_path) as im:
        im = flatten_rgb(im)
        w, h = im.size
        if w > width:
            nh = round(h * width / w)
            im = im.resize((width, nh), Image.LANCZOS)
        im.save(out_path, "WEBP", quality=QUALITY, method=6)
    size = os.path.getsize(out_path)
    print(f"OK  {out_name:40s} {im.size[0]}x{im.size[1]}  {size//1024} KB")
