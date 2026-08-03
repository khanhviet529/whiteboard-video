"""Dung 3 huong art direction moi, render cung mot noi dung de so bang mat.

Muc dich: chot huong TRUOC khi viet lai tang "nhin" cua theme. Ba huong nay
chua phai theme hoan chinh - chi la ban dung de chon.

Bon than phien cua nguoi dung, va cach tung huong xu ly:
  mau chua dep       -> bang mau co nhieu tang be mat, mau nhan giam do bao hoa
  nhin trong         -> nhieu hat, ke hairline, nhan mono nho, so thu tu, gach moc
  chu va bo cuc      -> can le trai lech truc, tracking am, thang co chu 5:1
  chuyen dong cung   -> khong the hien o anh tinh; ghi ke hoach easing rieng
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "src"))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FDIR = os.path.join(ROOT, "assets", "fonts")
W, H = 1080, 1920
SS = 2


def s(v):
    return int(round(v * SS))


_fc = {}


def F(name, size, wght=None):
    key = (name, size, wght)
    if key in _fc:
        return _fc[key]
    f = ImageFont.truetype(os.path.join(FDIR, name), s(size))
    if wght:
        try:
            f.set_variation_by_axes([wght])
        except Exception:
            pass
    _fc[key] = f
    return f


BLACK9 = "BeVietnamPro-Black.ttf"
SEMI = "BeVietnamPro-SemiBold.ttf"
MED = "BeVietnamPro-Medium.ttf"
MONO = "JetBrainsMono[wght].ttf"

_m = ImageDraw.Draw(Image.new("L", (8, 8)))


def tw(txt, f):
    b = _m.textbbox((0, 0), txt, font=f, anchor="lt")
    return (b[2] - b[0]) / SS, b[1] / SS, (b[3] - b[1]) / SS


def tracked(d, xy, txt, f, fill, track=0.0, anchor_left=True):
    """Ve chu co giãn khoang cach (tracking). PIL khong ho tro san."""
    x, y = xy
    if not anchor_left:
        total = sum(tw(c, f)[0] + track for c in txt) - track
        x -= total / 2
    for c in txt:
        d.text((s(x), s(y)), c, font=f, fill=fill)
        x += tw(c, f)[0] + track


def grain(img, amount=7, seed=3):
    """Hat nhieu mo. Day la thu chua benh 'nhin trong' hieu qua nhat va re nhat."""
    rng = np.random.default_rng(seed)
    n = rng.normal(0, amount, (img.height, img.width, 1)).astype(np.int16)
    a = np.array(img.convert("RGB")).astype(np.int16) + n
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")


def glow(img, box, color, radius=90, strength=115):
    """Vệt sáng toả quanh phần tử tieu diem. Chi dung cho huong nen toi."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).rectangle([s(box[0]), s(box[1]), s(box[2]), s(box[3])],
                                    fill=color + (strength,))
    layer = layer.filter(ImageFilter.GaussianBlur(s(radius)))
    img.alpha_composite(layer)


def hairlines(d, color, y_from, y_to, step=54, x0=0, x1=W):
    for y in range(y_from, y_to, step):
        d.line([s(x0), s(y), s(x1), s(y)], fill=color, width=max(1, s(0.5)))


