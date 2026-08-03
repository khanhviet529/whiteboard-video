"""Cac loai canh. Moi loai tu lo bo cuc cho khung doc 1080x1920.

Mo hinh dong: mot canh = danh sach (t_bat_dau, thoi_luong, ham_ve).
ham_ve(base, draw, p) voi p in [0,1] la tien do rieng cua phan tu do.

Builder `B` xep phan tu tuan tu: moi phan tu bat dau sau phan tu truoc mot
khoang `wait`. Cuoi cung neu tong vuot qua thoi luong canh thi TU DONG co lai
cho vua -> khong bao gio bi tran ra ngoai.
"""
import random

from PIL import Image, ImageDraw

import sketch as sk
import style as st
from style import (BAND_CAPTION, BAND_STAGE, BAND_TITLE, DOT, GREY, GREY_DARK,
                   H, HIGHLIGHT, INK, PAPER, SAFE_X, STICKY_TONES, W, color,
                   font, s)

CX = W // 2
STAGE_Y0, STAGE_Y1 = BAND_STAGE
STAGE_MID = (STAGE_Y0 + STAGE_Y1) // 2
CONTENT_W = W - SAFE_X * 2


# ------------------------------------------------------------------- nen giay
_bg = None


def background():
    """Nen giay kem + luoi cham + toi nhe 4 goc. Render mot lan roi cache."""
    global _bg
    if _bg is not None:
        return _bg
    img = Image.new("RGBA", (s(W), s(H)), PAPER + (255,))
    d = ImageDraw.Draw(img)
    step = 26
    r = max(1, s(1.6))
    for y in range(step, H, step):
        for x in range(step, W, step):
            cxp, cyp = s(x), s(y)
            d.ellipse([cxp - r, cyp - r, cxp + r, cyp + r], fill=DOT + (255,))
    # vignette: to mo dan o vien cho giong anh chup so tay
    vig = Image.new("L", (s(W), s(H)), 0)
    vd = ImageDraw.Draw(vig)
    layers = 26
    for i in range(layers):
        a = int(9 * (1 - i / layers))
        m = int(i * s(7))
        vd.rectangle([m, m, s(W) - m, s(H) - m], outline=a, width=s(8))
    img.alpha_composite(Image.merge("RGBA", (
        Image.new("L", vig.size, 120), Image.new("L", vig.size, 118),
        Image.new("L", vig.size, 108), vig)))
    _bg = img
    return img


from timing import B  # noqa: E402  (bo dem nhip dung chung moi theme)

FADE = 0.30  # theme nay xoa bang bang cach mo dan ve nen


# ------------------------------------------------------------------- tien ich
def caption(b, text, at=0.0):
    """Phu de thuyet minh o day duoi."""
    if not text:
        return
    f = font("body", 36)
    lines = sk.wrap(text, f, CONTENT_W - 40)[:3]
    y0 = BAND_CAPTION[0]

    def fn(base, d, p):
        sk.draw_text(base, lines, f, GREY_DARK, cx=CX, y=y0, p=p, reveal="fade")

    b.add(fn, dur=0.6, wait=0.0, at=at)


def chips(b, items, at=0.05):
    """Day nhan tien do o goc tren phai (giong badge trong video tham chieu)."""
    if not items:
        return
    f = font("body", 30)
    boxes = []
    x = W - SAFE_X
    for it in reversed(items):
        label = it["label"] if isinstance(it, dict) else str(it)
        done = bool(it.get("done")) if isinstance(it, dict) else False
        col = color(it.get("color", "blue")) if isinstance(it, dict) else color("blue")
        tw, th = sk.text_size(label, f)
        w = tw + 40
        boxes.append((x - w, 92, x, 92 + th + 26, label, done, col, f))
        x -= w + 16

    def fn(base, d, p):
        for i, (x0, y0, x1, y1, label, done, col, f_) in enumerate(boxes):
            sk.rect(d, (x0, y0, x1, y1), col, 3, 1.8, 300 + i, 1.0, )
            sk.draw_text(base, [label], f_, col, cx=(x0 + x1) / 2, y=y0 + 11, p=1.0,
                         reveal="fade")
            if done:
                sk.check(d, (x1 - 14, y0 - 2), color("green"), 26, 5, 400 + i, p)
    b.add(fn, dur=0.45, wait=0.0, at=at)


