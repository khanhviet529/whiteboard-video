"""Xuat dai anh cua RIENG mot canh mo phong theo nhieu moc thoi gian.

    python research/sim_strip.py topology
    python research/sim_strip.py race

Canh mo phong khong danh gia duoc bang mot anh tinh - phai xem vat the di toi
dau va node nao sang len theo thu tu nao.
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
KIND = sys.argv[1] if len(sys.argv) > 1 else "topology"
SCREEN = sys.argv[2] if len(sys.argv) > 2 else "double-charge.yaml"

doc = yaml.safe_load(open(os.path.join(ROOT, "screenplays", SCREEN),
                          encoding="utf-8"))
R.use_theme(doc.get("theme", "phongtoi"))
THEME = R.THEME

sp = next((x for x in doc["scenes"] if x["scene"] == KIND), None)
if sp is None:
    sys.exit(f"screenplay khong co canh {KIND!r}")
DUR = float(sp.get("min_duration", 11))
els = THEME.build(sp, DUR, doc)
bg = THEME.background()

MOMENTS = [0.14, 0.30, 0.46, 0.62, 0.76, 0.92]
TW, TH, LAB = W // 4, H // 4, 30
sheet = Image.new("RGB", (TW * len(MOMENTS), TH + LAB), "#3A3A40")
d = ImageDraw.Draw(sheet)
f = ImageFont.load_default(16)
for i, frac in enumerate(MOMENTS):
    t = DUR * frac
    img = R.render_scene_frame(bg, els, t)
    sheet.paste(img.convert("RGB").resize((TW, TH), Image.LANCZOS), (i * TW, LAB))
    d.text((i * TW + 8, 7), f"t = {t:.1f}s", fill="#EEE", font=f)

out = os.path.join(ROOT, "build", f"{KIND}-strip.png")
sheet.save(out)
print(out, sheet.size)
