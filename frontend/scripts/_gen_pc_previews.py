# -*- coding: utf-8 -*-
"""Generate optimized WebP previews for the architecture diagram PC module.

Sources: assets/images/PC/*.jpg|png (full-size screenshots, ~2363px wide)
Output:  assets/images/PC/preview/*.webp (width 820, quality 80)
"""
import os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets", "images", "PC")
OUT = os.path.join(SRC, "preview")
os.makedirs(OUT, exist_ok=True)

MAPPING = [
    ("user-mgmt.jpg", "user-mgmt.webp"),
    ("meter-mgmt.jpg", "meter-mgmt.webp"),
    ("billing-mgmt.jpg", "billing-mgmt.webp"),
    ("charging-mgmt.png", "charging-mgmt.webp"),
    ("accounting-treatment.jpg", "accounting-treatment.webp"),
    ("invoice-mgmt.jpg", "invoice-mgmt.webp"),
    ("meter-service.jpg", "meter-service.webp"),
    ("report-center.jpg", "report-center.webp"),
    ("business-parameters.jpg", "business-parameters.webp"),
]

WIDTH = 820
QUALITY = 80

for src_name, out_name in MAPPING:
    src_path = os.path.join(SRC, src_name)
    out_path = os.path.join(OUT, out_name)
    if not os.path.exists(src_path):
        print(f"!! MISSING {src_name}")
        continue
    with Image.open(src_path) as im:
        im = im.convert("RGB")
        w, h = im.size
        if w > WIDTH:
            nh = round(h * WIDTH / w)
            im = im.resize((WIDTH, nh), Image.LANCZOS)
        im.save(out_path, "WEBP", quality=QUALITY, method=6)
    size = os.path.getsize(out_path)
    print(f"OK  {out_name:34s} {size//1024} KB")