# ============================================================ HUONG A: PHONG TOI
def dir_a(headline, label_a, val_a, label_b, val_b, verdict, caption, accent):
    """Nen gan den, nhieu tang be mat, vet sang quanh diem nhan. Sang, dien anh."""
    BG, SURF, EDGE = (2, 6, 23), (14, 18, 35), (51, 65, 85)
    FG, MUTED = (248, 250, 252), (148, 163, 184)
    ALERT = (239, 68, 68)
    img = Image.new("RGBA", (s(W), s(H)), BG + (255,))
    d = ImageDraw.Draw(img)
    hairlines(d, (255, 255, 255, 8), 200, 1600, 60, 56, W - 56)

    # badge: nhan mono nho, tracking rong, co vach mau
    d.rectangle([s(56), s(150), s(62), s(196)], fill=accent + (255,))
    tracked(d, (80, 156), "BACKEND", F(MONO, 26, 600), accent + (255,), track=4)
    tracked(d, (80, 196), "SỰ CỐ #04", F(MONO, 22, 400), MUTED + (255,), track=3)

    # tieu de type-as-hero, can le trai, tracking am
    f = F(BLACK9, 104)
    y = 300
    for line in headline:
        ox, oy, th = tw(line, f)
        tracked(d, (52, y - oy), line, f, FG + (255,), track=-2.5)
        y += th + 22

    # hai the: the duoi la diem nhan -> co vet sang + vien mau
    y0 = 700
    for i, (lab, val) in enumerate(((label_a, val_a), (label_b, val_b))):
        by = y0 + i * 250
        box = (56, by, W - 56, by + 200)
        focus = (i == 1)
        if focus:
            glow(img, box, ALERT, 100, 90)
        d = ImageDraw.Draw(img)
        d.rectangle([s(box[0]), s(box[1]), s(box[2]), s(box[3])],
                    fill=SURF + (255,),
                    outline=(ALERT if focus else EDGE) + (255,), width=s(2))
        tracked(d, (88, by + 30), lab, F(MONO, 24, 500),
                (ALERT if focus else MUTED) + (255,), track=4)
        fv = F(BLACK9, 96)
        ox, oy, th = tw(val, fv)
        tracked(d, (84, by + 108 - oy), val, fv,
                (FG if focus else MUTED) + (255,), track=-2)
        if focus:
            fx = F(MONO, 30, 600)
            tracked(d, (W - 240, by + 112), "×2", fx, ALERT + (255,), track=0)

    # cau ket: gach hairline + chu
    d.line([s(56), s(1215), s(W - 56), s(1215)], fill=EDGE + (255,), width=s(2))
    fvd = F(BLACK9, 70)
    ox, oy, th = tw(verdict, fvd)
    tracked(d, (52, 1250 - oy), verdict, fvd, ALERT + (255,), track=-2)

    # phu de: khong phai dai den dac, ma la chu tren nen toi + vach mau
    d.rectangle([s(56), s(1420), s(60), s(1560)], fill=accent + (255,))
    fc = F(MED, 34)
    yy = 1424
    for ln in caption:
        ox, oy, th = tw(ln, fc)
        d.text((s(84), s(yy - oy)), ln, font=fc, fill=MUTED + (255,))
        yy += th + 14
    return grain(img, 6, 11)


# ============================================================ HUONG B: TAP CHI
def dir_b(headline, label_a, val_a, label_b, val_b, verdict, caption, accent):
    """Gan trang, chu la nhan vat chinh, ke hairline, so thu tu. Tinh te, bao chi."""
    BG, INK, MUTED, RULE = (250, 250, 249), (9, 9, 11), (113, 113, 122), (212, 212, 216)
    ALERT = (220, 38, 38)
    img = Image.new("RGBA", (s(W), s(H)), BG + (255,))
    d = ImageDraw.Draw(img)

    # dau trang kieu bao: nhan trai, so phai, gach ngang
    tracked(d, (56, 150), "BACKEND", F(MONO, 24, 600), INK + (255,), track=5)
    f_no = F(MONO, 24, 400)
    no = "04 / 12"
    d.text((s(W - 56 - tw(no, f_no)[0]), s(150)), no, font=f_no, fill=MUTED + (255,))
    d.line([s(56), s(196), s(W - 56), s(196)], fill=INK + (255,), width=s(3))

    # tieu de cuc lon, tracking am manh, can le trai
    f = F(BLACK9, 112)
    y = 262
    for line in headline:
        ox, oy, th = tw(line, f)
        tracked(d, (50, y - oy), line, f, INK + (255,), track=-3.5)
        y += th + 8

    # hai muc kieu bang bao: so + nhan + gia tri, phan cach bang hairline
    y0 = 700
    for i, (lab, val) in enumerate(((label_a, val_a), (label_b, val_b))):
        by = y0 + i * 210
        focus = (i == 1)
        d.line([s(56), s(by), s(W - 56), s(by)], fill=RULE + (255,), width=s(2))
        tracked(d, (56, by + 26), f"0{i+1}", F(MONO, 26, 600), MUTED + (255,), track=3)
        tracked(d, (150, by + 26), lab, F(MONO, 26, 500),
                (ALERT if focus else MUTED) + (255,), track=4)
        fv = F(BLACK9, 104)
        ox, oy, th = tw(val, fv)
        tracked(d, (146, by + 80 - oy), val, fv,
                (ALERT if focus else INK) + (255,), track=-2.5)
        if focus:
            # thanh mau danh dau muc trong tam
            d.rectangle([s(56), s(by + 74), s(64), s(by + 74 + th)],
                        fill=ALERT + (255,))
    d.line([s(56), s(y0 + 420)], fill=RULE + (255,), width=s(2))
    d.line([s(56), s(y0 + 420), s(W - 56), s(y0 + 420)], fill=RULE + (255,),
           width=s(2))

    # cau ket in dam, kem gach chan mau
    fvd = F(BLACK9, 82)
    ox, oy, th = tw(verdict, fvd)
    tracked(d, (50, 1230 - oy), verdict, fvd, INK + (255,), track=-3)
    d.rectangle([s(56), s(1230 + th + 14), s(56 + min(560, tw(verdict, fvd)[0])),
                 s(1230 + th + 26)], fill=accent + (255,))

    # phu de kieu chu thich anh bao
    d.line([s(56), s(1420), s(300), s(1420)], fill=INK + (255,), width=s(2))
    fc = F(MED, 34)
    yy = 1444
    for ln in caption:
        ox, oy, th = tw(ln, fc)
        d.text((s(56), s(yy - oy)), ln, font=fc, fill=(63, 63, 70, 255))
        yy += th + 14
    return grain(img, 4, 5)


