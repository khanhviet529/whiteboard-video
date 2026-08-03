import os, re, urllib.request
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.dirname(os.path.abspath(__file__))
FDIR = os.path.join(OUT, "fonts")
os.makedirs(FDIR, exist_ok=True)

# Old UA makes Google Fonts serve TTF instead of woff2
UA = "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)"

CANDIDATES = [
    ("Patrick Hand", "400"),
    ("Playpen Sans", "700"),
    ("Shantell Sans", "700"),
    ("Fuzzy Bubbles", "700"),
    ("Baloo 2", "800"),
    ("Mansalva", "400"),
    ("Pangolin", "400"),
    ("Grape Nuts", "400"),
    ("JetBrains Mono", "400"),
]

# Hardest Vietnamese diacritics: stacked tone marks on modified vowels
TESTS = [
    "ĂẮẰẲẴẶ ÂẤẦẨẪẬ ÊẾỀỂỄỆ",
    "ÔỐỒỔỖỘ ƠỚỜỞỠỢ ƯỨỪỬỮỰ",
    "ăắằẳẵặ âấầẩẫậ êếềểễệ",
    "ôốồổỗộ ơớờởỡợ ưứừửữự",
    "Đđ ỲỴỶỸ ỳỵỷỹ ỈĨ ỉĩ ỌỎ ọỏ",
    "XOÁ TRƯỚC HAY SAU KHI GHI?",
    "Cái sai sống lâu hơn khe hở",
]

def fetch_ttf(family, weight):
    fam = family.replace(" ", "+")
    url = f"https://fonts.googleapis.com/css2?family={fam}:wght@{weight}&display=swap"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    css = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")
    urls = re.findall(r"url\((https://[^)]+\.ttf)\)", css)
    if not urls:
        return None, f"no ttf in css (len={len(css)})"
    path = os.path.join(FDIR, family.replace(" ", "") + ".ttf")
    if not os.path.exists(path):
        urllib.request.urlretrieve(urls[-1], path)
    return path, None

rows = []
for fam, wt in CANDIDATES:
    try:
        p, err = fetch_ttf(fam, wt)
        rows.append((fam, p, err))
        print(f"{fam:18s} -> {'OK ' + os.path.basename(p) if p else 'FAIL ' + err}")
    except Exception as e:
        rows.append((fam, None, str(e)))
        print(f"{fam:18s} -> ERROR {e}")

# Render a sheet per font so missing glyphs (tofu boxes) are visible
ok = [(f, p) for f, p, e in rows if p]
LH = 60
H = 40 + len(ok) * (30 + len(TESTS) * LH + 20)
img = Image.new("RGB", (1400, H), "#FAFAF5")
d = ImageDraw.Draw(img)
label_font = ImageFont.load_default(18)
y = 20
for fam, path in ok:
    d.text((20, y), f"=== {fam} ===", fill="#B00020", font=label_font)
    y += 30
    f = ImageFont.truetype(path, 34)
    for t in TESTS:
        d.text((40, y), t, fill="#222222", font=f)
        y += LH
    y += 20
out = os.path.join(OUT, "font-vietnamese-test.png")
img.save(out)
print("sheet:", out, img.size)