def value_box(b, box, label, value, vcolor, seed, label_col=GREY_DARK,
              box_col=INK, vsize=78, wait=0.34):
    """Hop co nhan phia tren va gia tri lon ben trong (DATABASE / CACHE)."""
    x0, y0, x1, y1 = box
    lf = font("body", 32)
    vf = font("display", vsize)

    def fn(base, d, p):
        sk.rect(d, (x0, y0, x1, y1), box_col, 4, 2.4, seed, min(1.0, p * 1.6))
        if p > 0.35:
            sk.draw_text(base, [label], lf, label_col, cx=(x0 + x1) / 2,
                         y=y0 - 46, p=(p - 0.35) / 0.35, reveal="fade")
        if p > 0.55:
            sk.draw_text(base, [value], vf, color(vcolor), cx=(x0 + x1) / 2,
                         vcenter=(y0 + y1) / 2, p=(p - 0.55) / 0.45)
    return b.add(fn, dur=0.8, wait=wait)


def verdict(b, text, y, col="red", size=76, wait=0.35):
    """Cau ket cua canh. Tu co cho vua mot dong, neo theo DINH tai y.

    Co chot an toan: neu canh qua day thi keo cau ket len, khong bao gio
    de no tran xuong dai phu de.
    """
    f, lines = sk.fit_lines("display_bold", text, CONTENT_W, size, min_size=52)
    h = sk.block_metrics(lines, f)[1]
    max_bottom = BAND_CAPTION[0] - 40
    if y + h > max_bottom:
        y = max_bottom - h

    def fn(base, d, p):
        sk.draw_text(base, lines, f, color(col), cx=CX, y=y, p=p)
    b.add(fn, dur=0.7, wait=wait)
    return h


# =============================================================== CAC LOAI CANH
def scene_title(b, sp):
    f, lines = sk.fit_lines("display", sp["text"], CONTENT_W,
                            sp.get("size", 82), min_size=56)
    total = sk.block_metrics(lines, f)[1]
    y = STAGE_MID - total / 2 - (70 if sp.get("sub") else 0)
    col = color(sp.get("color", "ink"))

    def fn(base, d, p):
        sk.draw_text(base, lines, f, col, cx=CX, y=y, p=p)
    b.add(fn, dur=0.9, wait=0.55)

    if sp.get("underline"):
        uy = y + total + 18
        ucol = color(sp.get("underline_color", sp.get("color", "green")))

        def fn_u(base, d, p):
            sk.line(d, (CX - 300, uy), (CX + 300, uy), ucol, 7, 2.6, 12, p)
        b.add(fn_u, dur=0.45, wait=0.3)

    if sp.get("strike"):
        wmax = max(sk.text_size(l, f)[0] for l in lines)

        def fn_s(base, d, p):
            sk.strike(d, (CX - wmax / 2 - 20, y + 10, CX + wmax / 2 + 20,
                          y + total - 10), color("red"), 10, 21, p)
        b.add(fn_s, dur=0.4, wait=0.3)

    if sp.get("sub"):
        sf = font("body", 44)
        slines = sk.wrap(sp["sub"], sf, CONTENT_W - 60)
        sy = y + total + (70 if sp.get("underline") else 44)

        def fn2(base, d, p):
            sk.draw_text(base, slines, sf, color(sp.get("sub_color", "grey_dark")),
                         cx=CX, y=sy, p=p, reveal="fade")
        b.add(fn2, dur=0.6, wait=0.3)


