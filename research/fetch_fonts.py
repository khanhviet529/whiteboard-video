"""Tai TTF tu repo google/fonts va render bang thu dau tieng Viet.

Google Fonts CSS2 API chi tra woff2 (PIL khong doc duoc), nen lay TTF goc
tu GitHub. Dung API contents de liet ke file thay vi doan ten.
"""
import json, os, urllib.request
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FDIR = os.path.join(HERE, "fonts")
os.makedirs(FDIR, exist_ok=True)

# (ten hien thi, slug thu muc trong repo, uu tien chon file)
CANDIDATES = [
    ("Playpen Sans",   "playpensans",   ["[wght]", "Bold", "Regular"]),
    ("Shantell Sans",  "shantellsans",  ["[", "Bold", "Regular"]),
    ("Patrick Hand",   "patrickhand",   ["Regular"]),
    ("Baloo 2",        "baloo2",        ["[wght]", "Regular"]),
    ("Fuzzy Bubbles",  "fuzzybubbles",  ["Bold", "Regular"]),
    ("Mansalva",       "mansalva",      ["Regular"]),
    ("Pangolin",       "pangolin",      ["Regular"]),
    ("Grape Nuts",     "grapenuts",     ["Regular"]),
    ("JetBrains Mono", "jetbrainsmono", ["[wght]", "Regular"]),
]

LICENSE_DIRS = ["ofl", "apache", "ufl"]
UA = {"User-Agent": "whiteboard-video-tool"}


def gh_list(path):
    url = f"https://api.github.com/repos/google/fonts/contents/{path}"
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def fetch(display, slug, prefer):
    for lic in LICENSE_DIRS:
        try:
            items = gh_list(f"{lic}/{slug}")
        except Exception:
            continue
        ttfs = [i for i in items if i["name"].lower().endswith(".ttf")]
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


TESTS = [
    "ĂẮẰẲẴẶ ÂẤẦẨẪẬ ÊẾỀỂỄỆ",
    "ÔỐỒỔỖỘ ƠỚỜỞỠỢ ƯỨỪỬỮỰ",
    "ăắằẳẵặ âấầẩẫậ ôốồổỗộ",
    "ơớờởỡợ ưứừửữự Đđ ỳỵỷỹ",
    "XOÁ TRƯỚC HAY SAU KHI GHI?",
    "Cái sai sống lâu hơn khe hở",
]

results = []
for display, slug, prefer in CANDIDATES:
    try:
        path, info = fetch(display, slug, prefer)
        results.append((display, path, info))
        print(f"{display:16s} -> {info}")
    except Exception as e:
        results.append((display, None, str(e)))
        print(f"{display:16s} -> LOI {e}")

# Chia thanh nhieu sheet nho de chu khong bi thu nho khi xem
ok = [(d, p) for d, p, _ in results if p]
PER_SHEET = 3
sheets = [ok[i:i + PER_SHEET] for i in range(0, len(ok), PER_SHEET)]

for si, group in enumerate(sheets, 1):
    LH, W = 62, 1500
    H = 30 + len(group) * (44 + len(TESTS) * LH + 24)
    img = Image.new("RGB", (W, H), "#FAFAF5")
    d = ImageDraw.Draw(img)
    lab = ImageFont.load_default(22)
    y = 20
    for display, path in group:
        d.text((20, y), f"--- {display} ---", fill="#D32F2F", font=lab)
        y += 44
        try:
            f = ImageFont.truetype(path, 38)
            try:
                f.set_variation_by_name("Bold")
            except Exception:
                pass
        except Exception as e:
            d.text((40, y), f"khong load duoc: {e}", fill="#000", font=lab)
            y += len(TESTS) * LH + 24
            continue
        for t in TESTS:
            d.text((40, y), t, fill="#222222", font=f)
            y += LH
        y += 24
    out = os.path.join(HERE, f"font-test-{si}.png")
    img.save(out)
    print("sheet:", out, img.size)
