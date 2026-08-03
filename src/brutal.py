"""Theme NEO-BRUTALIST: khoi mau phang, vien den day, bong lech cung.

Khac han theme whiteboard o ba diem:
  1. Khong co net ve tay xieu xieu. Hinh hoc cung, truc thang, khong nhieu.
  2. Phan tu KHONG ve dan ma "dap vao" - phong tu 0.9 vuot co roi co lai.
  3. Chuyen canh cat thang, khong mo dan.

QUY TAC MOT DIEM NHAN: moi canh chi co DUNG MOT khoi duoc to mau domain.
Moi khoi con lai to trang, chu xam nhat. Mat khan gia biet nhin dau ngay.
Cac builder tu ap quy tac nay, screenplay khong phai khai bao gi them.
"""
import math

from PIL import Image, ImageDraw

import sketch as sk
import style as st
from style import H, W, clamp, font, s
from timing import B

# ---------------------------------------------------------------- chuyen canh
FADE = 0.0          # 0 = cat thang, dung chat brutalist
TRANSITION = "cut"

# --------------------------------------------------------------------- mau sac
PAPER = (242, 239, 230)      # giay am, sang hon noi dung -> khoi mau noi bat
INK = (17, 17, 17)           # den vien va chu
WHITE = (255, 255, 255)      # khoi khong phai diem nhan
MUTED = (138, 136, 128)      # chu cua khoi khong phai diem nhan
ALERT = (255, 77, 61)        # cai sai, canh bao
SHADOW = (17, 17, 17)

# Ma mau theo domain: xem 0,5 giay biet video thuoc mang nao.
DOMAINS = {
    "fe":       {"label": "FRONTEND", "color": (255, 212, 0)},
    "be":       {"label": "BACKEND",  "color": (74, 222, 128)},
    "database": {"label": "DATABASE", "color": (96, 165, 250)},
    "infra":    {"label": "HẠ TẦNG",  "color": (192, 132, 252)},
}
DEFAULT_DOMAIN = "be"

# ------------------------------------------------------------------ hinh khoi
BORDER = 7           # do day vien den
SHADOW_OFF = 13      # do lech bong
MARGIN = 56
CX = W // 2
CONTENT_W = W - MARGIN * 2

BAND_TOP = 290       # noi dung bat dau duoi badge
BAND_BOTTOM = 1290   # het noi dung, duoi la dai phu de
CAPTION_TOP = 1330   # dai phu de den full-bleed (TikTok phu UI tu ~1630)


def big_lines(txt, max_w, max_h, size, min_size=80, gap=1.06,
              role="slab_black"):
    """Uu tien NGAT DONG o co chu that lon, chi thu nho khi khoi qua cao.

    Khac han `sk.fit_lines` (co chu lai cho vua MOT dong). Brutalism can chu
    to het khung; hai dong chu khong lo dep hon mot dong chu vua phai.
    """
    sz = size
    while sz > min_size:
        f = font(role, sz)
        lines = sk.wrap_balanced(txt, f, max_w)
        if sk.block_metrics(lines, f, gap)[1] <= max_h:
            return f, lines
        sz -= 6
    f = font(role, min_size)
    return f, sk.wrap_balanced(txt, f, max_w)


def domain(sp, doc_domain=None):
    key = (sp.get("domain") or doc_domain or DEFAULT_DOMAIN).lower()
    return DOMAINS.get(key, DOMAINS[DEFAULT_DOMAIN])


# ------------------------------------------------------------------ nen phang
_bg = None


def background():
    """Nen phang tuyet doi. Khong luoi cham, khong vignette - brutalism."""
    global _bg
    if _bg is None:
        _bg = Image.new("RGBA", (s(W), s(H)), PAPER + (255,))
    return _bg


# ------------------------------------------------------------------- chuyen dong
def back_out(p, k=1.5):
    """Dap vao: vuot qua co roi co lai. Day la nhip dac trung cua theme nay."""
    p = clamp(p)
    p -= 1
    return 1 + (k + 1) * p ** 3 + k * p ** 2


def snap_box(box, p):
    """Phong khoi tu 0.88 len 1.0 quanh tam, co vuot co nhe."""
    e = back_out(p)
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    k = 0.88 + 0.12 * e
    return (cx + (x0 - cx) * k, cy + (y0 - cy) * k,
            cx + (x1 - cx) * k, cy + (y1 - cy) * k)


