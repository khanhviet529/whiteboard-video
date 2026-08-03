"""Xuat 4 anh cung mot canh, khac domain -> kiem tra he ma mau co nhat quan.

Muc dich: xem 0,5 giay co biet video thuoc mang nao khong, va bon mau co du
tuong phan voi chu den + nen giay khong.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "src"))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

import brutal  # noqa: E402
import render as R  # noqa: E402
from style import H, W  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R.use_theme("brutalist")

SPEC = {
    "scene": "compare",
    "caption": "Cùng một layout, khác mảng thì khác màu nhấn.",
    "items": [
        {"label": "MONG ĐỢI", "value": "120.000"},
        {"label": "THỰC TẾ", "value": "100.000", "cross": True},
    ],
    "verdict": "SAI Ở ĐÂU?",
}

bg = brutal.background()
shots = []
for key in ("fe", "be", "database", "infra"):
    sp = dict(SPEC, domain=key)
    els = brutal.build(sp, 6.0)
    img = R.render_scene_frame(bg, els, 5.4)
    shots.append((brutal.DOMAINS[key]["label"],
                  img.convert("RGB").resize((W // 3, H // 3), Image.LANCZOS)))

TW, TH = W // 3, H // 3
LABEL = 34
sheet = Image.new("RGB", (TW * 4, TH + LABEL), "#DDDBD3")
d = ImageDraw.Draw(sheet)
f = ImageFont.load_default(20)
for i, (label, im) in enumerate(shots):
    sheet.paste(im, (i * TW, LABEL))
    d.text((i * TW + 10, 8), label, fill="#111", font=f)

out = os.path.join(ROOT, "build", "domain-sheet.png")
sheet.save(out)
print(out, sheet.size)
