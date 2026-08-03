"""Xuat mot dai anh cua RIENG canh `race` theo nhieu moc thoi gian.

Canh mo phong khong the danh gia bang mot anh tinh - phai xem dau doc quet toi
dau va cac khoi sang len theo thu tu nao.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "src"))

import yaml  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

import brutal  # noqa: E402
import render as R  # noqa: E402
from style import H, W  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R.use_theme("brutalist")

doc = yaml.safe_load(open(os.path.join(ROOT, "screenplays", "double-charge.yaml"),
                          encoding="utf-8"))
sp = next(s for s in doc["scenes"] if s["scene"] == "race")
DUR = 11.0
els = brutal.build(sp, DUR, doc)
bg = brutal.background()

MOMENTS = [0.18, 0.36, 0.52, 0.68, 0.84, 0.97]
TW, TH, LAB = W // 4, H // 4, 30
sheet = Image.new("RGB", (TW * len(MOMENTS), TH + LAB), "#DDDBD3")
d = ImageDraw.Draw(sheet)
f = ImageFont.load_default(16)
for i, frac in enumerate(MOMENTS):
    t = DUR * frac
    img = R.render_scene_frame(bg, els, t)
    sheet.paste(img.convert("RGB").resize((TW, TH), Image.LANCZOS), (i * TW, LAB))
    d.text((i * TW + 8, 7), f"t = {t:.1f}s", fill="#111", font=f)

out = os.path.join(ROOT, "build", "race-strip.png")
sheet.save(out)
print(out, sheet.size)