# --------------------------------------------------------------- bo ve co ban
def block(base, box, fill, p=1.0, shadow=True, border=BORDER, rotate=0.0):
    """Khoi chu nhat phang: bong lech cung + vien den day. Khong bo goc."""
    if p <= 0:
        return
    x0, y0, x1, y1 = snap_box(box, p)
    w, h = max(1, int(s(x1 - x0))), max(1, int(s(y1 - y0)))
    off = int(s(SHADOW_OFF) * clamp(p * 1.4)) if shadow else 0
    pad = off + s(6)
    layer = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    if shadow and off:
        ld.rectangle([pad + off, pad + off, pad + w + off, pad + h + off],
                     fill=SHADOW + (255,))
    ld.rectangle([pad, pad, pad + w, pad + h], fill=fill + (255,),
                 outline=INK + (255,), width=s(border))
    if rotate:
        layer = layer.rotate(rotate, expand=True, resample=Image.BICUBIC)
    base.alpha_composite(layer, (int(s(x0)) - pad, int(s(y0)) - pad))


def slab(base, y0, y1, fill, p=1.0, full_bleed=True):
    """Dai mau chay het be ngang khung. Lan tu trai sang phai."""
    if p <= 0:
        return
    x0 = 0 if full_bleed else MARGIN
    x1 = W if full_bleed else W - MARGIN
    w = (x1 - x0) * st.ease_out(p)
    d = ImageDraw.Draw(base)
    d.rectangle([s(x0), s(y0), s(x0 + w), s(y1)], fill=fill + (255,))


def bar(base, box, fill, p=1.0, border=BORDER):
    """Thanh ngang lan ra, dung cho meter / TTL."""
    x0, y0, x1, y1 = box
    w = (x1 - x0) * st.ease_out(p)
    d = ImageDraw.Draw(base)
    d.rectangle([s(x0), s(y0), s(x0 + w), s(y1)], fill=fill + (255,),
                outline=INK + (255,), width=s(border))


def chunky_arrow(base, p0, p1, color, p=1.0, width=11, head=34):
    """Mui ten day, dau tam giac dac. Khong nhieu, khong cong."""
    if p <= 0:
        return
    d = ImageDraw.Draw(base)
    x0, y0 = p0
    x1, y1 = p1
    e = st.ease_out(p)
    ex, ey = x0 + (x1 - x0) * e, y0 + (y1 - y0) * e
    d.line([s(x0), s(y0), s(ex), s(ey)], fill=color + (255,), width=s(width))
    if p > 0.62:
        hp = clamp((p - 0.62) / 0.38)
        ang = math.atan2(ey - y0, ex - x0) if (ex != x0 or ey != y0) else math.pi / 2
        hl = head * hp
        tip = (ex, ey)
        a = (ex - math.cos(ang) * hl + math.cos(ang + math.pi / 2) * hl * 0.62,
             ey - math.sin(ang) * hl + math.sin(ang + math.pi / 2) * hl * 0.62)
        c = (ex - math.cos(ang) * hl - math.cos(ang + math.pi / 2) * hl * 0.62,
             ey - math.sin(ang) * hl - math.sin(ang + math.pi / 2) * hl * 0.62)
        d.polygon([(s(tip[0]), s(tip[1])), (s(a[0]), s(a[1])),
                   (s(c[0]), s(c[1]))], fill=color + (255,))


def cross_out(base, box, p=1.0, width=14, color=None):
    """Gach cheo X. `color` phai tuong phan voi nen khoi ben duoi.

    Mac dinh la do; nhung ve do len khoi da to do thi mat hut, nen khoi alert
    phai truyen mau den vao.
    """
    color = color or ALERT
    d = ImageDraw.Draw(base)
    x0, y0, x1, y1 = box
    e1 = clamp(p * 2)
    d.line([s(x0), s(y0), s(x0 + (x1 - x0) * e1), s(y0 + (y1 - y0) * e1)],
           fill=color + (255,), width=s(width))
    if p > 0.5:
        e2 = clamp((p - 0.5) * 2)
        d.line([s(x1), s(y0), s(x1 - (x1 - x0) * e2), s(y0 + (y1 - y0) * e2)],
               fill=color + (255,), width=s(width))