def scene_bigstat(b, sp):
    txt = sp["value"]
    f, lines = sk.fit_lines("display_bold", txt, CONTENT_W,
                            sp.get("size", 150), min_size=64)
    total = sk.block_metrics(lines, f)[1]
    cy = STAGE_MID - (90 if sp.get("sub") else 0)
    col = color(sp.get("color", "red"))

    def fn(base, d, p):
        sk.draw_text(base, lines, f, col, cx=CX, vcenter=cy, p=p)
    b.add(fn, dur=0.8, wait=0.5)

    if sp.get("circle"):
        wmax = max(sk.text_size(l, f)[0] for l in lines)
        rx, ry = wmax * 0.62, total * 0.85

        def fn_c(base, d, p):
            sk.ellipse(d, (CX - rx, cy - ry, CX + rx, cy + ry), col, 7, 3.0,
                       33, p)
        b.add(fn_c, dur=0.55, wait=0.35)

    if sp.get("sub"):
        sf, slines = sk.fit_lines("display", sp["sub"], CONTENT_W - 40, 58,
                                  min_size=42)

        def fn2(base, d, p):
            sk.draw_text(base, slines, sf, color(sp.get("sub_color", "ink")),
                         cx=CX, vcenter=cy + total / 2 + 90, p=p)
        b.add(fn2, dur=0.7, wait=0.35)


def scene_compare(b, sp):
    """Hai hop xep doc, co nhan + gia tri. Tuy chon mui ten va ket luan."""
    items = sp["items"][:2]
    bw = CONTENT_W - 100
    bh = 210
    gap = 190
    y0 = STAGE_Y0 + 95     # neo tu tren xuong, chua cho nhan phia tren hop
    boxes = []
    for i, it in enumerate(items):
        by = y0 + i * (bh + gap)
        box = (CX - bw / 2, by, CX + bw / 2, by + bh)
        boxes.append(box)
        value_box(b, box, it["label"], it["value"], it.get("color", "ink"),
                  seed=50 + i * 11, vsize=it.get("size", 82))
        if it.get("cross"):
            def fn_x(base, d, p, box=box):
                cx2 = box[2] - 30
                cy2 = (box[1] + box[3]) / 2
                sk.cross(d, (cx2 - 34, cy2 - 34, cx2 + 34, cy2 + 34),
                         color("red"), 8, 77, p)
            b.add(fn_x, dur=0.4, wait=0.3)
        if it.get("note"):
            nf = font("mono", 28)

            def fn_n(base, d, p, box=box, note=it["note"]):
                sk.draw_text(base, [note], nf, color("red"), cx=(box[0] + box[2]) / 2,
                             y=box[3] + 16, p=p, reveal="fade")
            b.add(fn_n, dur=0.5, wait=0.3)

    if sp.get("arrow"):
        a = sp["arrow"]
        y_mid_top = boxes[0][3]
        y_mid_bot = boxes[1][1]

        def fn_a(base, d, p):
            sk.arrow(d, (CX, y_mid_top + 22), (CX, y_mid_bot - 22),
                     color(a.get("color", "purple")), 5, 2.2, 88, p, head=26)
        b.add(fn_a, dur=0.55, wait=0.3)
        if a.get("label"):
            af = font("body", 34)

            def fn_al(base, d, p):
                sk.draw_text(base, [a["label"]], af, color(a.get("color", "purple")),
                             cx=CX, y=(y_mid_top + y_mid_bot) / 2 - 52, p=p,
                             reveal="fade")
            b.add(fn_al, dur=0.5, wait=0.3)

    if sp.get("verdict"):
        verdict(b, sp["verdict"], boxes[1][3] + 90,
                sp.get("verdict_color", "red"), 82)


