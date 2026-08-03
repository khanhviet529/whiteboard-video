"""Tai va kiem tra font cho huong neo-brutalist.

Can: chu tieu de CUC DAM, hoi hep ngang (poster/condensed), va mot font than
kieu grotesque. Tat ca phai du dau tieng Viet.

Uu tien font do nguoi Viet thiet ke (Phudu, Vina Sans, Be Vietnam Pro) vi chac
chan phu het dau, ke ca cac to hop kho.
"""
import json
import os
import urllib.request

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FDIR = os.path.join(HERE, "fonts-brutal")
os.makedirs(FDIR, exist_ok=True)
UA = {"User-Agent": "whiteboard-video-tool"}
LICENSE_DIRS = ["ofl", "apache", "ufl"]

# (ten, slug, uu tien ten file - cang dam cang tot)
CANDIDATES = [
    ("Anton",         "anton",        ["Regular"]),
    ("Phudu",         "phudu",        ["[wght]", "Bold", "Regular"]),
    ("Vina Sans",     "vinasans",     ["Regular"]),
    ("Archivo Black", "archivoblack", ["Regular"]),
    ("Anybody",       "anybody",      ["[", "Black", "Bold"]),
    ("Big Shoulders", "bigshoulders", ["[", "Black", "Bold"]),
    ("Be Vietnam Pro", "bevietnampro", ["Black", "Bold", "SemiBold"]),
    ("Bungee",        "bungee",       ["Regular"]),
]


def gh_list(path):
    req = urllib.request.Request(
        f"https://api.github.com/repos/google/fonts/contents/{path}", headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def fetch(slug, prefer):
    for lic in LICENSE_DIRS:
        try:
            items = gh_list(f"{lic}/{slug}")
        except Exception:
            continue
        ttfs = [i for i in items if i["name"].lower().endswith(".ttf")
                and "italic" not in i["name"].lower()]
        if not ttfs:
            continue
        pick = None
        for p in prefer:
            for t in ttfs:
                if p in t["name"]:
                    pick = t
                    break
            if pick:
                break
        pick = pick or ttfs[0]
        dest = os.path.join(FDIR, pick["name"])
        if not os.path.exists(dest):
            urllib.request.urlretrieve(pick["download_url"], dest)
        return dest, f"{lic}/{slug}/{pick['name']}"
    return None, "khong tim thay"


# Dong 1-2: dau kho. Dong 3-4: cau thuc te se dung lam tieu de.
TESTS = [
    "ẮẶẤẬẾỆỐỘỚỢỨỰ ĐỲỴỶỸ",
    "ăắặâấậêếệôốộơớợưứự đ",
    "GHI TRƯỚC, XOÁ SAU",
    "KHÔNG AI BÁO LỖI",
]

results = []
for name, slug, prefer in CANDIDATES:
    try:
        p, info = fetch(slug, prefer)
        results.append((name, p))
        print(f"{name:16s} -> {info}")
    except Exception as e:
        results.append((name, None))
        print(f"{name:16s} -> LOI {e}")

ok = [(n, p) for n, p in results if p]
PER = 3
for si in range(0, len(ok), PER):
    group = ok[si:si + PER]
    LH, W = 74, 1500
    H = 30 + len(group) * (46 + len(TESTS) * LH + 26)
    img = Image.new("RGB", (W, H), "#EFEDE4")
    d = ImageDraw.Draw(img)
    lab = ImageFont.load_default(22)
    y = 20
    for name, path in group:
        d.text((20, y), f"--- {name} ---", fill="#FF1744", font=lab)
        y += 46
        try:
            f = ImageFont.truetype(path, 46)
            for want in ("Black", "ExtraBold", "Bold"):
                try:
                    f.set_variation_by_name(want)
                    break
                except Exception:
                    continue
        except Exception as e:
            d.text((40, y), f"loi load: {e}", fill="#000", font=lab)
            y += len(TESTS) * LH + 26
            continue
        for t in TESTS:
            d.text((40, y), t, fill="#111111", font=f)
            y += LH
        y += 26
    out = os.path.join(HERE, f"font-brutal-{si // PER + 1}.png")
    img.save(out)
    print("sheet:", out, img.size)