def stamp(base, text, center, color, p=1.0, size=64, rotate=-9):
    """Con dau: chu trong khung vien, xoay nhe. Dung cho SAI / ĐÚNG."""
    if p <= 0:
        return
    f = font("slab_black", size)
    tw, th = sk.text_size(text, f)
    padx, pady = 34, 20
    bw, bh = tw + padx * 2, th + pady * 2
    layer = Image.new("RGBA", (s(bw) + s(20), s(bh) + s(20)), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    e = back_out(p)
    ld.rectangle([s(10), s(10), s(10 + bw), s(10 + bh)], outline=color + (255,),
                 width=s(7))
    oy, _ = sk.text_metrics(text, f)
    ld.text((s(10 + padx), s(10 + pady) - s(oy)), text, font=f,
            fill=color + (255,))
    layer = layer.rotate(rotate, expand=True, resample=Image.BICUBIC)
    if e < 1.0:
        a = clamp(e)
        layer.putalpha(layer.getchannel("A").point(lambda v: int(v * a)))
    base.alpha_composite(layer, (int(s(center[0] - bw / 2)) - s(10),
                                 int(s(center[1] - bh / 2)) - s(10)))


def text(base, lines, role, size, color, p=1.0, cx=None, x=None, y=None,
         vcenter=None, align="center", gap=1.12, max_w=None, min_size=44):
    """Chu brutalist: hien nhanh, truot len mot chut. Khong ve dan tung net."""
    if isinstance(lines, str):
        if max_w:
            f, lines = sk.fit_lines(role, lines, max_w, size, min_size=min_size,
                                    gap=gap)
        else:
            f, lines = font(role, size), [lines]
    else:
        f = font(role, size)
    sk.draw_text(base, lines, f, color, cx=cx, x=x, y=y or 0, align=align,
                 gap=gap, p=p, reveal="fade", vcenter=vcenter)
    return f, lines


def block_text(base, box, lines, role, size, color, p=1.0, gap=1.12,
               min_size=36):
    """Chu can giua trong mot khoi, tu co cho vua be ngang khoi."""
    x0, y0, x1, y1 = box
    if isinstance(lines, str):
        f, lines = sk.fit_lines(role, lines, (x1 - x0) - 60, size,
                                min_size=min_size, gap=gap)
    else:
        f = font(role, size)
    sk.draw_text(base, lines, f, color, cx=(x0 + x1) / 2, gap=gap, p=p,
                 reveal="fade", vcenter=(y0 + y1) / 2)


# ------------------------------------------------------------------ khung chung
def badge(b, dom, at=0.0):
    """Badge domain: khoi TO MAU DOMAIN, chu den. Luon cung mot vi tri.

    Phai to mau domain chu khong phai to den chu mau domain: nhieu canh lay
    do ALERT lam diem nhan, neu badge chi la vet mau nho thi bon mang nhin
    gan nhu y nhau va ca he ma mau thanh vo nghia.
    """
    SIZE = 40
    label = dom["label"]
    tw, th = sk.text_size(label, font("grot_black", SIZE))
    box = (MARGIN, 122, MARGIN + tw + 60, 122 + th + 40)

    def fn(base, d, p):
        block(base, box, dom["color"], p=p)
        block_text(base, box, [label], "grot_black", SIZE, INK,
                   p=min(1.0, p * 1.5))
    b.add(fn, dur=0.34, wait=0.0, at=at)


def caption(b, txt, at=0.30):
    """Phu de: dai den full-bleed, chu trang. Vua la phu de vua la dau hieu kenh."""
    if not txt:
        return
    f = font("grot_med", 38)
    lines = sk.wrap(txt, f, CONTENT_W - 30)[:3]
    lh = sk.line_height(f, 1.3)
    h = lh * len(lines) + 56
    y0 = CAPTION_TOP

    def fn(base, d, p):
        slab(base, y0, y0 + h, INK, p=min(1.0, p * 1.7))
        if p > 0.35:
            sk.draw_text(base, lines, f, WHITE, cx=CX, y=y0 + 28, gap=1.3,
                         p=(p - 0.35) / 0.65, reveal="fade")
    b.add(fn, dur=0.55, wait=0.0, at=at)


# ============================================================== CAC LOAI CANH
def sc_title(b, sp, dom):
    """Tieu de: dai mau full-bleed + chu cuc lon de len."""
    acc = dom["color"]
    txt = sp["text"]
    f, lines = big_lines(txt, CONTENT_W + 20, 560, sp.get("size", 175),
                         min_size=96)
    th = sk.block_metrics(lines, f, 1.06)[1]
    cy = (BAND_TOP + BAND_BOTTOM) / 2 - (90 if sp.get("sub") else 0)
    sy0, sy1 = cy - th / 2 - 58, cy + th / 2 + 58

    def fn_slab(base, d, p):
        slab(base, sy0, sy1, acc, p=p)
    b.add(fn_slab, dur=0.42, wait=0.30)

    def fn_txt(base, d, p):
        sk.draw_text(base, lines, f, INK, cx=CX, gap=1.06, p=p, reveal="fade",
                     vcenter=cy)
    b.add(fn_txt, dur=0.5, wait=0.42)

    if sp.get("sub"):
        def fn_sub(base, d, p):
            text(base, sp["sub"], "grot", 52, INK, p=p, cx=CX,
                 vcenter=sy1 + 86, max_w=CONTENT_W, min_size=38)
        b.add(fn_sub, dur=0.45, wait=0.35)


def sc_bigstat(b, sp, dom):
    """Mot con so / mot cau dap vao mat. Day la diem nhan tuyet doi."""
    acc = dom["color"] if sp.get("color") != "alert" else ALERT
    txt = sp["value"]
    f, lines = big_lines(txt, CONTENT_W - 80, 640, sp.get("size", 250),
                         min_size=110, gap=1.02)
    th = sk.block_metrics(lines, f, 1.02)[1]
    cy = (BAND_TOP + BAND_BOTTOM) / 2 - (105 if sp.get("sub") else 0)
    box = (MARGIN, cy - th / 2 - 78, W - MARGIN, cy + th / 2 + 78)

    def fn_box(base, d, p):
        block(base, box, acc, p=p)
    b.add(fn_box, dur=0.4, wait=0.32)

    def fn_txt(base, d, p):
        sk.draw_text(base, lines, f, INK, cx=CX, gap=1.02, p=p, reveal="fade",
                     vcenter=cy)
    b.add(fn_txt, dur=0.5, wait=0.42)

    if sp.get("sub"):
        def fn_sub(base, d, p):
            text(base, sp["sub"], "grot_black", 60, INK, p=p, cx=CX,
                 vcenter=box[3] + 90, max_w=CONTENT_W, min_size=40)
        b.add(fn_sub, dur=0.45, wait=0.35)


def sc_compare(b, sp, dom):
    """Hai khoi gia tri xep doc. Khoi thu hai (cai sai) la diem nhan."""
    acc = dom["color"]
    items = sp["items"][:2]
    # mac dinh: khoi nao co cross/focus thi la diem nhan, khong thi lay khoi 2
    focus = next((i for i, it in enumerate(items)
                  if it.get("focus") or it.get("cross")), len(items) - 1)
    bh = 300
    gap = 150
    y0 = BAND_TOP + 60
    boxes = []
    for i, it in enumerate(items):
        by = y0 + i * (bh + gap)
        box = (MARGIN, by, W - MARGIN, by + bh)
        boxes.append(box)
        is_focus = (i == focus)
        fill = (ALERT if it.get("cross") else acc) if is_focus else WHITE
        lab_col = INK if is_focus else MUTED
        val_col = INK if is_focus else MUTED

        def fn(base, d, p, box=box, fill=fill, it=it, i=i, lab_col=lab_col,
               val_col=val_col, is_focus=is_focus):
            block(base, box, fill, p=p, shadow=is_focus)
            if p > 0.30:
                q = (p - 0.30) / 0.70
                text(base, it["label"], "grot_black", 38, lab_col, p=q,
                     cx=CX, vcenter=box[1] - 46)
                block_text(base, box, it["value"], "slab_black", 168, val_col,
                           p=q)
        b.add(fn, dur=0.5, wait=0.42)

        if it.get("cross"):
            def fn_x(base, d, p, box=box, fill=fill):
                cross_out(base, (box[2] - 168, box[1] + 62,
                                 box[2] - 56, box[3] - 62), p,
                          color=INK if fill == ALERT else ALERT)
            b.add(fn_x, dur=0.35, wait=0.28)

    if sp.get("arrow"):
        a = sp["arrow"]

        def fn_a(base, d, p):
            chunky_arrow(base, (CX, boxes[0][3] + 26), (CX, boxes[1][1] - 26),
                         INK, p)
            if p > 0.55 and a.get("label"):
                text(base, a["label"], "grot", 34, MUTED, p=(p - 0.55) / 0.45,
                     x=CX + 42, vcenter=(boxes[0][3] + boxes[1][1]) / 2,
                     align="left")
        b.add(fn_a, dur=0.45, wait=0.32)

    if sp.get("verdict"):
        _verdict(b, sp["verdict"], boxes[-1][3] + 62, ALERT)


def sc_flow(b, sp, dom):
    """Chuoi buoc noi bang mui ten day. Buoc cuoi la diem nhan."""
    acc = dom["color"]
    steps = sp["steps"]
    n = len(steps)
    focus = next((i for i, s_ in enumerate(steps) if s_.get("focus")), n - 1)
    reserve = 150 if sp.get("verdict") else 0
    top = BAND_TOP + 30
    bottom = BAND_BOTTOM - reserve
    bh = 186
    gap = max(78, min((bottom - top - bh * n) / max(1, n - 1), 140))
    total = bh * n + gap * (n - 1)
    y = top + (bottom - top - total) / 2

    for i, stp in enumerate(steps):
        by = y + i * (bh + gap)
        box = (MARGIN, by, W - MARGIN, by + bh)
        is_focus = (i == focus)
        fill = (ALERT if stp.get("bad") else acc) if is_focus else WHITE

        def fn(base, d, p, box=box, fill=fill, stp=stp, is_focus=is_focus):
            block(base, box, fill, p=p, shadow=is_focus)
            if p > 0.28:
                block_text(base, box, stp["text"], "slab_black", 88,
                           INK if is_focus else MUTED, p=(p - 0.28) / 0.72)
        b.add(fn, dur=0.46, wait=0.38)

        if i < n - 1:
            nxt = steps[i + 1]

            def fn_a(base, d, p, by=by, lab=nxt.get("arrow_label")):
                chunky_arrow(base, (CX, by + bh + 14), (CX, by + bh + gap - 14),
                             INK, p, width=10, head=30)
                if lab and p > 0.5:
                    text(base, lab, "grot", 32, MUTED, p=(p - 0.5) / 0.5,
                         x=CX + 38, vcenter=by + bh + gap / 2, align="left")
            b.add(fn_a, dur=0.36, wait=0.26)

    if sp.get("verdict"):
        _verdict(b, sp["verdict"], y + total + 54, ALERT)


def sc_timeline(b, sp, dom):
    """Truc thoi gian: thanh day, vung khe ho la diem nhan mau alert."""
    acc = dom["color"]
    y = BAND_TOP + 370
    hgt = 118
    x0, x1 = MARGIN, W - MARGIN

    def fn_axis(base, d, p):
        bar(base, (x0, y, x1, y + hgt), WHITE, p=p)
    b.add(fn_axis, dur=0.42, wait=0.34)

    marks = sp.get("marks", [])
    positions = []
    for i, m in enumerate(marks):
        mx = x0 + (x1 - x0) * float(m["at"])
        positions.append(mx)

        def fn_m(base, d, p, mx=mx, m=m, i=i):
            dd = ImageDraw.Draw(base)
            dd.line([s(mx), s(y - 18), s(mx), s(y + hgt + 18)],
                    fill=INK + (255,), width=s(8))
            if p > 0.35:
                text(base, m["label"], "grot_black", 34, INK,
                     p=(p - 0.35) / 0.65, cx=mx, vcenter=y - 62, max_w=380,
                     min_size=26)
        b.add(fn_m, dur=0.4, wait=0.3)

    g = sp.get("gap")
    if g and len(positions) >= 2:
        gx0 = x0 + (x1 - x0) * float(g["from"])
        gx1 = x0 + (x1 - x0) * float(g["to"])

        def fn_g(base, d, p):
            bar(base, (gx0, y, gx1, y + hgt), ALERT, p=p)
        b.add(fn_g, dur=0.42, wait=0.34)

        if g.get("note"):
            def fn_n(base, d, p):
                text(base, g["note"], "slab_black", 260, ALERT, p=p, cx=CX,
                     vcenter=y - 260, max_w=CONTENT_W, min_size=140)
            b.add(fn_n, dur=0.5, wait=0.38)

        if g.get("label"):
            def fn_l(base, d, p):
                text(base, g["label"], "grot_black", 46, INK, p=p,
                     cx=(gx0 + gx1) / 2, vcenter=y + hgt + 58)
            b.add(fn_l, dur=0.4, wait=0.3)

    if sp.get("intruder"):
        ix = sum(positions[:2]) / 2 if len(positions) >= 2 else CX

        def fn_i(base, d, p):
            chunky_arrow(base, (ix, y + hgt + 260), (ix, y + hgt + 110), INK, p)
            if p > 0.45:
                q = (p - 0.45) / 0.55
                f = font("grot_black", 38)
                tw = sk.text_size(sp["intruder"], f)[0]
                box = (ix - tw / 2 - 34, y + hgt + 268,
                       ix + tw / 2 + 34, y + hgt + 358)
                block(base, box, acc, p=q)
                block_text(base, box, [sp["intruder"]], "grot_black", 38, INK,
                           p=q)
        b.add(fn_i, dur=0.5, wait=0.34)


def sc_sticky(b, sp, dom):
    """Khoi quy tac: dai tieu de mau domain + khoi trang chua noi dung."""
    acc = dom["color"]
    hf = font("slab_black", 74)
    heading = sp["heading"]
    body = sp.get("body", "")
    small = sp.get("small", "")

    bf, blines = sk.fit_lines("grot_black", body, CONTENT_W - 90, 64,
                              min_size=42, gap=1.18) if body else (None, [])
    sfz = font("grot_med", 34)
    slines = sk.wrap(small, sfz, CONTENT_W - 110) if small else []

    hh = sk.text_size(heading, hf)[1] + 56
    bh_ = sk.block_metrics(blines, bf, 1.18)[1] if blines else 0
    sh = sk.line_height(sfz, 1.35) * len(slines) if slines else 0
    inner = bh_ + (34 + sh if sh else 0) + 96
    cy = (BAND_TOP + BAND_BOTTOM) / 2
    top = cy - (hh + inner) / 2

    hbox = (MARGIN, top, W - MARGIN, top + hh)
    bbox = (MARGIN, top + hh, W - MARGIN, top + hh + inner)

    def fn_body(base, d, p):
        block(base, bbox, WHITE, p=p)
    b.add(fn_body, dur=0.42, wait=0.30)

    def fn_head(base, d, p):
        block(base, hbox, acc, p=p, shadow=False)
        block_text(base, hbox, [heading], "slab_black", 74, INK,
                   p=min(1.0, p * 1.5))
    b.add(fn_head, dur=0.42, wait=0.38)

    if blines:
        def fn_b(base, d, p):
            sk.draw_text(base, blines, bf, INK, cx=CX, y=bbox[1] + 48, gap=1.18,
                         p=p, reveal="fade")
        b.add(fn_b, dur=0.5, wait=0.4)

    if slines:
        def fn_s(base, d, p):
            sk.draw_text(base, slines, sfz, MUTED, cx=CX,
                         y=bbox[1] + 48 + bh_ + 34, gap=1.35, p=p,
                         reveal="fade")
        b.add(fn_s, dur=0.45, wait=0.3)


def sc_code(b, sp, dom):
    """Khoi code kieu cua so: thanh tieu de den + than trang, chu mono."""
    acc = dom["color"]
    heading = sp["heading"]
    clines = sp["code"] if isinstance(sp["code"], list) else [sp["code"]]
    cf = font("mono", sp.get("code_size", 54))

    hf = font("grot_black", 40)
    hh = sk.text_size(heading, hf)[1] + 40
    lh = sk.line_height(cf, 1.42)
    ch = lh * len(clines) + 76
    cy = (BAND_TOP + BAND_BOTTOM) / 2 - (70 if sp.get("verdict") else 0)
    top = cy - (hh + ch) / 2
    hbox = (MARGIN, top, W - MARGIN, top + hh)
    cbox = (MARGIN, top + hh, W - MARGIN, top + hh + ch)

    def fn_c(base, d, p):
        block(base, cbox, WHITE, p=p)
    b.add(fn_c, dur=0.42, wait=0.30)

    def fn_h(base, d, p):
        block(base, hbox, INK, p=p, shadow=False)
        block_text(base, hbox, [heading], "grot_black", 40, acc,
                   p=min(1.0, p * 1.5))
    b.add(fn_h, dur=0.4, wait=0.36)

    def fn_t(base, d, p):
        sk.draw_text(base, clines, cf, INK, cx=CX, y=cbox[1] + 38, gap=1.42,
                     p=p, reveal="fade")
    b.add(fn_t, dur=0.5, wait=0.4)

    if sp.get("mark") == "cross":
        def fn_x(base, d, p):
            cross_out(base, (cbox[2] - 168, cbox[1] + 34,
                             cbox[2] - 56, cbox[3] - 34), p)
        b.add(fn_x, dur=0.35, wait=0.28)

    if sp.get("verdict"):
        _verdict(b, sp["verdict"], cbox[3] + 66, ALERT)


def sc_checklist(b, sp, dom):
    """Danh sach: moi dong mot khoi. Dong duoc danh dau focus la diem nhan."""
    acc = dom["color"]
    items = sp["items"]
    n = len(items)
    focus = next((i for i, it in enumerate(items)
                  if isinstance(it, dict) and it.get("focus")), None)
    bh = {1: 300, 2: 260, 3: 210, 4: 176}.get(n, 148)
    gap = 30
    total = bh * n + gap * (n - 1)
    y = (BAND_TOP + BAND_BOTTOM) / 2 - total / 2

    for i, it in enumerate(items):
        txt = it if isinstance(it, str) else it["text"]
        by = y + i * (bh + gap)
        # khoi so khong duoc vuong to bang chieu cao dong, khong thi mot chu so
        # chiem ca mot o khong lo
        nw = min(bh, 148)
        nbox = (MARGIN, by, MARGIN + nw, by + bh)
        tbox = (MARGIN + nw + gap, by, W - MARGIN, by + bh)
        is_focus = (focus == i)

        def fn(base, d, p, i=i, nbox=nbox, tbox=tbox, txt=txt,
               is_focus=is_focus):
            block(base, nbox, acc if (is_focus or focus is None) else WHITE,
                  p=p, shadow=False)
            block_text(base, nbox, [str(i + 1)], "slab_black", 120, INK,
                       p=min(1.0, p * 1.4))
            block(base, tbox, ALERT if is_focus else WHITE, p=p,
                  shadow=is_focus)
            if p > 0.28:
                block_text(base, tbox, txt, "grot_black",
                           {1: 72, 2: 66, 3: 58, 4: 50}.get(n, 42),
                           INK if (is_focus or focus is None) else MUTED,
                           p=(p - 0.28) / 0.72, min_size=30)
        b.add(fn, dur=0.46, wait=0.36)


def sc_figures(b, sp, dom):
    """Ty le nguoi: day o vuong. So o duoc to la diem nhan."""
    acc = dom["color"]
    n = sp.get("count", 10)
    lit = sp.get("lit", n)
    cols = min(n, 5)
    rows = (n + cols - 1) // cols
    cell = min(168, (CONTENT_W - (cols - 1) * 22) / cols)
    gapx = 22
    gw = cell * cols + gapx * (cols - 1)
    gh = cell * rows + gapx * (rows - 1)
    ox = CX - gw / 2
    oy = (BAND_TOP + BAND_BOTTOM) / 2 - gh / 2 - (80 if sp.get("label") else 0)

    def fn(base, d, p):
        for i in range(n):
            q = clamp((p - i / n * 0.7) * 3.0)
            if q <= 0:
                continue
            r, c = divmod(i, cols)
            bx = ox + c * (cell + gapx)
            by = oy + r * (cell + gapx)
            block(base, (bx, by, bx + cell, by + cell),
                  acc if i < lit else WHITE, p=q, shadow=False)
    b.add(fn, dur=0.9, wait=0.6)

    if sp.get("label"):
        _verdict(b, sp["label"], oy + gh + 82, ALERT)


def sc_qa(b, sp, dom):
    """Cau hoi lon: khoi den, chu mau domain. Dung cho hook phong van."""
    acc = dom["color"]
    txt = sp["text"]
    f, lines = big_lines(txt, CONTENT_W - 90, 600, sp.get("size", 170),
                         min_size=100)
    th = sk.block_metrics(lines, f, 1.06)[1]
    cy = (BAND_TOP + BAND_BOTTOM) / 2
    box = (MARGIN, cy - th / 2 - 88, W - MARGIN, cy + th / 2 + 88)

    def fn_box(base, d, p):
        block(base, box, INK, p=p)
    b.add(fn_box, dur=0.42, wait=0.34)

    def fn_txt(base, d, p):
        sk.draw_text(base, lines, f, acc, cx=CX, gap=1.06, p=p, reveal="fade",
                     vcenter=cy)
    b.add(fn_txt, dur=0.55, wait=0.45)


def sc_decay(b, sp, dom):
    """Gia tri cu ton lai qua thoi gian: khoi alert + cac moc thoi gian."""
    bw, bh = CONTENT_W - 200, 240
    bx0 = CX - bw / 2
    by0 = BAND_TOP + 40
    box = (bx0, by0, bx0 + bw, by0 + bh)

    def fn_box(base, d, p):
        block(base, box, ALERT, p=p)
        if p > 0.3:
            q = (p - 0.3) / 0.7
            text(base, sp.get("label", "CACHE"), "grot_black", 34, INK, p=q,
                 cx=CX, vcenter=by0 - 42)
            block_text(base, box, sp["value"], "slab_black", 138, INK, p=q)
    b.add(fn_box, dur=0.5, wait=0.42)

    stops = sp.get("stops", [])
    if stops:
        sw = (CONTENT_W - (len(stops) - 1) * 20) / len(stops)
        sy = by0 + bh + 96
        for i, stp in enumerate(stops):
            sx = MARGIN + i * (sw + 20)

            def fn_s(base, d, p, sx=sx, stp=stp):
                sbox = (sx, sy, sx + sw, sy + 108)
                block(base, sbox, WHITE, p=p, shadow=False)
                block_text(base, sbox, [stp], "grot_black", 38, MUTED,
                           p=min(1.0, p * 1.4), min_size=26)
            b.add(fn_s, dur=0.35, wait=0.24)

    if sp.get("verdict"):
        _verdict(b, sp["verdict"], by0 + bh + 96 + 108 + 76, ALERT)


def sc_race(b, sp, dom):
    """MO PHONG hai luong chay song song, dan vao nhau theo thoi gian.

    Day la scene quan trong nhat cua cong thuc "hien truong vu an": nhip 4 phai
    CHO THAY co che chu khong ke lai. Mot dau doc quet tu trai sang phai; moi
    buoc sang len khi dau doc di qua. Nguoi xem tu thay hai luong xen ke.

    Toan bo canh la MOT phan tu, vi `p` cua no chinh la truc thoi gian mo phong.
    """
    acc = dom["color"]
    lanes = sp["lanes"][:3]
    x0, x1 = MARGIN, W - MARGIN
    lane_h = 152
    lane_gap = 38
    label_h = 60          # phai cao hon co chu, khong thi nhan de len duong ray
    total = len(lanes) * (lane_h + label_h) + (len(lanes) - 1) * lane_gap
    top = BAND_TOP + 60
    coll = sp.get("collision")

    def fn(base, d, p):
        head = x0 + (x1 - x0) * clamp(p)
        dd = ImageDraw.Draw(base)
        geom = []

        # Luot 1: duong ray + phan da to cua tung buoc
        for li, lane in enumerate(lanes):
            ly = top + li * (lane_h + label_h + lane_gap)
            by = ly + label_h
            lcol = color_of(lane.get("color"), acc)
            geom.append((lane, ly, by, lcol))
            dd.rectangle([s(x0), s(by), s(x1), s(by + lane_h)],
                         fill=WHITE + (255,), outline=INK + (255,),
                         width=s(BORDER - 2))
            for step in lane.get("steps", []):
                sx = x0 + (x1 - x0) * float(step["at"])
                sw = (x1 - x0) * float(step.get("w", 0.18))
                if head < sx:
                    continue
                grow = clamp((head - sx) / max(sw, 1e-6))
                fill = ALERT if step.get("bad") else lcol
                dd.rectangle([s(sx), s(by + 8), s(sx + sw * grow),
                              s(by + lane_h - 8)], fill=fill + (255,),
                             outline=INK + (255,), width=s(BORDER - 2))

        # Luot 2: dau doc. Chi quet qua vung duong ray, KHONG cat ngang nhan lan.
        for _, _, by, _ in geom:
            dd.line([s(head), s(by - 10), s(head), s(by + lane_h + 10)],
                    fill=INK + (255,), width=s(7))

        # Luot 3: chu. Luon nam tren cung, khong bi dau doc cat qua.
        for lane, ly, by, _ in geom:
            text(base, lane["label"], "grot_black", 34, INK, p=1.0, x=x0,
                 vcenter=ly + label_h / 2, align="left")
            for step in lane.get("steps", []):
                sx = x0 + (x1 - x0) * float(step["at"])
                sw = (x1 - x0) * float(step.get("w", 0.18))
                if head < sx:
                    continue
                grow = clamp((head - sx) / max(sw, 1e-6))
                # chi hien khi khoi da to gan xong, khong thi chu tran ra
                # ngoai phan da to trong nhu loi
                if grow >= 0.97:
                    block_text(base, (sx, by, sx + sw, by + lane_h),
                               step["text"], "grot_black", 34, INK, p=1.0,
                               min_size=22)

        if coll and p >= float(coll["at"]):
            q = clamp((p - float(coll["at"])) / 0.12)
            cy = top + total + 96
            f = font("slab_black", 76)
            tw = sk.text_size(coll["label"], f)[0]
            cbox = (max(MARGIN, CX - tw / 2 - 44), cy,
                    min(W - MARGIN, CX + tw / 2 + 44), cy + 132)
            block(base, cbox, ALERT, p=q)
            block_text(base, cbox, coll["label"], "slab_black", 76, INK, p=q,
                       min_size=44)
    # mot phan tu duy nhat, keo dai gan het canh -> p chinh la truc thoi gian
    b.add(fn, dur=max(1.6, b.dur * 0.72), wait=b.dur)


def color_of(name, fallback):
    if not name:
        return fallback
    named = {"blue": (96, 165, 250), "green": (74, 222, 128),
             "amber": (255, 212, 0), "purple": (192, 132, 252),
             "alert": ALERT, "white": WHITE}
    return named.get(name, fallback)


def _verdict(b, txt, y, col, size=92, wait=0.36):
    """Cau ket: chu cuc dam, tu keo len neu sap tran vao dai phu de."""
    f, lines = sk.fit_lines("slab_black", txt, CONTENT_W, size, min_size=54,
                            gap=1.06)
    h = sk.block_metrics(lines, f, 1.06)[1]
    if y + h > CAPTION_TOP - 34:
        y = CAPTION_TOP - 34 - h

    def fn(base, d, p):
        sk.draw_text(base, lines, f, col, cx=CX, y=y, gap=1.06, p=p,
                     reveal="fade")
    b.add(fn, dur=0.5, wait=wait)


BUILDERS = {
    "title": sc_title, "bigstat": sc_bigstat, "compare": sc_compare,
    "flow": sc_flow, "timeline": sc_timeline, "sticky": sc_sticky,
    "code": sc_code, "checklist": sc_checklist, "figures": sc_figures,
    "qa": sc_qa, "decay": sc_decay,
    # --- mo phong
    "race": sc_race,
}


def build(sp, dur, doc=None):
    kind = sp.get("scene")
    if kind not in BUILDERS:
        raise ValueError(f"theme brutalist khong co loai canh {kind!r}. "
                         f"Co: {', '.join(sorted(BUILDERS))}")
    dom = domain(sp, (doc or {}).get("domain"))
    b = B(dur)
    badge(b, dom)
    BUILDERS[kind](b, sp, dom)
    b.finish()
    caption(b, sp.get("caption"), at=0.28)
    return b.els
