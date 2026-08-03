"""Primitive ve tay: net xieu xieu, ve dan theo tien do, chu hien dan.

Moi ham nhan TOA DO LOGIC (he 1080x1920) va tu nhan supersample ben trong.

Nguyen tac quan trong: nhieu (jitter) phai TIEN DINH. Neu sinh lai ngau nhien
moi frame thi hinh se rung. Vi vay moi hinh co mot `seed` va diem duoc cache.
"""
import math
import random

from PIL import Image, ImageDraw

from style import SS, s, clamp, ease_out

_pts_cache = {}


# --------------------------------------------------------------- nhieu net ve
def _jitter_pts(x0, y0, x1, y1, amp, seed, segs=None):
    """Chuoi diem tu (x0,y0) den (x1,y1) voi do xieu `amp`, tien dinh theo seed."""
    key = ("l", x0, y0, x1, y1, amp, seed, segs)
    if key in _pts_cache:
        return _pts_cache[key]
    d = math.hypot(x1 - x0, y1 - y0)
    n = segs or max(2, int(d / 22))
    rng = random.Random(seed)
    # lech lon nhat o giua, hai dau gan nhu dinh vi dung -> giong net but that
    pts = []
    for i in range(n + 1):
        t = i / n
        bow = math.sin(math.pi * t)
        ox = rng.uniform(-amp, amp) * bow
        oy = rng.uniform(-amp, amp) * bow
        pts.append((x0 + (x1 - x0) * t + ox, y0 + (y1 - y0) * t + oy))
    _pts_cache[key] = pts
    return pts


def _ellipse_pts(cx, cy, rx, ry, amp, seed, segs=64, start=-0.5 * math.pi,
                 sweep=2 * math.pi):
    key = ("e", cx, cy, rx, ry, amp, seed, segs, round(start, 4), round(sweep, 4))
    if key in _pts_cache:
        return _pts_cache[key]
    rng = random.Random(seed)
    pts = []
    for i in range(segs + 1):
        t = i / segs
        a = start + sweep * t
        # bien do nhieu doi cham theo goc -> vong tron meo tu nhien
        wob = 1 + 0.035 * math.sin(a * 3 + seed % 7)
        ox = rng.uniform(-amp, amp)
        oy = rng.uniform(-amp, amp)
        pts.append((cx + math.cos(a) * rx * wob + ox,
                    cy + math.sin(a) * ry * wob + oy))
    _pts_cache[key] = pts
    return pts


def _partial(pts, p):
    """Cat chuoi diem con `p` phan do dai (0..1) -> hieu ung dang duoc ve."""
    p = clamp(p)
    if p >= 1.0:
        return pts
    if p <= 0.0:
        return []
    seglen = [math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1])
              for i in range(len(pts) - 1)]
    total = sum(seglen)
    if total <= 0:
        return pts
    want = total * p
    out = [pts[0]]
    acc = 0.0
    for i, L in enumerate(seglen):
        if acc + L >= want:
            r = (want - acc) / L if L else 0
            x = pts[i][0] + (pts[i + 1][0] - pts[i][0]) * r
            y = pts[i][1] + (pts[i + 1][1] - pts[i][1]) * r
            out.append((x, y))
            break
        acc += L
        out.append(pts[i + 1])
    return out


def _poly(d, pts, color, width):
    if len(pts) < 2:
        return
    d.line([(s(x), s(y)) for x, y in pts], fill=color, width=s(width),
           joint="curve")


# ------------------------------------------------------------------ hinh co ban
def line(d, p0, p1, color, width=3, amp=2.0, seed=1, p=1.0, double=False):
    pts = _jitter_pts(p0[0], p0[1], p1[0], p1[1], amp, seed)
    _poly(d, _partial(pts, p), color, width)
    if double:  # ve lai lan hai lech nhe -> giong to but hai luot
        pts2 = _jitter_pts(p0[0] + 1.5, p0[1] + 1.5, p1[0] + 1.5, p1[1] + 1.5,
                           amp, seed + 991)
        _poly(d, _partial(pts2, p), color, max(1, width - 1))


