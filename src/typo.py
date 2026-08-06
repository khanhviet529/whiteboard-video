"""Chu co tracking, he lo bang mask truot len, vet sang - dung chung cho theme toi.

Truoc day nhung ham nay nam trong `phongtoi.py`. Khi theme `bench` ra doi thi
ca hai theme deu can y nguyen chung, nen tach ra day de chi co MOT ban cai dat.
Khong co gi rieng cua theme nao trong file nay: khong bang mau, khong bo cuc.

PIL khong ho tro letter-spacing nen `ttext` phai ve tung ky tu roi tu day con
tro. Moi ham nhan TOA DO LOGIC (he 1080x1920) va tu nhan supersample ben trong.
"""
import math

from PIL import Image, ImageDraw, ImageFilter

import sketch as sk
from style import SS, clamp, font, s


# --------------------------------------------------------------------- easing
def expo_out(p):
    """Bat dau rat nhanh roi ha rat cham. Nhip cua panel / thanh / man che."""
    p = clamp(p)
    return 1.0 if p >= 1 else 1 - math.pow(2, -10 * p)


def ease_out_cubic(p):
    """Nhip cua CHU. Deu hon expo_out nhieu.

    `expo_out` don 87% chuyen dong vao 30% dau roi keo mot cai duoi rat dai gan
    nhu khong nhin thay. Voi panel thi dep, nhung voi chu thi thanh ra: chu hien
    gan nhu tuc thi, sau do bo len vai pixel rat lau -> mat doc thay mot cu
    "khung". Cubic dai deu hon nen chu vao cho mot mach.
    """
    p = clamp(p)
    return 1 - (1 - p) ** 3


# ------------------------------------------------------------------ vet sang
def glow(base, box, col, radius=70, strength=95):
    """Vet sang toa quanh phan tu tieu diem.

    Blur o 1/4 kich thuoc roi phong lai: nhanh hon blur truc tiep khoang 16 lan
    ma mat thuong khong phan biet duoc voi vet sang mem.
    """
    x0, y0, x1, y1 = box
    pad = radius * 2
    w = int(s(x1 - x0 + pad * 2) / 4)
    h = int(s(y1 - y0 + pad * 2) / 4)
    if w < 4 or h < 4:
        return
    small = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(small).rectangle(
        [int(s(pad) / 4), int(s(pad) / 4), w - int(s(pad) / 4),
         h - int(s(pad) / 4)], fill=col + (strength,))
    small = small.filter(ImageFilter.GaussianBlur(max(1, int(s(radius) / 4))))
    base.alpha_composite(small.resize(
        (int(s(x1 - x0 + pad * 2)), int(s(y1 - y0 + pad * 2))), Image.BILINEAR),
        (int(s(x0 - pad)), int(s(y0 - pad))))


# ----------------------------------------------------------------------- chu
def adv(txt, f):
    """Be rong thuc (advance), khac bbox: bbox cua dau cach la rong."""
    return f.getlength(txt) / s(1)


def track_w(txt, f, track):
    return sum(adv(c, f) for c in txt) + track * max(0, len(txt) - 1)


ANCHOR = "la"   # PHAI trung voi anchor ma ttext() dung khi ve


def tm(txt, f):
    """(offset_y, cao_thuc) he LOGIC - do bang DUNG anchor ma ttext() se ve.

    Khong dung `sk.text_metrics` duoc: no do bang anchor "lt", con `"t"` (top)
    chi hop le voi chu DOC. Voi chu ngang thi PIL tra ve b[1] == 0 mai mai, nen
    offset luon ra 0 va phep tru can giua khong bao gio chay -> moi thu bi dat
    THAP hon dung cho dung bang khoang tu dinh ascender xuong dinh muc (22px voi
    Phudu 72, 15,5px voi BeVietnamPro Black 62). So "02" trong khung ngoac cua
    canh `rule` lech han xuong duoi la vi the.

    `sk.text_metrics` van giu nguyen: theme whiteboard/brutalist do VA ve cung
    bang "lt" nen tu khop voi nhau, sua o do se lam lech hai theme cu.
    """
    if not txt:
        return 0.0, 0.0
    b = sk._measure.textbbox((0, 0), txt, font=f, anchor=ANCHOR)
    return b[1] / SS, (b[3] - b[1]) / SS


