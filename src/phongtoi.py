"""Theme PHONG TOI - nen xanh dem nhieu tang, luoi hairline, vet sang tieu diem.

Thay the theme brutalist. Bon dieu phai chua, va cach chua:

  mau chua dep      -> BA tang be mat (nen / mat phang / vien) thay vi mot mau
                       phang. Mau nhan giam bao hoa. Do CHI dung cho loi.
  nhin trong        -> luoi hairline chay toan khung + hat nhieu + nhan mono co
                       tracking + so thu tu + vet sang quanh phan tu tieu diem.
  chu va bo cuc     -> can le TRAI lech truc, tracking am, thang co chu 5:1.
                       Bo het kieu "can giua xep chong" cua theme cu.
  chuyen dong cung  -> easing expo.out 500-700ms, he lo bang mask truot len,
                       chuyen canh bang dai mau quet qua thay cho cat tho.
"""
import numpy as np
from PIL import Image, ImageDraw

import sketch as sk
import typo
from style import H, W, clamp, font, s
from timing import B
from typo import (expo_out, glow, headline, mono, ttext, track_w,  # noqa: F401
                  wrap_track)

# ---------------------------------------------------- chuyen canh: dai mau quet
FADE = 0.0            # khong mo dan ve nen; theme nay tu ve dai quet
WIPE_OUT = 0.34       # thoi luong dai mau phu kin cuoi canh
WIPE_IN = 0.28        # thoi luong dai mau rut di dau canh

# ------------------------------------------------------------------- bang mau
BG = (2, 6, 23)          # nen xanh dem
SURF = (14, 18, 35)      # mat phang noi dung
SURF_HI = (23, 29, 51)   # mat phang nang len
EDGE = (51, 65, 85)      # vien
FG = (248, 250, 252)     # chu chinh
MUTED = (148, 163, 184)  # chu phu
DIM = (86, 100, 124)     # chu mo nhat
ALERT = (239, 68, 68)    # CHI dung cho cai sai
GRID = (255, 255, 255)   # luoi hairline (khong dung truc tiep nua)
GRID_LINE = (20, 25, 44)  # mau luoi DA TRON san voi nen - xem background()

DOMAINS = {
    "fe":       {"label": "FRONTEND", "color": (251, 191, 36)},
    "be":       {"label": "BACKEND",  "color": (52, 211, 153)},
    "database": {"label": "DATABASE", "color": (96, 165, 250)},
    "infra":    {"label": "HẠ TẦNG",  "color": (167, 139, 250)},
}
DEFAULT_DOMAIN = "be"

# --------------------------------------------------------------------- bo cuc
MARGIN = 56
CX = W // 2
CONTENT_W = W - MARGIN * 2
BAND_TOP = 300
BAND_BOTTOM = 1180
CAPTION_TOP = 1200   # dat gan noi dung; duoi ~1600 la vung TikTok phu UI
RAIL_W = 6           # vach mau canh nhan
TEXT_X = MARGIN + 30                  # moc le trai cua chu (sau vach mau)
TEXT_W = W - TEXT_X - MARGIN           # be rong thuc te con lai cho chu
# Luu y: phai do be rong theo TEXT_W chu khong phai CONTENT_W. Chu thut vao
# thêm 30px so voi le, nen dung CONTENT_W la tran qua le phai dung 30px.


def domain(sp, doc_domain=None):
    key = (sp.get("domain") or doc_domain or DEFAULT_DOMAIN).lower()
    return DOMAINS.get(key, DOMAINS[DEFAULT_DOMAIN])


# ------------------------------------------------------------------ nen + hat
_bg = None


def background():
    """Nen + luoi hairline + hat nhieu. Ve MOT lan roi cache.

    Hat nhieu la thu chua benh "nhin trong" hieu qua nhat: nen phang tuyet doi
    trong re, con hat nhieu lam no co chat lieu. Phai nuong vao nen chu khong
    ve lai moi frame, khong thi cham va hat se nhay lung tung.
    """
    global _bg
    if _bg is not None:
        return _bg
    img = Image.new("RGBA", (s(W), s(H)), BG + (255,))
    # KHONG dua vao alpha: `Draw(im, "RGBA")` chi tron khi anh la RGB, con voi
    # anh RGBA thi PIL ghi thang mau. Truoc do duong ke mo hoa ra sang 115/255
    # tren nen 15/255. Nen tu tinh san mau DA TRON roi ve dac.
    d = ImageDraw.Draw(img)
    for y in range(200, 1620, 60):
        d.line([s(MARGIN), s(y), s(W - MARGIN), s(y)], fill=GRID_LINE + (255,),
               width=max(1, s(0.5)))
    rng = np.random.default_rng(11)
    a = np.array(img.convert("RGB")).astype(np.int16)
    a += rng.normal(0, 6, (img.height, img.width, 1)).astype(np.int16)
    _bg = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    return _bg


def _tm(txt, f):
    """(offset_y, offset_y, cao_thuc) - bien the 3 gia tri, chi theme nay dung."""
    oy, th = typo.tm(txt, f)
    return oy, oy, th