def scene_timeline(b, sp):
    """Truc thoi gian ngang: cac moc + vung khe ho gach cheo + ghi chu.

    Bo cuc doc: so lon o TREN, nhan moc sat truc, ke chen ngang o DUOI.
    Ba thu nay tung tranh cho nhau nen phai tach han ba tang.
    """
    y = STAGE_Y0 + 400
    x0, x1 = SAFE_X + 40, W - SAFE_X - 40

    def fn_axis(base, d, p):
        sk.line(d, (x0, y), (x1, y), INK, 5, 2.0, 101, p)
    b.add(fn_axis, dur=0.6, wait=0.4)

    marks = sp.get("marks", [])
    mf = font("body", 34)
    positions = []
    for i, m in enumerate(marks):
        mx = x0 + (x1 - x0) * float(m["at"])
        positions.append(mx)
        col = color(m.get("color", "ink"))

        def fn_m(base, d, p, mx=mx, col=col, m=m, i=i):
            sk.line(d, (mx, y - 34), (mx, y + 34), col, 5, 1.4, 110 + i, p)
            if p > 0.4:
                lines = sk.wrap(m["label"], mf, 300)
                sk.draw_text(base, lines, mf, col, cx=mx,
                             y=y - 44 - sk.line_height(mf) * len(lines),
                             p=(p - 0.4) / 0.6, reveal="fade")
        b.add(fn_m, dur=0.5, wait=0.32)

    g = sp.get("gap")
    if g and len(positions) >= 2:
        gx0 = x0 + (x1 - x0) * float(g["from"])
        gx1 = x0 + (x1 - x0) * float(g["to"])
        gcol = color(g.get("color", "red"))

        def fn_g(base, d, p):
            w = (gx1 - gx0) * st.ease_out(p)
            layer = Image.new("RGBA", (s(w) + 4, s(70) + 4), (0, 0, 0, 0))
            ld = ImageDraw.Draw(layer)
            step = s(16)
            for xx in range(0, int(s(w)) + step, step):
                ld.line([(xx, s(70)), (xx + s(24), 0)], fill=gcol + (95,),
                        width=s(2))
            base.alpha_composite(layer, (s(gx0), s(y - 35)))
            sk.rect(d, (gx0, y - 35, gx0 + w, y + 35), gcol, 3, 1.6, 130,
                    min(1.0, p * 1.4))
        b.add(fn_g, dur=0.6, wait=0.35)

        # tang TREN: con so lon, dat cao hon ca nhan moc
        if g.get("note"):
            nf = font("display_bold", 118)

            def fn_gn(base, d, p):
                sk.draw_text(base, [g["note"]], nf, gcol, cx=(gx0 + gx1) / 2,
                             vcenter=y - 245, p=p)
            b.add(fn_gn, dur=0.6, wait=0.35)

        # sat duoi truc: nhan vung khe ho
        if g.get("label"):
            lf = font("display", 46)

            def fn_gl(base, d, p):
                sk.draw_text(base, [g["label"]], lf, gcol, cx=(gx0 + gx1) / 2,
                             y=y + 56, p=p)
            b.add(fn_gl, dur=0.5, wait=0.3)

    # tang DUOI: request chen ngang, mui ten chi len vung khe ho
    if sp.get("intruder"):
        ix = (x0 + x1) / 2 if not positions else sum(positions[:2]) / 2
        itf = font("body", 36)

        def fn_i(base, d, p):
            sk.arrow(d, (ix, y + 300), (ix, y + 130), color("purple"), 5, 2.0,
                     150, p, head=24)
            if p > 0.5:
                bx = sk.text_size(sp["intruder"], itf)[0] / 2 + 30
                sk.rect(d, (ix - bx, y + 310, ix + bx, y + 400), color("purple"),
                        3, 2.0, 151, (p - 0.5) / 0.5)
                sk.draw_text(base, [sp["intruder"]], itf, color("purple"), cx=ix,
                             vcenter=y + 355, p=(p - 0.5) / 0.5, reveal="fade")
        b.add(fn_i, dur=0.7, wait=0.35)


