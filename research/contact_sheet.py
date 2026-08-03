"""Ghep tat ca stills thanh mot bang tong de soi bo cuc toan cuc."""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "build", "stills")
files = sorted(f for f in os.listdir(SRC) if f.endswith(".png"))
if not files:
    sys.exit("chua co stills")

COLS = 6
TW, TH = 250, 444          # kich thuoc moi o
LABEL = 26
rows = (len(files) + COLS - 1) // COLS
sheet = Image.new("RGB", (COLS * TW, rows * (TH + LABEL)), "#E8E8E0")
d = ImageDraw.Draw(sheet)
lf = ImageFont.load_default(17)

for i, fn in enumerate(files):
    im = Image.open(os.path.join(SRC, fn)).resize((TW - 6, TH - 6), Image.LANCZOS)
    cx = (i % COLS) * TW
    cy = (i // COLS) * (TH + LABEL)
    sheet.paste(im, (cx + 3, cy + LABEL))
    d.text((cx + 6, cy + 5), fn.replace("scene-", "").replace(".png", ""),
           fill="#111", font=lf)

out = os.path.join(ROOT, "build", "contact-sheet.png")
sheet.save(out)
print(out, sheet.size, f"({len(files)} canh)")