def panel(base, box, p=1.0, focus=False, accent=None, fill=None):
    """Mat phang noi dung. Tieu diem thi co vet sang + vien mau."""
    if p <= 0:
        return
    e = expo_out(p)
    x0, y0, x1, y1 = box
    # nang len tu 96% chieu cao, khong phai phong tu tam -> mem hon
    cy = (y0 + y1) / 2
    k = 0.96 + 0.04 * e
    y0, y1 = cy + (y0 - cy) * k, cy + (y1 - cy) * k
    if focus and accent:
        glow(base, (x0, y0, x1, y1), accent, 66, int(78 * e))
    d = ImageDraw.Draw(base)
    d.rectangle([s(x0), s(y0), s(x1), s(y1)], fill=(fill or SURF) + (255,),
                outline=((accent if focus else EDGE)) + (255,), width=s(2))


def hairline(base, y, col=EDGE, x0=MARGIN, x1=W - MARGIN, p=1.0, width=2):
    if p <= 0:
        return
    e = expo_out(p)
    ImageDraw.Draw(base).line(
        [s(x0), s(y), s(x0 + (x1 - x0) * e), s(y)], fill=col + (255,),
        width=s(width))


def rail(base, x, y0, y1, col, p=1.0):
    """Vach mau doc - dau hieu nhan dien, luon o cung vi tri."""
    if p <= 0:
        return
    e = expo_out(p)
    ImageDraw.Draw(base).rectangle(
        [s(x), s(y0), s(x + RAIL_W), s(y0 + (y1 - y0) * e)], fill=col + (255,))


# ------------------------------------------------------------- khung co dinh
def badge(b, dom, sp, doc=None, at=0.0):
    """Vach mau + ten mang + so ho so. Luon cung vi tri o moi video.

    `case` la tang thong tin phu ("SU CO #04") - thu nho nhung lam khung do day
    va tao cam giac day la mot ho so dieu tra, dung tinh than cong thuc.
    """
    acc = dom["color"]
    case = sp.get("case") or (doc or {}).get("case")

    def fn(base, d, p):
        rail(base, MARGIN, 150, 196, acc, min(1.0, p * 2))
        mono(base, dom["label"], (MARGIN + 24, 154), acc, p, 26, 4.5)
        if case:
            mono(base, case, (MARGIN + 24, 196), DIM, p, 22, 3.5, 400)
    b.add(fn, dur=0.34, wait=0.0, at=at)


def caption(b, txt, dom, at=0.26):
    """Phu de: chu mo tren nen toi + vach mau. Khong dung dai den dac nua."""
    if not txt:
        return
    acc = dom["color"]
    f = font("grot_med", 34)
    lines = sk.wrap(txt, f, CONTENT_W - 40)[:3]
    lh = sk.line_height(f, 1.34)

    def fn(base, d, p):
        rail(base, MARGIN, CAPTION_TOP, CAPTION_TOP + lh * len(lines) + 6, acc,
             min(1.0, p * 2))
        for i, ln in enumerate(lines):
            lp = clamp((p - i * 0.10) * 1.6)
            if lp > 0:
                ttext(base, ln, f, MUTED, CAPTION_TOP + i * lh,
                      x=MARGIN + 28, p=lp, rise=12)
    b.add(fn, dur=0.55, wait=0.0, at=at)


def wipes(b, dom):
    """Chuyen canh: BONG TOI quet qua, dan dau bang mot vach sang.

    Ban dau lam dai mau phu kin khung. Nhung 0.34s cuoi canh + 0.28s dau canh
    sau = khoang 0.6s moi diem cat; nhan voi 9 diem cat la hon 5 giay man hinh
    mau phang tren mot video 76 giay. Tren nen toi thi vua choi mat vua lang phi
    thoi luong.

    Cach nay: quet bang chinh mau nen, chi de mot vach sang o bien dan duong.
    Noi dung bi "xoa" bang bong toi, khong bao gio loe mau ca khung.
    """
    acc = dom["color"]
    EDGE_W = 5

    def _sweep(base, x_edge, cover_left):
        dd = ImageDraw.Draw(base)
        if cover_left:
            dd.rectangle([0, 0, s(x_edge), s(H)], fill=BG + (255,))
        else:
            dd.rectangle([s(x_edge), 0, s(W), s(H)], fill=BG + (255,))
        if 0 < x_edge < W:
            glow(base, (x_edge - 30, 0, x_edge + 30, H), acc, 40, 60)
            dd.rectangle([s(x_edge - EDGE_W / 2), 0, s(x_edge + EDGE_W / 2),
                          s(H)], fill=acc + (255,))

    def fn_in(base, d, p):
        e = expo_out(p)
        if e >= 1.0:
            return
        _sweep(base, W * e, cover_left=False)
    b.add(fn_in, dur=WIPE_IN, wait=0.0, at=0.0)

    def fn_out(base, d, p):
        _sweep(base, W * expo_out(p), cover_left=True)
    b.add(fn_out, dur=WIPE_OUT, wait=0.0, at=max(0.1, b.dur - WIPE_OUT))


