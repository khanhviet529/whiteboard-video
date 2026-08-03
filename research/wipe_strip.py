"""Xuat dai anh cua rieng cu chuyen canh, de kiem tra truoc khi render full.

Render full mat ~12 phut nen phai soi cu quet bang anh tinh truoc.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "src"))

import yaml  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

import render as R  # noqa: E402
from style import H, W  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
doc = yaml.safe_load(open(os.path.join(ROOT, "screenplays", "double-charge.yaml"),
                          encoding="utf-8"))
R.use_theme(doc.get("theme", "phongtoi"))
THEME = R.THEME

DUR = 6.0
sp = doc["scenes"][0]
els = THEME.build(sp, DUR, doc)
bg = THEME.background()

# nua dau: dai rut di (vao canh). nua sau: bong toi quet vao (ra canh)
MOMENTS = [0.02, 0.06, 0.12, 0.90, 0.95, 0.99]
TW, TH, LAB = W // 4, H // 4, 30
sheet = Image.new("RGB", (TW * len(MOMENTS), TH + LAB), "#3A3A40")
d = ImageDraw.Draw(sheet)
f = ImageFont.load_default(15)
for i, frac in enumerate(MOMENTS):
    t = DUR * frac
    img = R.render_scene_frame(bg, els, t)
    sheet.paste(img.convert("RGB").resize((TW, TH), Image.LANCZOS), (i * TW, LAB))
    tag = "VAO" if frac < 0.5 else "RA"
    d.text((i * TW + 8, 7), f"{tag}  t={t:.2f}s", fill="#EEE", font=f)

out = os.path.join(ROOT, "build", "wipe-strip.png")
sheet.save(out)
print(out, sheet.size)