def rect(d, box, color, width=3, amp=2.2, seed=1, p=1.0, radius=0):
    """Khung chu nhat ve tay. Bon canh ve lan luot theo p."""
    x0, y0, x1, y1 = box
    sides = [((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)),
             ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))]
    for i, (a, b) in enumerate(sides):
        lo, hi = i / 4, (i + 1) / 4
        sp = clamp((p - lo) / (hi - lo)) if p < hi else 1.0
        if sp <= 0:
            break
        line(d, a, b, color, width, amp, seed + i * 17, sp)


def fill_rect(base, box, fill, radius=14, rotate=0.0, shadow=True):
    """Hop dac (sticky note, hop code). Ve tren layer rieng de xoay duoc."""
    x0, y0, x1, y1 = box
    w, h = s(x1 - x0), s(y1 - y0)
    pad = s(20)
    layer = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    if shadow:
        ld.rounded_rectangle([pad + s(4), pad + s(5), pad + w + s(4), pad + h + s(5)],
                             radius=s(radius), fill=(0, 0, 0, 26))
    ld.rounded_rectangle([pad, pad, pad + w, pad + h], radius=s(radius), fill=fill)
    if rotate:
        layer = layer.rotate(rotate, expand=True, resample=Image.BICUBIC)
    base.alpha_composite(layer, (s(x0) - pad, s(y0) - pad))


def ellipse(d, box, color, width=3, amp=2.4, seed=1, p=1.0, sweep=1.08):
    """Vong khoanh tay. sweep>1 -> ve qua diem dau mot chut, rat dac trung."""
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    pts = _ellipse_pts(cx, cy, (x1 - x0) / 2, (y1 - y0) / 2, amp, seed,
                       sweep=2 * math.pi * sweep)
    _poly(d, _partial(pts, p), color, width)


def arrow(d, p0, p1, color, width=3, amp=2.0, seed=1, p=1.0, head=22,
          curve=0.0):
    """Mui ten. curve != 0 -> than cong (dung cho luong du lieu)."""
    x0, y0 = p0
    x1, y1 = p1
    if curve:
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy) or 1
        mx -= dy / L * curve
        my += dx / L * curve
        # Bezier bac 2 roi them nhieu
        rng = random.Random(seed)
        pts = []
        for i in range(29):
            t = i / 28
            bx = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * mx + t * t * x1
            by = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * my + t * t * y1
            bow = math.sin(math.pi * t)
            pts.append((bx + rng.uniform(-amp, amp) * bow,
                        by + rng.uniform(-amp, amp) * bow))
        key = ("c", x0, y0, x1, y1, curve, amp, seed)
        pts = _pts_cache.setdefault(key, pts)
    else:
        pts = _jitter_pts(x0, y0, x1, y1, amp, seed)

    shown = _partial(pts, p)
    _poly(d, shown, color, width)
    # dau mui ten chi ve khi than da gan xong
    if p > 0.82 and len(shown) >= 2:
        hp = clamp((p - 0.82) / 0.18)
        ax, ay = shown[-1]
        bx, by = shown[-2] if len(shown) > 1 else shown[-1]
        ang = math.atan2(ay - by, ax - bx)
        for sgn in (+1, -1):
            a2 = ang + math.pi + sgn * 0.42
            hx = ax + math.cos(a2) * head * hp
            hy = ay + math.sin(a2) * head * hp
            line(d, (ax, ay), (hx, hy), color, width, 1.0, seed + 55 + sgn, 1.0)


def cross(d, box, color, width=6, seed=1, p=1.0):
    """Dau X do."""
    x0, y0, x1, y1 = box
    line(d, (x0, y0), (x1, y1), color, width, 1.6, seed, clamp(p * 2))
    if p > 0.5:
        line(d, (x1, y0), (x0, y1), color, width, 1.6, seed + 3, clamp((p - 0.5) * 2))


def check(d, at, color, size=34, width=6, seed=1, p=1.0):
    """Dau tich xanh."""
    x, y = at
    a = (x - size * 0.5, y)
    b = (x - size * 0.12, y + size * 0.42)
    c = (x + size * 0.55, y - size * 0.5)
    line(d, a, b, color, width, 1.2, seed, clamp(p * 2.2))
    if p > 0.45:
        line(d, b, c, color, width, 1.2, seed + 7, clamp((p - 0.45) / 0.55))