# ============================================================== CAC LOAI CANH
def _label_over(base, txt, box, col, p, size=26):
    """Nhan mono nho dat PHIA TREN mat phang, can le trai theo mat phang."""
    mono(base, txt, (box[0] + 28, box[1] - 46), col, p, size, 4.5)


def sc_title(b, sp, dom):
    acc = dom["color"]
    f, lines, lh = headline(sp["text"], TEXT_W, 520, sp.get("size", 108),
                            min_size=66)
    total = lh * len(lines)
    y = BAND_TOP + 120

    def fn_rail(base, d, p):
        rail(base, MARGIN, y - 26, y + total + 10, acc, p)
    b.add(fn_rail, dur=0.4, wait=0.24)

    for i, ln in enumerate(lines):
        def fn(base, d, p, ln=ln, i=i):
            ttext(base, ln, f, FG, y + i * lh, x=MARGIN + 30, track=-2.5, p=p,
                  rise=26)
        b.add(fn, dur=0.5, wait=0.22)

    def fn_rule(base, d, p):
        hairline(base, y + total + 46, EDGE, MARGIN, W - MARGIN, p)
    b.add(fn_rule, dur=0.45, wait=0.26)

    if sp.get("sub"):
        sf = font("grot", 46)
        slines = sk.wrap(sp["sub"], sf, CONTENT_W - 40)

        def fn_s(base, d, p):
            for i, ln in enumerate(slines):
                lp = clamp((p - i * 0.12) * 1.5)
                ttext(base, ln, sf, MUTED, y + total + 86 + i * lh * 0.5,
                      x=MARGIN + 30, p=lp, rise=16)
        b.add(fn_s, dur=0.5, wait=0.3)


def sc_bigstat(b, sp, dom):
    acc = ALERT if sp.get("color") == "alert" else dom["color"]
    f, lines, lh = headline(sp["value"], TEXT_W, 620,
                            sp.get("size", 150), min_size=76, track=-3.5)
    total = lh * len(lines)
    y = BAND_TOP + 140
    if sp.get("label"):
        def fn_l(base, d, p):
            mono(base, sp["label"], (MARGIN + 30, y - 56), MUTED, p, 26, 4.5)
        b.add(fn_l, dur=0.35, wait=0.2)

    # vet sang chi bam theo BE RONG CHU, khong keo ngang ca khung -
    # keo ngang thi trong nhu vet loi lens flare chu khong phai chu dich
    gw = max(track_w(l, f, -3.5) for l in lines)

    def fn_g(base, d, p):
        glow(base, (MARGIN + 30, y + 10, MARGIN + 30 + gw, y + total - 10),
             acc, 78, int(46 * expo_out(p)))
    b.add(fn_g, dur=0.6, wait=0.12)

    def fn_rail(base, d, p):
        rail(base, MARGIN, y - 10, y + total + 6, acc, p)
    b.add(fn_rail, dur=0.4, wait=0.2)

    for i, ln in enumerate(lines):
        def fn(base, d, p, ln=ln, i=i):
            ttext(base, ln, f, FG, y + i * lh, x=MARGIN + 30, track=-3.5, p=p,
                  rise=30)
        b.add(fn, dur=0.52, wait=0.24)

    if sp.get("sub"):
        sf = font("grot_black", 54)

        def fn_s(base, d, p):
            ttext(base, sp["sub"], sf, acc, y + total + 60, x=MARGIN + 30,
                  track=-1.5, p=p, rise=20)
        b.add(fn_s, dur=0.5, wait=0.28)


def sc_compare(b, sp, dom):
    acc = dom["color"]
    items = sp["items"][:2]
    focus = next((i for i, it in enumerate(items)
                  if it.get("focus") or it.get("cross")), len(items) - 1)
    ph = 208
    gap = 116
    y0 = BAND_TOP + 120
    boxes = []
    for i, it in enumerate(items):
        by = y0 + i * (ph + gap)
        box = (MARGIN, by, W - MARGIN, by + ph)
        boxes.append(box)
        is_f = (i == focus)
        col = ALERT if (is_f and it.get("cross")) else (acc if is_f else EDGE)
        vcol = FG if is_f else DIM

        def fn(base, d, p, box=box, it=it, is_f=is_f, col=col, vcol=vcol):
            panel(base, box, p, focus=is_f, accent=col)
            if p > 0.22:
                q = (p - 0.22) / 0.78
                _label_over(base, it["label"], box, col if is_f else MUTED, q)
                vf = font("grot_black", 94)
                oy, _, th = _tm(it["value"], vf)
                ttext(base, it["value"], vf, vcol,
                      (box[1] + box[3]) / 2 - th / 2, x=box[0] + 28,
                      track=-2.5, p=q, rise=22)
                if it.get("cross"):
                    mono(base, "×2", (box[2] - 110, (box[1] + box[3]) / 2 - 22),
                         ALERT, q, 34, 0, 700)
        b.add(fn, dur=0.55, wait=0.34)

    if sp.get("verdict"):
        _verdict(b, sp["verdict"], boxes[-1][3] + 76, ALERT)