def scene_sticky(b, sp):
    """Sticky note nghieng nhe: tieu de + than + dong chu nho."""
    tone = STICKY_TONES.get(sp.get("tone", "yellow"), STICKY_TONES["yellow"])
    fill, accent = tone
    hf = font("display", 60)
    bf = font("body", 44)
    sf = font("mono", 28)

    hlines = sk.wrap(sp["heading"], hf, CONTENT_W - 150)
    blines = sk.wrap(sp.get("body", ""), bf, CONTENT_W - 150) if sp.get("body") else []
    slines = sk.wrap(sp.get("small", ""), sf, CONTENT_W - 150) if sp.get("small") else []

    hh = sk.line_height(hf) * len(hlines)
    bh = sk.line_height(bf) * len(blines) if blines else 0
    sh = sk.line_height(sf) * len(slines) if slines else 0
    inner = hh + (24 + bh if bh else 0) + (20 + sh if sh else 0)
    pad = 56
    box_h = inner + pad * 2
    bx0, bx1 = SAFE_X + 20, W - SAFE_X - 20
    by0 = STAGE_MID - box_h / 2
    rot = sp.get("rotate", -1.4)

    def fn_note(base, d, p):
        if p < 0.12:
            return
        sk.fill_rect(base, (bx0, by0, bx1, by0 + box_h), fill + (255,),
                     radius=10, rotate=rot)
    b.add(fn_note, dur=0.35, wait=0.28)

    def fn_h(base, d, p):
        y = by0 + pad
        sk.draw_text(base, hlines, hf, accent, cx=CX, y=y, p=p)
    b.add(fn_h, dur=0.7, wait=0.38)

    if blines:
        def fn_b(base, d, p):
            y = by0 + pad + hh + 24
            sk.draw_text(base, blines, bf, INK, cx=CX, y=y, p=p)
        b.add(fn_b, dur=0.7, wait=0.36)

    if slines:
        def fn_s2(base, d, p):
            y = by0 + pad + hh + (24 + bh if bh else 0) + 20
            sk.draw_text(base, slines, sf, GREY_DARK, cx=CX, y=y, p=p,
                         reveal="fade")
        b.add(fn_s2, dur=0.6, wait=0.3)


def scene_code(b, sp):
    """Tieu de + hop code mono, tuy chon dau X / dau tich."""
    hf, hlines = sk.fit_lines("display", sp["heading"], CONTENT_W, 70,
                              min_size=50)
    hy = STAGE_Y0 + 90
    hh = sk.block_metrics(hlines, hf)[1]

    def fn_h(base, d, p):
        sk.draw_text(base, hlines, hf, color(sp.get("color", "ink")), cx=CX,
                     y=hy, p=p)
    b.add(fn_h, dur=0.8, wait=0.5)

    cf = font("mono", sp.get("code_size", 46))
    clines = sp["code"] if isinstance(sp["code"], list) else [sp["code"]]
    cw = max(sk.text_size(l, cf)[0] for l in clines) + 90
    ch = sk.line_height(cf, 1.5) * len(clines) + 70
    cy = hy + hh + 110
    cx0 = CX - cw / 2

    def fn_c(base, d, p):
        if p < 0.1:
            return
        sk.fill_rect(base, (cx0, cy, cx0 + cw, cy + ch), (255, 255, 255, 255),
                     radius=8, rotate=sp.get("rotate", -0.7))
        sk.draw_text(base, clines, cf, INK, cx=CX, y=cy + 34, gap=1.5,
                     p=min(1.0, p * 1.5))
    b.add(fn_c, dur=0.8, wait=0.42)

    if sp.get("mark") == "cross":
        def fn_x(base, d, p):
            mx = cx0 + cw + 60
            my = cy + ch / 2
            sk.cross(d, (mx - 40, my - 40, mx + 40, my + 40), color("red"), 9,
                     181, p)
        b.add(fn_x, dur=0.45, wait=0.3)
    elif sp.get("mark") == "check":
        def fn_v(base, d, p):
            sk.check(d, (cx0 + cw + 70, cy + ch / 2), color("green"), 60, 9,
                     182, p)
        b.add(fn_v, dur=0.45, wait=0.3)

    if sp.get("verdict"):
        verdict(b, sp["verdict"], cy + ch + 110,
                sp.get("verdict_color", "red"), 80)