def strike(d, box, color, width=8, seed=1, p=1.0):
    """Gach cheo de bo (dung cho '100%' bi gach)."""
    x0, y0, x1, y1 = box
    line(d, (x0, y1), (x1, y0), color, width, 2.0, seed, p)


def stick_figure(d, at, color, scale=1.0, seed=1, p=1.0, arm_up=False):
    """Nguoi que. p ve dan: dau -> than -> tay -> chan."""
    x, y = at            # y = dinh dau
    hr = 26 * scale
    ellipse(d, (x - hr, y, x + hr, y + hr * 2), color, max(2, int(3 * scale)),
            1.6, seed, clamp(p * 3))
    if p <= 0.33:
        return
    p2 = clamp((p - 0.33) / 0.67)
    neck = y + hr * 2
    hip = neck + 62 * scale
    line(d, (x, neck), (x, hip), color, max(2, int(3 * scale)), 1.4, seed + 1,
         clamp(p2 * 2.4))
    if p2 > 0.42:
        p3 = clamp((p2 - 0.42) / 0.58)
        sh = neck + 16 * scale
        if arm_up:
            line(d, (x, sh), (x - 44 * scale, sh - 30 * scale), color,
                 max(2, int(3 * scale)), 1.4, seed + 2, p3)
            line(d, (x, sh), (x + 44 * scale, sh - 34 * scale), color,
                 max(2, int(3 * scale)), 1.4, seed + 3, p3)
        else:
            line(d, (x, sh), (x - 42 * scale, sh + 34 * scale), color,
                 max(2, int(3 * scale)), 1.4, seed + 2, p3)
            line(d, (x, sh), (x + 42 * scale, sh + 34 * scale), color,
                 max(2, int(3 * scale)), 1.4, seed + 3, p3)
        line(d, (x, hip), (x - 34 * scale, hip + 56 * scale), color,
             max(2, int(3 * scale)), 1.4, seed + 4, p3)
        line(d, (x, hip), (x + 34 * scale, hip + 56 * scale), color,
             max(2, int(3 * scale)), 1.4, seed + 5, p3)


# ----------------------------------------------------------------------- chu
_measure_img = Image.new("L", (8, 8))
_measure = ImageDraw.Draw(_measure_img)


def text_size(txt, f):
    """Kich thuoc chu, tra ve theo he LOGIC."""
    if not txt:
        return 0, 0
    b = _measure.textbbox((0, 0), txt, font=f)
    return (b[2] - b[0]) / SS, (b[3] - b[1]) / SS


def wrap(txt, f, max_w):
    """Chia dong theo be rong toi da (he logic)."""
    words = txt.split()
    if not words:
        return []
    lines, cur = [], words[0]
    for w in words[1:]:
        cand = cur + " " + w
        if text_size(cand, f)[0] <= max_w:
            cur = cand
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def wrap_balanced(txt, f, max_w):
    """Ngat dong CAN BANG: cac dong xap xi bang nhau, khong de chu mo coi.

    `wrap` thuong nhoi day dong tren roi de lai mot tu tro troi o dong cuoi
    ("TANG 1 - THU / TU"). Cach sua: tim be rong NHO NHAT ma van ngat ra dung
    so dong nhu cu - be rong nho hon thi cac dong tu dong deu nhau.
    """
    lines = wrap(txt, f, max_w)
    n = len(lines)
    if n <= 1:
        return lines
    lo, hi, best = 1, int(max_w), lines
    while lo < hi:
        mid = (lo + hi) // 2
        cand = wrap(txt, f, mid)
        if len(cand) <= n and all(text_size(l, f)[0] <= max_w for l in cand):
            best, hi = cand, mid
        else:
            lo = mid + 1
    return best


def line_height(f, factor=1.42):
    return text_size("Ăgjqy", f)[1] * factor


def text_metrics(txt, f):
    """(offset_y, cao_thuc) theo he LOGIC khi ve o anchor 'lt'.

    PIL dat DINH KHUNG DONG tai y, con muc chu bat dau thap hon mot chut.
    Muon can giua theo chieu doc thi phai tru phan offset nay, khong thi
    chu se luon bi day len tren.
    """
    if not txt:
        return 0.0, 0.0
    b = _measure.textbbox((0, 0), txt, font=f, anchor="lt")
    return b[1] / SS, (b[3] - b[1]) / SS