def sc_flow(b, sp, dom):
    acc = dom["color"]
    steps = sp["steps"]
    n = len(steps)
    focus = next((i for i, st_ in enumerate(steps) if st_.get("focus")), n - 1)
    reserve = 150 if sp.get("verdict") else 0
    top, bottom = BAND_TOP + 60, BAND_BOTTOM - reserve
    ph = 132
    gap = max(58, min((bottom - top - ph * n) / max(1, n - 1), 104))
    total = ph * n + gap * (n - 1)
    y = top + (bottom - top - total) / 2

    for i, stp in enumerate(steps):
        by = y + i * (ph + gap)
        box = (MARGIN, by, W - MARGIN, by + ph)
        is_f = (i == focus)
        col = ALERT if stp.get("bad") else (acc if is_f else EDGE)

        def fn(base, d, p, box=box, stp=stp, is_f=is_f, col=col, i=i):
            panel(base, box, p, focus=is_f, accent=col)
            if p > 0.22:
                q = (p - 0.22) / 0.78
                mono(base, f"{i+1:02d}", (box[0] + 28, box[1] + 24),
                     col if is_f else DIM, q, 24, 3)
                tf = font("grot_black", 58)
                oy, _, th = _tm(stp["text"], tf)
                ttext(base, stp["text"], tf, FG if is_f else DIM,
                      (box[1] + box[3]) / 2 - th / 2 + 8, x=box[0] + 28,
                      track=-1.5, p=q, rise=18)
        b.add(fn, dur=0.5, wait=0.3)

        if i < n - 1:
            lab = steps[i + 1].get("arrow_label")

            def fn_c(base, d, p, by=by, lab=lab):
                e = expo_out(p)
                x = MARGIN + 42
                ImageDraw.Draw(base).line(
                    [s(x), s(by + ph), s(x), s(by + ph + gap * e)],
                    fill=EDGE + (255,), width=s(3))
                if lab and p > 0.45:
                    mono(base, lab, (x + 24, by + ph + gap / 2 - 16), DIM,
                         (p - 0.45) / 0.55, 22, 3, 400)
            b.add(fn_c, dur=0.4, wait=0.22)

    if sp.get("verdict"):
        _verdict(b, sp["verdict"], y + total + 60, ALERT)


def sc_timeline(b, sp, dom):
    acc = dom["color"]
    y = BAND_TOP + 330
    hgt = 96
    x0, x1 = MARGIN, W - MARGIN
    g = sp.get("gap")

    if g and g.get("note"):
        def fn_n(base, d, p):
            nf = font("grot_black", 168)
            oy, _, th = _tm(g["note"], nf)
            mono(base, "KHOẢNG HỞ", (MARGIN + 30, y - 300), MUTED,
                 min(1.0, p * 2), 24, 4.5)
            ttext(base, g["note"], nf, ALERT, y - 252, x=MARGIN + 30,
                  track=-5, p=p, rise=32)
        b.add(fn_n, dur=0.55, wait=0.3)

    def fn_track(base, d, p):
        panel(base, (x0, y, x1, y + hgt), p)
    b.add(fn_track, dur=0.45, wait=0.3)

    positions = []
    for i, m in enumerate(sp.get("marks", [])):
        mx = x0 + (x1 - x0) * float(m["at"])
        positions.append(mx)

        def fn_m(base, d, p, mx=mx, m=m):
            e = expo_out(p)
            ImageDraw.Draw(base).line(
                [s(mx), s(y - 14), s(mx), s(y + hgt * e + 14)],
                fill=MUTED + (255,), width=s(3))
            if p > 0.4:
                mono(base, m["label"], (mx + 14, y + hgt + 22), MUTED,
                     (p - 0.4) / 0.6, 22, 3)
        b.add(fn_m, dur=0.42, wait=0.26)

    if g and len(positions) >= 2:
        gx0 = x0 + (x1 - x0) * float(g["from"])
        gx1 = x0 + (x1 - x0) * float(g["to"])

        def fn_g(base, d, p):
            e = expo_out(p)
            glow(base, (gx0, y, gx1, y + hgt), ALERT, 50, int(70 * e))
            ImageDraw.Draw(base).rectangle(
                [s(gx0), s(y + 3), s(gx0 + (gx1 - gx0) * e), s(y + hgt - 3)],
                fill=ALERT + (255,))
        b.add(fn_g, dur=0.5, wait=0.3)

    if sp.get("intruder"):
        ix = sum(positions[:2]) / 2 if len(positions) >= 2 else CX

        def fn_i(base, d, p):
            e = expo_out(p)
            ImageDraw.Draw(base).line(
                [s(ix), s(y + hgt + 210), s(ix), s(y + hgt + 210 - 120 * e)],
                fill=acc + (255,), width=s(3))
            if p > 0.4:
                mono(base, sp["intruder"], (ix + 20, y + hgt + 196), acc,
                     (p - 0.4) / 0.6, 24, 3.5)
        b.add(fn_i, dur=0.45, wait=0.28)