def ttext(base, txt, f, fill, y, x=None, cx=None, track=0.0, p=1.0,
          reveal="mask", rise=20):
    """Chu co tracking, he lo bang mask truot len.

    PIL khong ho tro tracking nen phai ve tung ky tu. reveal="mask": chu truot
    len tu duoi trong khi bi cat boi mot cua so co dinh -> giong chu duoc day
    vao cho, muot hon nhieu so voi mo dan.
    """
    if p <= 0 or not txt:
        return 0.0
    total = track_w(txt, f, track)
    oy, th = tm(txt, f)
    lx = (cx - total / 2) if cx is not None else (x or 0)
    # Chu dung cubic, KHONG dung expo_out: xem ease_out_cubic().
    e = ease_out_cubic(p)

    pad = s(30)
    layer = Image.new("RGBA", (int(s(total)) + pad * 2, int(s(th)) + pad * 2),
                      (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    # Con tro PHAI cong ca `track`. Thieu ve nay thi tracking chi doi vi tri
    # khoi chu chu khong doi khoang giua cac ky tu, va nang hon: layer duoc cap
    # theo be rong DA tinh tracking, nen voi tracking AM (tieu de lon dung
    # track -2 den -3.5) layer hep hon chu thuc ve va ky tu cuoi bi cat mat.
    # Giu con tro o dang float roi moi lam tron khi ve, tranh doi sai so.
    # anchor PHAI ghi ro va trung voi anchor trong tm() - xem ghi chu o tm().
    cur = float(pad)
    for c in txt:
        ld.text((int(round(cur)), pad - s(oy)), c, font=f, fill=fill + (255,),
                anchor=ANCHOR)
        cur += (adv(c, f) + track) * SS

    if reveal == "mask" and e < 1.0:
        dy = int((1 - e) * s(rise))
        # Do mo phai di CUNG mot duong cong voi cu truot. Truoc day dung
        # `e * 1.6` nen chu dat do dac o 14% dau roi con bo len het phan con
        # lai - do la cu "khung" nhin thay duoc. He so 1.15 cho chu dac xong
        # hoi som hon luc dung han, vua du de khong thay no dang mo.
        alpha = layer.getchannel("A").point(
            lambda v: int(v * min(1.0, e * 1.15)))
        layer.putalpha(alpha)
        mask = Image.new("L", layer.size, 0)
        ImageDraw.Draw(mask).rectangle([0, pad - s(4), layer.size[0],
                                        pad + int(s(th)) + s(6)], fill=255)
        layer.putalpha(Image.composite(layer.getchannel("A"), mask, mask))
        base.alpha_composite(layer, (int(s(lx)) - pad, int(s(y)) - pad + dy))
    else:
        base.alpha_composite(layer, (int(s(lx)) - pad, int(s(y)) - pad))
    return th


def mono(base, txt, xy, col, p=1.0, size=26, track=4.0, wght=600):
    """Nhan mono nho, tracking rong. Tang thong tin phu lam day khung."""
    f = font("mono", size)
    try:
        f.set_variation_by_axes([wght])
    except Exception:
        pass
    return ttext(base, txt, f, col, xy[1], x=xy[0], track=track, p=p, rise=10)


def mono_font(size, wght=600):
    """Font mono da nhan wght - dung khi can do be rong truoc khi ve."""
    f = font("mono", size)
    try:
        f.set_variation_by_axes([wght])
    except Exception:
        pass
    return f


# ------------------------------------------------------------------ ngat dong
def _wrap_greedy(txt, f, max_w, track):
    """Ngat dong tham lam: nhoi day dong tren roi xuong dong."""
    words = txt.split()
    if not words:
        return []
    lines, cur = [], words[0]
    for w_ in words[1:]:
        cand = cur + " " + w_
        if track_w(cand, f, track) <= max_w:
            cur = cand
        else:
            lines.append(cur)
            cur = w_
    lines.append(cur)
    return lines


def wrap_track(txt, f, max_w, track):
    """Ngat dong CAN BANG, co tinh ca tracking.

    Tim nhi phan be rong NHO NHAT ma van ra dung so dong -> cac dong deu nhau,
    khong de chu mo coi. Vong tim PHAI goi ban tham lam, khong duoc goi lai
    chinh no: goi de quy thi moi buoc lai sinh mot vong tim moi, chi phi bung
    no ham mu (loi nay tung lam mot frame ton 60 giay).
    """
    lines = _wrap_greedy(txt, f, max_w, track)
    n = len(lines)
    if n < 2:
        return lines
    lo, hi, best = 1, int(max_w), lines
    while lo < hi:
        mid = (lo + hi) // 2
        c2 = _wrap_greedy(txt, f, mid, track)
        if len(c2) <= n and all(track_w(l, f, track) <= max_w for l in c2):
            best, hi = c2, mid
        else:
            lo = mid + 1
    return best


def headline(txt, max_w, max_h, size=104, min_size=64, track=-2.5,
             role="grot_black"):
    """Tieu de type-as-hero: uu tien NGAT DONG o co lon, chi thu nho khi qua cao."""
    sz = size
    while sz > min_size:
        f = font(role, sz)
        lines = wrap_track(txt, f, max_w, track)
        lh = sk.text_size("Ăgjqy", f)[1] * 1.16
        if lh * len(lines) <= max_h:
            return f, lines, lh
        sz -= 4
    f = font(role, min_size)
    lines = wrap_track(txt, f, max_w, track)
    return f, lines, sk.text_size("Ăgjqy", f)[1] * 1.16