def scene_checklist(b, sp):
    """Danh sach co so thu tu, hien lan luot. Tu khoa duoc highlight vang."""
    items = sp["items"]
    # it dong thi chu to len cho day khung, nhieu dong thi nho lai
    tsize = {1: 68, 2: 62, 3: 54}.get(len(items), 48)
    nf = font("display", int(tsize * 0.82))
    tf = font("body", sp.get("size", tsize))
    x_num = SAFE_X + 30
    x_txt = x_num + 74
    maxw = W - SAFE_X - x_txt - 20

    prepared = []
    for it in items:
        txt = it if isinstance(it, str) else it["text"]
        hl = None if isinstance(it, str) else it.get("highlight")
        prepared.append((txt, sk.wrap(txt, tf, maxw), hl))

    lh = sk.line_height(tf)
    heights = [lh * len(l) + 34 for _, l, _ in prepared]
    total = sum(heights)
    y = STAGE_MID - total / 2

    ys = []
    acc = y
    for h_ in heights:
        ys.append(acc)
        acc += h_

    for i, ((txt, lines, hl), yy) in enumerate(zip(prepared, ys)):
        def fn(base, d, p, i=i, lines=lines, yy=yy, hl=hl):
            num = f"{i + 1}."
            sk.draw_text(base, [num], nf, color("grey_dark"), x=x_num, y=yy + 6,
                         align="left", p=min(1.0, p * 2), reveal="fade")
            if hl and p > 0.75:
                # highlight sau tu khoa o dong dau tien co chua no
                for li, ln in enumerate(lines):
                    if hl in ln:
                        pre = ln.split(hl)[0]
                        wpre = sk.text_size(pre, tf)[0]
                        whl = sk.text_size(hl, tf)[0]
                        hy2 = yy + li * lh
                        sk.highlight_behind(base, (x_txt + wpre - 6, hy2 + 8,
                                                   x_txt + wpre + whl + 6,
                                                   hy2 + lh * 0.82),
                                            HIGHLIGHT, 190 + i,
                                            (p - 0.75) / 0.25)
                        break
            sk.draw_text(base, lines, tf, INK, x=x_txt, y=yy, align="left", p=p)
        b.add(fn, dur=0.75, wait=0.42)


def scene_figures(b, sp):
    """Day nguoi que: `lit` nguoi dau mau dam, con lai xam."""
    n = sp.get("count", 10)
    lit = sp.get("lit", n)
    col = color(sp.get("color", "purple"))
    gap = min(100, (CONTENT_W - 20) / n)
    scale = sp.get("scale", min(0.9, gap / 108))
    x0 = CX - gap * (n - 1) / 2
    y = STAGE_MID - 130

    def fn(base, d, p):
        for i in range(n):
            ip = st.clamp((p - i / n * 0.75) * 3.2)
            if ip <= 0:
                continue
            sk.stick_figure(d, (x0 + i * gap, y), col if i < lit else GREY,
                            scale, 200 + i, ip)
    b.add(fn, dur=1.1, wait=0.7)

    if sp.get("label"):
        verdict(b, sp["label"], y + 300 * scale + 90,
                sp.get("label_color", "ink"), 72, wait=0.4)