def sc_sticky(b, sp, dom):
    acc = dom["color"]
    hf = font("grot_black", 62)
    bf, blines, blh = headline(sp.get("body", ""), CONTENT_W - 90, 300, 60,
                               min_size=42, track=-1.5) if sp.get("body") \
        else (None, [], 0)
    sfz = font("grot_med", 32)
    slines = sk.wrap(sp.get("small", ""), sfz, CONTENT_W - 100) \
        if sp.get("small") else []
    slh = sk.line_height(sfz, 1.36)

    hh = 96
    inner = (blh * len(blines) if blines else 0) + \
            ((slh * len(slines) + 28) if slines else 0) + 88
    y0 = (BAND_TOP + BAND_BOTTOM) / 2 - (hh + inner) / 2
    box = (MARGIN, y0, W - MARGIN, y0 + hh + inner)

    def fn_p(base, d, p):
        panel(base, box, p, focus=True, accent=acc, fill=SURF)
    b.add(fn_p, dur=0.48, wait=0.28)

    def fn_h(base, d, p):
        e = expo_out(p)
        ImageDraw.Draw(base).rectangle(
            [s(MARGIN), s(y0), s(MARGIN + CONTENT_W * e), s(y0 + hh)],
            fill=acc + (255,))
        if p > 0.4:
            oy, _, th = _tm(sp["heading"], hf)
            ttext(base, sp["heading"], hf, BG, y0 + hh / 2 - th / 2,
                  x=MARGIN + 30, track=-1.5, p=(p - 0.4) / 0.6, rise=14)
    b.add(fn_h, dur=0.5, wait=0.3)

    if blines:
        def fn_b(base, d, p):
            for i, ln in enumerate(blines):
                lp = clamp((p - i * 0.12) * 1.5)
                ttext(base, ln, bf, FG, y0 + hh + 42 + i * blh, x=MARGIN + 30,
                      track=-1.5, p=lp, rise=18)
        b.add(fn_b, dur=0.52, wait=0.3)

    if slines:
        ytop = y0 + hh + 42 + (blh * len(blines) if blines else 0) + 28

        def fn_s(base, d, p):
            hairline(base, ytop - 14, EDGE, MARGIN + 30, W - MARGIN - 30,
                     min(1.0, p * 2))
            for i, ln in enumerate(slines):
                lp = clamp((p - 0.2 - i * 0.1) * 1.6)
                if lp > 0:
                    ttext(base, ln, sfz, DIM, ytop + i * slh, x=MARGIN + 30,
                          p=lp, rise=12)
        b.add(fn_s, dur=0.5, wait=0.26)


def sc_code(b, sp, dom):
    acc = dom["color"]
    clines = sp["code"] if isinstance(sp["code"], list) else [sp["code"]]
    cf = font("mono", sp.get("code_size", 46))
    clh = sk.line_height(cf, 1.5)
    hh = 76
    ch = clh * len(clines) + 76
    y0 = (BAND_TOP + BAND_BOTTOM) / 2 - (hh + ch) / 2 - \
        (60 if sp.get("verdict") else 0)
    box = (MARGIN, y0, W - MARGIN, y0 + hh + ch)

    def fn_p(base, d, p):
        panel(base, box, p, fill=SURF)
    b.add(fn_p, dur=0.46, wait=0.28)

    def fn_h(base, d, p):
        e = expo_out(p)
        ImageDraw.Draw(base).rectangle(
            [s(MARGIN + 2), s(y0 + 2), s(MARGIN + 2 + (CONTENT_W - 4) * e),
             s(y0 + hh)], fill=SURF_HI + (255,))
        hairline(base, y0 + hh, EDGE, MARGIN, W - MARGIN, e)
        if p > 0.35:
            mono(base, sp["heading"], (MARGIN + 28, y0 + 24), acc,
                 (p - 0.35) / 0.65, 26, 4.5)
    b.add(fn_h, dur=0.45, wait=0.28)

    def fn_c(base, d, p):
        for i, ln in enumerate(clines):
            lp = clamp((p - i * 0.16) * 1.6)
            if lp > 0:
                ttext(base, ln, cf, FG, y0 + hh + 36 + i * clh, x=MARGIN + 34,
                      p=lp, rise=14)
    b.add(fn_c, dur=0.55, wait=0.3)

    if sp.get("mark") == "cross":
        def fn_x(base, d, p):
            mono(base, "FAILED", (W - MARGIN - 150, y0 + 26), ALERT, p, 24, 3.5,
                 700)
        b.add(fn_x, dur=0.35, wait=0.24)
    elif sp.get("mark") == "check":
        def fn_v(base, d, p):
            mono(base, "OK", (W - MARGIN - 76, y0 + 26), acc, p, 24, 3.5, 700)
        b.add(fn_v, dur=0.35, wait=0.24)

    if sp.get("verdict"):
        _verdict(b, sp["verdict"], y0 + hh + ch + 70, ALERT)


