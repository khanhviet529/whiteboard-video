"""Xuat N frame LIEN TIEP cua mot canh - de bat cu "khung" trong chuyen dong.

    python research/frame_strip.py cache-stale.yaml 11 0.7 14
    #                              screenplay      canh  t_bat_dau  so_frame

Khac `sim_strip.py`: file kia lay 6 moc RAI DEU khap canh nen chi kiem tra duoc
noi dung. Muon danh gia do MUOT thi phai xem cac frame ke nhau, vi cu khung chi
keo dai 2-3 frame - rai deu la khong bao gio thay.

Cot in kem do mo trung binh cua dai chu: day so tang deu thi muot, tang nhay bac
roi dung yen thi co cu khung.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "src"))

import numpy as np  # noqa: E402
import yaml  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

import render as R  # noqa: E402
from style import FPS, H, W  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCREEN = sys.argv[1] if len(sys.argv) > 1 else "cache-stale.yaml"
SCENE = int(sys.argv[2]) if len(sys.argv) > 2 else 1
T0 = float(sys.argv[3]) if len(sys.argv) > 3 else 0.6
N = int(sys.argv[4]) if len(sys.argv) > 4 else 12
BAND = (int(sys.argv[5]) if len(sys.argv) > 5 else 200,
        int(sys.argv[6]) if len(sys.argv) > 6 else 460)

doc = yaml.safe_load(open(os.path.join(ROOT, "screenplays", SCREEN),
                          encoding="utf-8"))
R.use_theme(doc.get("theme", "bench"))
THEME = R.THEME

sp = doc["scenes"][SCENE - 1]
DUR = max(4.0, float(sp.get("min_duration", 0)) or 8.0)
els = THEME.build(sp, DUR, doc)
bg = THEME.background()

TW, TH, LAB = W // 5, H // 5, 34
sheet = Image.new("RGB", (TW * N, TH + LAB), "#2A2A30")
d = ImageDraw.Draw(sheet)
f = ImageFont.load_default(13)
prev = None
for i in range(N):
    t = T0 + i / FPS
    img = R.render_scene_frame(bg, els, t)
    a = np.array(img.convert("L"))[BAND[0] * 2:BAND[1] * 2, :]
    lum = a.mean()
    delta = "" if prev is None else f"  d={lum - prev:+.2f}"
    prev = lum
    sheet.paste(img.convert("RGB").resize((TW, TH), Image.LANCZOS), (i * TW, LAB))
    d.text((i * TW + 5, 4), f"f{i} t={t:.2f}", fill="#EEE", font=f)
    d.text((i * TW + 5, 19), f"L={lum:.2f}{delta}", fill="#9CF", font=f)
    print(f"  f{i:2d} t={t:5.2f}s  sang dai chu = {lum:7.3f}{delta}")

out = os.path.join(ROOT, "build", f"frames-s{SCENE:02d}.png")
sheet.save(out)
print(out, sheet.size)