# ======================================================= HUONG C: TUYEN BO NGON
def dir_c(headline, label_a, val_a, label_b, val_b, verdict, caption, accent):
    """Gan den tuyet doi, MOT mau nhan duy nhat, chu chiem het khung. Manh, gon."""
    BG, INK, MUTED = (10, 10, 11), (250, 250, 250), (100, 100, 106)
    img = Image.new("RGBA", (s(W), s(H)), BG + (255,))
    d = ImageDraw.Draw(img)

    # khoi mau nhan chay tran le trai - dau hieu nhan dien
    d.rectangle([0, s(150), s(18), s(1560)], fill=accent + (255,))
    tracked(d, (56, 152), "BACKEND", F(MONO, 26, 600), accent + (255,), track=5)

    # tieu de tran gan het khung, tracking am rat manh
    f = F(BLACK9, 124)
    y = 250
    for line in headline:
        ox, oy, th = tw(line, f)
        tracked(d, (50, y - oy), line, f, INK + (255,), track=-4.5)
        y += th + 4

    # so lieu doi lap: chu khong lo, khong khung, phan cap bang co chu
    y0 = 720
    tracked(d, (56, y0), label_a, F(MONO, 26, 500), MUTED + (255,), track=4)
    fa = F(BLACK9, 92)
    ox, oy, th = tw(val_a, fa)
    tracked(d, (52, y0 + 46 - oy), val_a, fa, MUTED + (255,), track=-2)

    tracked(d, (56, y0 + 210), label_b, F(MONO, 26, 600), accent + (255,), track=4)
    fb = F(BLACK9, 168)
    ox, oy, th = tw(val_b, fb)
    tracked(d, (48, y0 + 256 - oy), val_b, fb, accent + (255,), track=-4)

    # cau ket: khoi mau nhan, chu den -> dao mau tao diem nhan
    fvd = F(BLACK9, 66)
    ox, oy, th = tw(verdict, fvd)
    bw = tw(verdict, fvd)[0] + 64
    d.rectangle([s(56), s(1216), s(56 + bw), s(1216 + th + 44)],
                fill=accent + (255,))
    tracked(d, (86, 1238 - oy), verdict, fvd, (10, 10, 11, 255), track=-2)

    fc = F(MED, 34)
    yy = 1430
    for ln in caption:
        ox, oy, th = tw(ln, fc)
        d.text((s(56), s(yy - oy)), ln, font=fc, fill=MUTED + (255,))
        yy += th + 14
    return grain(img, 5, 21)


CONTENT = dict(
    headline=["KHÁCH BẤM", "MỘT LẦN."],
    label_a="KHÁCH BẤM", val_a="1 LẦN",
    label_b="HỆ THỐNG TRỪ", val_b="2 LẦN",
    verdict="KHÔNG AI BÁO LỖI",
    caption=["Khách bấm thanh toán một lần.", "Hệ thống trừ tiền hai lần."],
)
ACCENT = (52, 211, 153)   # BACKEND

DIRS = [("A · PHÒNG TỐI", dir_a), ("B · TẠP CHÍ", dir_b),
        ("C · TUYÊN BỐ NGÔN", dir_c)]

TWv, THv, LAB = W // 3, H // 3, 34
sheet = Image.new("RGB", (TWv * 3, THv + LAB), "#C9C7C0")
sd = ImageDraw.Draw(sheet)
lf = ImageFont.load_default(20)
for i, (name, fn) in enumerate(DIRS):
    img = fn(accent=ACCENT, **CONTENT)
    img.convert("RGB").resize((TWv, THv), Image.LANCZOS)
    sheet.paste(img.convert("RGB").resize((TWv, THv), Image.LANCZOS),
                (i * TWv, LAB))
    sd.text((i * TWv + 10, 9), name, fill="#111", font=lf)
    img.convert("RGB").save(os.path.join(ROOT, "build",
                                         f"dir-{name.split(' ')[0]}.png"))
out = os.path.join(ROOT, "build", "direction-sheet.png")
sheet.save(out)
print(out, sheet.size)