def scene_qa(b, sp):
    """Nguoi que + bong thoai. Dung cho cau hoi phong van."""
    qf = font("display", sp.get("size", 72))
    lines = sk.wrap(sp["text"], qf, CONTENT_W - 130)
    lh = sk.line_height(qf)
    bh = lh * len(lines) + 76
    by0 = STAGE_Y0 + 60
    bx0, bx1 = SAFE_X + 10, W - SAFE_X - 10

    def fn_b(base, d, p):
        sk.rect(d, (bx0, by0, bx1, by0 + bh), INK, 4, 2.6, 210, p)
        if p > 0.75:
            # duoi bong thoai
            sk.line(d, (bx1 - 150, by0 + bh), (bx1 - 96, by0 + bh + 54), INK, 4,
                    1.6, 211, (p - 0.75) / 0.25)
            sk.line(d, (bx1 - 96, by0 + bh + 54), (bx1 - 104, by0 + bh), INK, 4,
                    1.6, 212, (p - 0.75) / 0.25)
    b.add(fn_b, dur=0.7, wait=0.42)

    def fn_t(base, d, p):
        sk.draw_text(base, lines, qf, color(sp.get("color", "red")), cx=CX,
                     y=by0 + 38, p=p)
    b.add(fn_t, dur=0.85, wait=0.5)

    def fn_f(base, d, p):
        sk.stick_figure(d, (SAFE_X + 120, by0 + bh + 150), INK, 1.15, 220, p)
    b.add(fn_f, dur=0.8, wait=0.4)

    if sp.get("thought"):
        tf = font("body", 40)

        def fn_th(base, d, p):
            tx = SAFE_X + 260
            ty = by0 + bh + 210
            tw = sk.text_size(sp["thought"], tf)[0] + 60
            sk.rect(d, (tx, ty, tx + tw, ty + 86), GREY, 3, 2.0, 230,
                    min(1.0, p * 1.6))
            if p > 0.4:
                sk.draw_text(base, [sp["thought"]], tf, GREY_DARK,
                             cx=tx + tw / 2, y=ty + 22, p=(p - 0.4) / 0.6,
                             reveal="fade")
        b.add(fn_th, dur=0.6, wait=0.35)


def scene_flow(b, sp):
    """Chuoi hop noi bang mui ten (doc). Dung cho luong request -> cache -> db."""
    steps = sp["steps"]
    n = len(steps)
    bw = CONTENT_W - 140
    bh = 125
    # Chua san cho cau ket TRUOC roi moi chia deu phan con lai cho cac hop.
    # Neo theo dai phu de chu khong theo STAGE_Y1, vi cau ket phai nam gon
    # giua hop cuoi va phu de.
    top = STAGE_Y0 + 50
    bottom = (BAND_CAPTION[0] - 200) if sp.get("verdict") else STAGE_Y1
    gap = (bottom - top - bh * n) / max(1, n - 1)
    gap = max(80, min(gap, 170))
    total = bh * n + gap * (n - 1)
    y = top + (bottom - top - total) / 2

    for i, stp in enumerate(steps):
        by = y + i * (bh + gap)
        col = color(stp.get("color", "ink"))
        tf, lines = sk.fit_lines("display", stp["text"], bw - 70,
                                 stp.get("size", 54), min_size=38)

        def fn(base, d, p, by=by, col=col, tf=tf, lines=lines, i=i):
            sk.rect(d, (CX - bw / 2, by, CX + bw / 2, by + bh), col, 4, 2.4,
                    240 + i, min(1.0, p * 1.5))
            if p > 0.35:
                sk.draw_text(base, lines, tf, col, cx=CX, vcenter=by + bh / 2,
                             p=(p - 0.35) / 0.65)
        b.add(fn, dur=0.7, wait=0.36)

        if i < n - 1:
            nxt = steps[i + 1]
            acol = color(nxt.get("arrow_color", "purple"))
            alab = nxt.get("arrow_label")

            def fn_a(base, d, p, by=by, acol=acol, alab=alab, i=i):
                sk.arrow(d, (CX, by + bh + 14), (CX, by + bh + gap - 14), acol,
                         5, 2.0, 250 + i, p, head=24)
                if alab and p > 0.5:
                    af = font("body", 32)
                    sk.draw_text(base, [alab], af, acol, x=CX + 30,
                                 y=by + bh + gap / 2 - 24, align="left",
                                 p=(p - 0.5) / 0.5, reveal="fade")
            b.add(fn_a, dur=0.5, wait=0.3)

    if sp.get("verdict"):
        verdict(b, sp["verdict"], y + total + 45,
                sp.get("verdict_color", "red"), 78)