def sc_checklist(b, sp, dom):
    acc = dom["color"]
    items = sp["items"]
    n = len(items)
    focus = next((i for i, it in enumerate(items)
                  if isinstance(it, dict) and it.get("focus")), None)
    tsize = {1: 62, 2: 58, 3: 52, 4: 46}.get(n, 40)
    tf = font("grot_black", tsize)
    rows = []
    for it in items:
        txt = it if isinstance(it, str) else it["text"]
        lines = wrap_track(txt, tf, CONTENT_W - 130, -1.2)
        rows.append((lines, it if isinstance(it, dict) else {}))
    lh = sk.text_size("Ăgjqy", tf)[1] * 1.2
    heights = [lh * len(l) + 62 for l, _ in rows]
    total = sum(heights)
    y = (BAND_TOP + BAND_BOTTOM) / 2 - total / 2
    ys, acc_y = [], y
    for h_ in heights:
        ys.append(acc_y)
        acc_y += h_

    for i, ((lines, meta), yy) in enumerate(zip(rows, ys)):
        is_f = (focus == i)

        def fn(base, d, p, i=i, lines=lines, yy=yy, is_f=is_f):
            hairline(base, yy, EDGE, MARGIN, W - MARGIN, min(1.0, p * 2))
            col = ALERT if is_f else (acc if focus is None else DIM)
            mono(base, f"{i+1:02d}", (MARGIN, yy + 26), col,
                 min(1.0, p * 1.6), 26, 3)
            if is_f:
                rail(base, MARGIN + 84, yy + 24, yy + 24 + lh * len(lines),
                     ALERT, min(1.0, p * 1.6))
            for j, ln in enumerate(lines):
                lp = clamp((p - j * 0.1) * 1.5)
                ttext(base, ln, tf, FG if (is_f or focus is None) else DIM,
                      yy + 22 + j * lh, x=MARGIN + 112, track=-1.2, p=lp,
                      rise=18)
        b.add(fn, dur=0.5, wait=0.3)

    def fn_end(base, d, p):
        hairline(base, ys[-1] + heights[-1], EDGE, MARGIN, W - MARGIN, p)
    b.add(fn_end, dur=0.4, wait=0.2)


def sc_figures(b, sp, dom):
    acc = dom["color"]
    n = sp.get("count", 10)
    lit = sp.get("lit", n)
    cols = min(n, 5)
    rows_n = (n + cols - 1) // cols
    gapx = 20
    cell = min(160, (CONTENT_W - (cols - 1) * gapx) / cols)
    gw = cell * cols + gapx * (cols - 1)
    gh = cell * rows_n + gapx * (rows_n - 1)
    ox = MARGIN
    oy = (BAND_TOP + BAND_BOTTOM) / 2 - gh / 2 - (70 if sp.get("label") else 0)

    def fn(base, d, p):
        dd = ImageDraw.Draw(base)
        for i in range(n):
            q = clamp((p - i / n * 0.6) * 3.0)
            if q <= 0:
                continue
            r, c = divmod(i, cols)
            bx, by = ox + c * (cell + gapx), oy + r * (cell + gapx)
            e = expo_out(q)
            k = 0.9 + 0.1 * e
            cxx, cyy = bx + cell / 2, by + cell / 2
            hw = cell / 2 * k
            if i < lit:
                dd.rectangle([s(cxx - hw), s(cyy - hw), s(cxx + hw),
                              s(cyy + hw)], fill=acc + (255,))
            else:
                dd.rectangle([s(cxx - hw), s(cyy - hw), s(cxx + hw),
                              s(cyy + hw)], fill=SURF + (255,),
                             outline=EDGE + (255,), width=s(2))
    b.add(fn, dur=0.85, wait=0.5)

    if sp.get("label"):
        _verdict(b, sp["label"], oy + gh + 70, ALERT)


def sc_qa(b, sp, dom):
    acc = dom["color"]
    f, lines, lh = headline(sp["text"], TEXT_W - 30, 560,
                            sp.get("size", 116), min_size=72, track=-3)
    total = lh * len(lines)
    y0 = (BAND_TOP + BAND_BOTTOM) / 2 - total / 2 - 56
    box = (MARGIN, y0 - 56, W - MARGIN, y0 + total + 56)

    def fn_p(base, d, p):
        panel(base, box, p, focus=True, accent=acc, fill=SURF)
    b.add(fn_p, dur=0.5, wait=0.3)

    for i, ln in enumerate(lines):
        def fn(base, d, p, ln=ln, i=i):
            ttext(base, ln, f, acc if i == 0 else FG, y0 + i * lh,
                  x=MARGIN + 32, track=-3, p=p, rise=26)
        b.add(fn, dur=0.55, wait=0.26)