def block_metrics(lines, f, gap=1.42):
    """(offset_y_dong_dau, tong_cao_thuc) cua ca khoi nhieu dong."""
    if not lines:
        return 0.0, 0.0
    oy, h = text_metrics(lines[0], f)
    return oy, line_height(f, gap) * (len(lines) - 1) + h


def fit_lines(role, txt, max_w, size, min_size=44, step=4, gap=1.42):
    """Thu thu nho font cho vua MOT dong. Khong vua thi moi ngat dong.

    Nho vay tieu de va cau ket khong bi ngat dong xau roi de len phan tu khac.
    """
    from style import font as _font
    s_ = size
    f = _font(role, s_)
    while s_ > min_size and text_size(txt, f)[0] > max_w:
        s_ -= step
        f = _font(role, s_)
    if text_size(txt, f)[0] <= max_w:
        return f, [txt]
    return f, wrap(txt, f, max_w)


def draw_text(base, lines, f, color, cx=None, x=None, y=0, align="center",
              gap=1.42, p=1.0, reveal="wipe", vcenter=None):
    """Ve khoi chu, hien dan.

    reveal="wipe"  -> tung dong hien dan tu trai sang phai (giong dang viet)
    reveal="fade"  -> mo dan + nhoi len nhe
    vcenter=cy     -> can giua theo chieu doc quanh cy (da tru offset font)
    Tra ve chieu cao da chiem (he logic).
    """
    if isinstance(lines, str):
        lines = [lines]
    lines = [l for l in lines if l is not None]
    if not lines:
        return 0
    lh = line_height(f, gap)
    if vcenter is not None:
        oy, total = block_metrics(lines, f, gap)
        y = vcenter - total / 2 - oy
    n = len(lines)
    for i, txt in enumerate(lines):
        if not txt.strip():
            continue
        # moi dong co cua so hien rieng -> chu chay tuan tu tung dong
        lo, hi = i / n, (i + 1) / n
        lp = 1.0 if p >= hi else clamp((p - lo) / (hi - lo))
        if lp <= 0:
            break
        tw, th = text_size(txt, f)
        if align == "center":
            lx = (cx if cx is not None else 0) - tw / 2
        elif align == "right":
            lx = (x or 0) - tw
        else:
            lx = x or 0
        ly = y + i * lh

        pad = s(26)
        layer = Image.new("RGBA", (s(tw) + pad * 2, s(th) + pad * 2), (0, 0, 0, 0))
        ImageDraw.Draw(layer).text((pad, pad), txt, font=f, fill=color, anchor="lt")

        if reveal == "fade":
            a = ease_out(lp)
            if a < 1.0:
                alpha = layer.getchannel("A").point(lambda v: int(v * a))
                layer.putalpha(alpha)
            rise = int((1 - ease_out(lp)) * s(14))
            base.alpha_composite(layer, (s(lx) - pad, s(ly) - pad + rise))
        else:
            if lp < 1.0:
                cutoff = int(pad + s(tw) * ease_out(lp))
                mask = Image.new("L", layer.size, 0)
                ImageDraw.Draw(mask).rectangle([0, 0, cutoff, layer.size[1]], fill=255)
                layer.putalpha(Image.composite(layer.getchannel("A"), mask, mask))
            base.alpha_composite(layer, (s(lx) - pad, s(ly) - pad))
    return lh * n


def highlight_behind(base, box, fill, seed=1, p=1.0):
    """Vet highlight vang sau chu, lan tu trai sang phai."""
    x0, y0, x1, y1 = box
    w = (x1 - x0) * ease_out(p)
    if w <= 1:
        return
    layer = Image.new("RGBA", (s(w) + s(10), s(y1 - y0) + s(10)), (0, 0, 0, 0))
    ImageDraw.Draw(layer).rounded_rectangle(
        [0, 0, s(w), s(y1 - y0)], radius=s(6), fill=fill + (215,))
    base.alpha_composite(layer, (s(x0), s(y0)))