def scene_decay(b, sp):
    """Hop cache giu gia cu + truc thoi gian keo dai (1 gio / 1 ngay / 1 tuan)."""
    bw, bh = 440, 190
    bx0 = CX - bw / 2
    by0 = STAGE_Y0 + 80
    value_box(b, (bx0, by0, bx0 + bw, by0 + bh), sp.get("label", "CACHE"),
              sp["value"], sp.get("color", "red"), seed=260, vsize=84)

    y = by0 + bh + 170
    x0, x1 = SAFE_X + 50, W - SAFE_X - 50
    stops = sp.get("stops", [])
    tf = font("body", 36)

    def fn_axis(base, d, p):
        sk.line(d, (x0, y), (x1, y), GREY, 4, 1.8, 270, p)
    b.add(fn_axis, dur=0.5, wait=0.35)

    for i, stop in enumerate(stops):
        sx = x0 + (x1 - x0) * (i + 1) / (len(stops) + 0.4)

        def fn_s(base, d, p, sx=sx, stop=stop, i=i):
            sk.line(d, (sx, y - 22), (sx, y + 22), GREY, 4, 1.2, 271 + i, p)
            if p > 0.35:
                sk.draw_text(base, [stop], tf, GREY_DARK, cx=sx, y=y + 34,
                             p=(p - 0.35) / 0.65, reveal="fade")
        b.add(fn_s, dur=0.45, wait=0.3)

    if sp.get("verdict"):
        verdict(b, sp["verdict"], y + 140, sp.get("verdict_color", "pink"), 76,
                wait=0.4)

    if sp.get("customer"):
        cf = font("body", 40)

        def fn_c(base, d, p):
            fx = W - SAFE_X - 130
            fy = y + 310
            sk.stick_figure(d, (fx, fy), color("pink"), 0.95, 280, p, arm_up=True)
            if p > 0.45:
                txt = sp["customer"]
                tw = sk.text_size(txt, cf)[0] + 54
                sk.rect(d, (fx - tw - 70, fy + 60, fx - 70, fy + 148),
                        color("pink"), 3, 2.2, 281, (p - 0.45) / 0.55)
                sk.draw_text(base, [txt], cf, color("pink"),
                             cx=fx - tw / 2 - 70, y=fy + 86,
                             p=(p - 0.45) / 0.55, reveal="fade")
        b.add(fn_c, dur=0.8, wait=0.4)


BUILDERS = {
    "title": scene_title,
    "bigstat": scene_bigstat,
    "compare": scene_compare,
    "timeline": scene_timeline,
    "sticky": scene_sticky,
    "code": scene_code,
    "checklist": scene_checklist,
    "figures": scene_figures,
    "qa": scene_qa,
    "flow": scene_flow,
    "decay": scene_decay,
}


def build(sp, dur, doc=None):
    kind = sp.get("scene")
    if kind not in BUILDERS:
        raise ValueError(f"khong biet loai canh: {kind!r}. "
                         f"Cac loai co: {', '.join(sorted(BUILDERS))}")
    b = B(dur)
    chips(b, sp.get("chips"))
    BUILDERS[kind](b, sp)
    b.finish()
    # Phu de them SAU khi chuan hoa nhip: no phai hien ngay tu dau cung giong
    # doc, khong duoc bi keo gian theo cac net ve.
    caption(b, sp.get("caption"), at=0.30)
    return b.els