def sc_decay(b, sp, dom):
    ph = 216
    y0 = BAND_TOP + 90
    box = (MARGIN, y0, W - MARGIN, y0 + ph)

    def fn_p(base, d, p):
        panel(base, box, p, focus=True, accent=ALERT)
        if p > 0.22:
            q = (p - 0.22) / 0.78
            _label_over(base, sp.get("label", "CACHE"), box, ALERT, q)
            vf = font("grot_black", 108)
            oy, _, th = _tm(sp["value"], vf)
            ttext(base, sp["value"], vf, FG, (box[1] + box[3]) / 2 - th / 2,
                  x=box[0] + 28, track=-3, p=q, rise=24)
    b.add(fn_p, dur=0.55, wait=0.34)

    stops = sp.get("stops", [])
    if stops:
        sy = y0 + ph + 90
        sw = (CONTENT_W - (len(stops) - 1) * 18) / len(stops)
        for i, stp in enumerate(stops):
            sx = MARGIN + i * (sw + 18)

            def fn_s(base, d, p, sx=sx, stp=stp):
                panel(base, (sx, sy, sx + sw, sy + 96), p)
                if p > 0.3:
                    mono(base, stp, (sx + 22, sy + 34), MUTED,
                         (p - 0.3) / 0.7, 26, 3)
            b.add(fn_s, dur=0.4, wait=0.22)

    if sp.get("verdict"):
        _verdict(b, sp["verdict"], y0 + ph + 90 + 96 + 74, ALERT)


def sc_race(b, sp, dom):
    """MO PHONG dang Gantt: hai luong dan vao nhau theo thoi gian."""
    acc = dom["color"]
    lanes = sp["lanes"][:3]
    x0, x1 = MARGIN, W - MARGIN
    lane_h, lane_gap, label_h = 126, 40, 52
    total = len(lanes) * (lane_h + label_h) + (len(lanes) - 1) * lane_gap
    top = BAND_TOP + 90
    coll = sp.get("collision")

    def fn(base, d, p):
        head = x0 + (x1 - x0) * clamp(p)
        dd = ImageDraw.Draw(base)
        geom = []
        for li, lane in enumerate(lanes):
            ly = top + li * (lane_h + label_h + lane_gap)
            by = ly + label_h
            lcol = _c(lane.get("color"), acc)
            geom.append((lane, ly, by, lcol))
            dd.rectangle([s(x0), s(by), s(x1), s(by + lane_h)],
                         fill=SURF + (255,), outline=EDGE + (255,), width=s(2))
            for step in lane.get("steps", []):
                sx = x0 + (x1 - x0) * float(step["at"])
                sw = (x1 - x0) * float(step.get("w", 0.18))
                if head < sx:
                    continue
                grow = clamp((head - sx) / max(sw, 1e-6))
                fill = ALERT if step.get("bad") else lcol
                dd.rectangle([s(sx), s(by + 4), s(sx + sw * grow),
                              s(by + lane_h - 4)], fill=fill + (255,))
        # dau doc chi quet trong vung duong ray, khong cat ngang nhan
        for _, _, by, _ in geom:
            dd.line([s(head), s(by - 12), s(head), s(by + lane_h + 12)],
                    fill=FG + (255,), width=s(3))
        # chu luon tren cung
        for lane, ly, by, _ in geom:
            mono(base, lane["label"], (x0, ly + 10), MUTED, 1.0, 24, 3.5)
            for step in lane.get("steps", []):
                sx = x0 + (x1 - x0) * float(step["at"])
                sw = (x1 - x0) * float(step.get("w", 0.18))
                if head < sx:
                    continue
                if clamp((head - sx) / max(sw, 1e-6)) >= 0.97:
                    mono(base, step["text"], (sx + 18, by + lane_h / 2 - 16),
                         BG, 1.0, 26, 2, 700)
        if coll and p >= float(coll["at"]):
            q = clamp((p - float(coll["at"])) / 0.14)
            cy = top + total + 76
            cf = font("grot_black", 76)
            glow(base, (MARGIN, cy, W - MARGIN, cy + 90), ALERT, 70, int(80 * q))
            rail(base, MARGIN, cy, cy + 90, ALERT, q)
            ttext(base, coll["label"], cf, ALERT, cy + 4, x=MARGIN + 30,
                  track=-2.5, p=q, rise=22)
    b.add(fn, dur=max(1.6, b.dur * 0.72), wait=b.dur)


def sc_topology(b, sp, dom):
    """MO PHONG dang so do he thong: cac node + goi tin BAY giua chung.

    Khac `race` o cho tra loi cau "O DAU" chu khong phai "KHI NAO". Mat nguoi
    xem tu bam theo vat chuyen dong, khong phai hoc cach doc bieu do.
    """
    acc = dom["color"]
    nodes = {nd["id"]: nd for nd in sp["nodes"]}
    order = [nd["id"] for nd in sp["nodes"]]
    top, bottom = BAND_TOP + 60, BAND_BOTTOM - 90
    nw, nh = CONTENT_W - 240, 116
    packets = sp.get("packets", [])
    events = sp.get("events", [])

    pos = {}
    for nd in sp["nodes"]:
        ax, ay = nd.get("at", [0.5, 0.5])
        cx = MARGIN + 120 + nw * float(ax)
        cy = top + (bottom - top) * float(ay)
        pos[nd["id"]] = (cx, cy)

    def fn(base, d, p):
        dd = ImageDraw.Draw(base)
        # canh noi giua cac node lien tiep
        for i in range(len(order) - 1):
            a, bb = pos[order[i]], pos[order[i + 1]]
            dd.line([s(a[0]), s(a[1] + nh / 2), s(bb[0]), s(bb[1] - nh / 2)],
                    fill=EDGE + (255,), width=s(2))
        # node
        for nid in order:
            cx, cy = pos[nid]
            nd = nodes[nid]
            hit = any(ev.get("node") == nid and p >= float(ev["at"])
                      for ev in events)
            box = (cx - nw / 2, cy - nh / 2, cx + nw / 2, cy + nh / 2)
            col = ALERT if hit else EDGE
            if hit:
                glow(base, box, ALERT, 56, 70)
            dd.rectangle([s(box[0]), s(box[1]), s(box[2]), s(box[3])],
                         fill=SURF + (255,), outline=col + (255,), width=s(2))
            mono(base, nd["label"], (box[0] + 26, cy - 16),
                 ALERT if hit else FG, 1.0, 30, 3.5, 700)
        # goi tin: hinh tron bay tu node nay sang node kia
        for pk in packets:
            at = float(pk["at"])
            dur = float(pk.get("dur", 0.14))
            if p < at:
                continue
            k = clamp((p - at) / dur)
            a, bb = pos[pk["from"]], pos[pk["to"]]
            ax, ay = a[0], a[1] + nh / 2
            bx, by = bb[0], bb[1] - nh / 2
            e = k if k < 1 else 1.0
            px, py = ax + (bx - ax) * e, ay + (by - ay) * e
            col = ALERT if pk.get("bad") else _c(pk.get("color"), acc)
            r = 26
            if k >= 1.0 and not pk.get("stay"):
                continue
            glow(base, (px - r, py - r, px + r, py + r), col, 34, 90)
            dd.ellipse([s(px - r), s(py - r), s(px + r), s(py + r)],
                       fill=col + (255,))
            if pk.get("label"):
                mono(base, pk["label"], (px + r + 14, py - 15), col, 1.0, 24,
                     2.5, 700)
        # su kien: nhan mono canh node
        for ev in events:
            if p < float(ev["at"]):
                continue
            q = clamp((p - float(ev["at"])) / 0.10)
            cx, cy = pos[ev["node"]]
            mono(base, ev["label"], (cx + nw / 2 + 20, cy - 14), ALERT, q, 24,
                 3, 700)
    b.add(fn, dur=max(1.8, b.dur * 0.74), wait=b.dur)


def _c(name, fallback):
    if not name:
        return fallback
    return {"blue": (96, 165, 250), "green": (52, 211, 153),
            "amber": (251, 191, 36), "purple": (167, 139, 250),
            "alert": ALERT, "fg": FG}.get(name, fallback)


def _verdict(b, txt, y, col, size=82, wait=0.32):
    """Cau ket: gach hairline + chu dam can le trai. Tu keo len neu sap tran."""
    f, lines, lh = headline(txt, TEXT_W, 240, size, min_size=54, track=-2.5)
    h = lh * len(lines)
    if y + h > CAPTION_TOP - 60:
        y = CAPTION_TOP - 60 - h

    def fn(base, d, p):
        hairline(base, y - 34, EDGE, MARGIN, W - MARGIN, min(1.0, p * 2))
        for i, ln in enumerate(lines):
            lp = clamp((p - i * 0.12) * 1.5)
            ttext(base, ln, f, col, y + i * lh, x=MARGIN + 30, track=-2.5,
                  p=lp, rise=22)
    b.add(fn, dur=0.55, wait=wait)


BUILDERS = {
    "title": sc_title, "bigstat": sc_bigstat, "compare": sc_compare,
    "flow": sc_flow, "timeline": sc_timeline, "sticky": sc_sticky,
    "code": sc_code, "checklist": sc_checklist, "figures": sc_figures,
    "qa": sc_qa, "decay": sc_decay,
    # --- mo phong
    "race": sc_race, "topology": sc_topology,
}


def build(sp, dur, doc=None):
    kind = sp.get("scene")
    if kind not in BUILDERS:
        raise ValueError(f"theme phongtoi khong co loai canh {kind!r}. "
                         f"Co: {', '.join(sorted(BUILDERS))}")
    dom = domain(sp, (doc or {}).get("domain"))
    b = B(dur)
    badge(b, dom, sp, doc)
    BUILDERS[kind](b, sp, dom)
    b.finish()
    caption(b, sp.get("caption"), dom, at=0.24)
    # dai quet phai them CUOI CUNG: phan tu ve theo thu tu, no can nam tren het
    wipes(b, dom)
    return b.els
