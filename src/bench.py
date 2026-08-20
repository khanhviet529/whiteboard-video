"""Theme BENCH - "ban thi nghiem": so do dat duoi dong ho do, co so chay that.

Khac `phongtoi` o CHO NHIN, khong chi o mau:

  phongtoi                        bench
  ------------------------------  ------------------------------------------
  chu can le trai, khoi lon       KHUNG CO DINH day khung: rail thuong, chip
  noi dung chi o nua tren         chuong, tieu de, the phu de, dong chan
  nen xanh dem + ke ngang         nen gan den + luoi CHAM + bloom tim mo
  panel to dac, vien 2px          net manh + NGOAC GOC kieu khung ngam
  hinh minh hoa tinh              DONG HO DO chay that: gia tri cache/db doi
                                  theo dau doc, bo dem "khach thay gia sai"
  chuyen canh: bong quet ngang    tan mem RIENG dai noi dung, rail va dong chan
                                  dung yen -> giong doi trang cung mot ban do

Y tuong dan dat: nguoi xem khong doc bieu do, ho DOC SO. Mot con so dang nhay
giu mat lau hon bat ky mui ten nao. Vi vay moi canh mo phong deu phai co it
nhat mot o so lien tuc doi gia tri (xem `sc_gantt`).
"""
import numpy as np
from PIL import Image, ImageDraw

import sketch as sk
import typo
from style import H, W, clamp, ease_in_out, font, s
from timing import B
from typo import expo_out, glow, mono, ttext, track_w, wrap_track

# ------------------------------------------------ chuyen canh: tan mem noi dung
FADE = 0.0          # render.py khong tron them: theme tu lo cu tan
DISSOLVE = 0.42     # dai hon cu quet cu (0,30) - cham hon thi de nhin hon
WIPE_OUT = DISSOLVE  # render.py doc hang so nay de khong chup stills luc dang tan

# ------------------------------------------------------------------- bang mau
BG = (9, 9, 12)           # gan den, khong xanh - de tach khoi phongtoi
SURF = (18, 18, 23)
EDGE = (50, 50, 60)
EDGE_HI = (78, 78, 92)
FG = (240, 242, 246)
MUTED = (152, 154, 164)
DIM = (96, 98, 108)
DOTS = (26, 26, 33)       # mau luoi cham DA TRON san voi nen

HOT = (255, 82, 48)       # cam-do: cai sai, tieu diem  (mau tieu de cua mau)
OK = (58, 219, 138)       # xanh la: dung
COOL = (88, 168, 255)     # xanh duong: luong chinh
VIOLET = (170, 132, 255)  # tim: luong phu / request khac
GOLD = (250, 196, 60)     # vang: moc thoi gian

ACCENTS = {"hot": HOT, "ok": OK, "cool": COOL, "violet": VIOLET, "gold": GOLD,
           "fg": FG, "muted": MUTED, "edge": EDGE}

STATES = {"ok": OK, "bad": HOT, "stale": MUTED, "empty": DIM, "warn": GOLD}


# --------------------------------------------------------------- he nhan dien
#
# Mot theme, HAI bo nhan dien. Ly do: 90 video ma cung mot bang mau thi nguoi
# xem khong phan biet duoc mua, va hook cua mua 2 ("ban tin X, day la phan con
# lai") doc nham thanh mua 1 ("hien truong vu an") la mat tac dung.
#
# Doi bang cach GHI DE bien module trong `build()`, khong phai bang cach truyen
# bang mau xuong tung ham. Ly do rat thuc dung: 13 loai canh dang doc thang
# `HOT`, `SURF`, `EDGE`... o hang tram cho: doi sang tra cuu thi phai sua het.
# An toan vi moi tien trinh render chi lam MOT screenplay, va `build()` ap lai
# he o dau moi canh.
HE = {
    # Mua 1, 3, 6 - hien truong vu an. Nen gan den, luoi CHAM, bloom tim.
    "hien_truong": dict(
        BG=(9, 9, 12), SURF=(18, 18, 23), EDGE=(50, 50, 60),
        EDGE_HI=(78, 78, 92), FG=(240, 242, 246), MUTED=(152, 154, 164),
        DIM=(96, 98, 108), DOTS=(26, 26, 33),
        HOT=(255, 82, 48), OK=(58, 219, 138), COOL=(88, 168, 255),
        VIOLET=(170, 132, 255), GOLD=(250, 196, 60),
        nen="cham", bloom=(30.0, 20.0, 52.0)),
    # Mua 2, 5 - toi tuong toi biet. Nen muc xanh, luoi KE NGANG, bloom am.
    # Mau nhan chinh la vang ho phach chu khong phai do: mua 2 khong noi ve su
    # co ma ve mot niem tin bi lat, nen mau bao dong la sai giong.
    "giang_duong": dict(
        BG=(14, 16, 26), SURF=(24, 27, 40), EDGE=(56, 60, 78),
        EDGE_HI=(86, 92, 116), FG=(238, 240, 248), MUTED=(150, 156, 176),
        DIM=(98, 104, 124), DOTS=(30, 34, 48),
        HOT=(245, 176, 66), OK=(94, 214, 178), COOL=(120, 158, 255),
        VIOLET=(186, 148, 255), GOLD=(255, 122, 92),
        nen="ke", bloom=(46.0, 38.0, 18.0)),
}
_HE_HIEN = "hien_truong"


def ap_he(ten):
    """Ghi de bang mau cua module. Goi o dau `build()` cho moi canh."""
    global _HE_HIEN, _bg, ACCENTS, STATES
    ten = ten if ten in HE else "hien_truong"
    if ten == _HE_HIEN and _bg is not None:
        return
    g = globals()
    for k, v in HE[ten].items():
        g[k] = v
    ACCENTS = {"hot": HOT, "ok": OK, "cool": COOL, "violet": VIOLET,
               "gold": GOLD, "fg": FG, "muted": MUTED}
    STATES = {"ok": OK, "bad": HOT, "stale": MUTED, "empty": DIM, "warn": GOLD}
    _bg = None          # nen da cache theo he cu, phai ve lai
    _HE_HIEN = ten


def acc_of(name, fallback=None):
    if isinstance(name, (tuple, list)):
        return tuple(name)
    # `fallback=HOT` trong chu ky ham thi KHONG dung duoc: tham so mac dinh
    # duoc gan luc DINH NGHIA ham, nen no giu bang mau cua he dau tien va
    # `ap_he()` doi mai cung khong toi. Phai tra cuu luc GOI.
    return ACCENTS.get((name or "").lower(), HOT if fallback is None else fallback)


# --------------------------------------------------------------------- bo cuc
MARGIN = 60
CX = W // 2
CONTENT_W = W - MARGIN * 2          # 960

RAIL_Y = 62                          # dong chu mono tren cung
RULE_Y = 116                         # ke ngang duoi rail
CHIP_Y = 150                         # chip chuong, cao 48
CHIP_H = 48
HEAD_Y = 244                         # tieu de canh
HEAD_MAX_H = 190
STAGE_TOP = 470                      # san dien
STAGE_BOTTOM = 1296
NOTE_Y = 1332                        # the phu de
NOTE_MAX_H = 168
FOOT_Y = 1524                        # dong chan; duoi 1570 la vung TikTok phu UI

STAGE_H = STAGE_BOTTOM - STAGE_TOP
STAGE_CY = (STAGE_TOP + STAGE_BOTTOM) / 2


# ------------------------------------------------------------------------ nen
_bg = None


def chuan_bi(doc):
    """Ap he nhan dien TRUOC khi bat ky thu gi duoc ve.

    Bat buoc phai co: `render.py` goi `background()` TRUOC vong lap canh, con
    `build()` moi la cho goi `ap_he()`. Nen neu chi dua vao build() thi nen da
    kip duoc ve va cache bang bang mau cua he mac dinh - da thay dung loi do,
    mau doi dung nhung nen thi khong.
    """
    ap_he((doc or {}).get("he", "hien_truong"))


def background():
    """Nen theo he dang ap. Ve MOT lan roi cache.

    Luoi CHAM (khong phai ke ngang nhu phongtoi) va vet bloom la hai thu lam
    khung hinh co chat lieu ma khong hut mat khoi noi dung. Ca hai phai nuong
    vao nen: ve lai moi frame thi vua cham vua nhay.
    """
    global _bg
    if _bg is not None:
        return _bg
    img = Image.new("RGBA", (s(W), s(H)), BG + (255,))
    d = ImageDraw.Draw(img)
    kieu = HE[_HE_HIEN].get("nen", "cham")
    if kieu == "ke":
        # KE NGANG thay vi luoi cham: doi chat lieu nen la thu doc duoc trong
        # nua giay, nhanh hon bat ky khac biet mau nao.
        for y in range(RULE_Y + 40, FOOT_Y + 20, 44):
            d.line([s(MARGIN), s(y), s(W - MARGIN), s(y)],
                   fill=DOTS + (255,), width=max(1, s(1)))
    else:
        r = max(1, s(1.2))
        for y in range(RULE_Y + 40, FOOT_Y + 20, 46):
            for x in range(MARGIN, W - MARGIN + 1, 46):
                d.ellipse([s(x) - r, s(y) - r, s(x) + r, s(y) + r],
                          fill=DOTS + (255,))

    a = np.array(img.convert("RGB")).astype(np.float32)
    hh, ww = a.shape[:2]
    yy, xx = np.mgrid[0:hh, 0:ww].astype(np.float32)
    # bloom elip quanh san dien - sang o giua, tat han o bien
    nx = (xx / ww - 0.5) / 0.62
    ny = (yy / hh - 0.44) / 0.40
    fall = np.clip(1.0 - (nx * nx + ny * ny), 0.0, 1.0) ** 2.1
    for i, tint in enumerate(HE[_HE_HIEN].get("bloom", (30.0, 20.0, 52.0))):
        a[:, :, i] += fall * tint
    rng = np.random.default_rng(7)
    a += rng.normal(0, 5.5, (hh, ww, 1))
    _bg = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    return _bg


# ------------------------------------------------------------- primitive khung
def card(base, box, p=1.0, fill=-1, border=-1, radius=14, lit=None,
         width=2):
    """The noi dung: bo goc, net manh. `lit` = mau vet sang neu la tieu diem.

    `fill=-1` chu khong `fill=SURF`: tham so mac dinh duoc gan luc DINH NGHIA
    ham, nen `SURF` o day se dong bang bang mau cua he dau tien va `ap_he()`
    doi mai cung khong toi. Dung mot gia tri canh de biet "chua ai khai".
    """
    if p <= 0:
        return
    if fill == -1:
        fill = SURF
    if border == -1:
        border = EDGE
    e = expo_out(p)
    x0, y0, x1, y1 = box
    cy = (y0 + y1) / 2
    k = 0.965 + 0.035 * e
    y0, y1 = cy + (y0 - cy) * k, cy + (y1 - cy) * k
    if lit:
        glow(base, (x0, y0, x1, y1), lit, 60, int(66 * e))
    ImageDraw.Draw(base).rounded_rectangle(
        [s(x0), s(y0), s(x1), s(y1)], radius=s(radius),
        fill=fill + (255,) if fill else None,
        outline=border + (255,), width=s(width))


def brackets(base, box, col, p=1.0, size=30, width=3):
    """Bon goc kieu khung ngam. Dau hieu nhan dien cua theme nay.

    Dung thay cho vien kin: khung ngam goi y "dang do", con vien kin goi y
    "mot cai hop". Ca video la mot ban do nen phai ra chat do.
    """
    if p <= 0:
        return
    e = expo_out(p)
    x0, y0, x1, y1 = box
    L = size * e
    if L < 1:
        return
    d = ImageDraw.Draw(base)
    w = s(width)
    for cx_, cy_, sx, sy in ((x0, y0, 1, 1), (x1, y0, -1, 1),
                             (x0, y1, 1, -1), (x1, y1, -1, -1)):
        d.line([s(cx_), s(cy_), s(cx_ + L * sx), s(cy_)], fill=col + (255,),
               width=w)
        d.line([s(cx_), s(cy_), s(cx_), s(cy_ + L * sy)], fill=col + (255,),
               width=w)


def hline(base, y, col=-1, x0=MARGIN, x1=W - MARGIN, p=1.0, width=2):
    if p <= 0:
        return
    if col == -1:            # xem chu thich trong `card` ve tham so mac dinh
        col = EDGE
    e = expo_out(p)
    ImageDraw.Draw(base).line(
        [s(x0), s(y), s(x0 + (x1 - x0) * e), s(y)], fill=col + (255,),
        width=s(width))


def bar(base, box, col, p=1.0, radius=8, grow="x"):
    """Thanh dac moc ra theo p - dung cho lane, thanh tien do."""
    if p <= 0:
        return
    e = expo_out(p) if grow == "x" else clamp(p)
    x0, y0, x1, y1 = box
    x1 = x0 + (x1 - x0) * e
    if x1 - x0 < 2:
        return
    ImageDraw.Draw(base).rounded_rectangle(
        [s(x0), s(y0), s(x1), s(y1)], radius=s(radius), fill=col + (255,))


def fit_one(role, txt, max_w, size, min_size=30, track=-1.5, step=2):
    """Thu nho cho vua MOT dong. Dung cho o so - so khong duoc ngat dong."""
    sz = size
    f = font(role, sz)
    while sz > min_size and track_w(txt, f, track) > max_w:
        sz -= step
        f = font(role, sz)
    return f


def headline_fit(txt, max_w, max_h, size, min_size, track=-1.6, role="grot"):
    return typo.headline(txt, max_w, max_h, size, min_size, track, role)


# ------------------------------------------------------- khung co dinh moi canh
def chapters(doc):
    """Ten chuong -> so thu tu, dem theo lan xuat hien dau tien trong doc."""
    out, n = {}, 0
    for sp in (doc or {}).get("scenes", []):
        ch = sp.get("chapter")
        if ch and ch not in out:
            n += 1
            out[ch] = n
    return out


def chrome(b, sp, doc, acc, chmap, first=False):
    """Rail tren + chip chuong + tieu de canh. Ba thu nay co o MOI canh.

    Day la diem khac lon nhat so voi phongtoi: khung hinh luon co bo khung, nen
    mat nguoi xem biet dang o dau trong video. Phia phongtoi de trong ba phan
    tu khung nen moi canh trong nhu mot slide roi.

    Rail chi chay hieu ung o canh DAU TIEN (`first`), tu canh hai tro di ve dac
    ngay. Ly do: cu tan cuoi canh khong tan rail, nen neu canh sau lai cho rail
    mo dan tu 0 thi moi diem cat co mot cu sut sang cua rail - dung thu ma cu
    tan nay sinh ra de tranh. Do dac la thu phai dung yen thi moi ra "cung mot
    ban do".
    """
    brand = (doc or {}).get("brand")
    tag = (doc or {}).get("tag")

    def fn_rail(base, d, p):
        q = p if first else 1.0
        if brand:
            mono(base, brand, (MARGIN, RAIL_Y), acc, q, 24, 5.0, 700)
        if tag:
            f = typo.mono_font(22, 400)
            ttext(base, tag, f, DIM, RAIL_Y + 2,
                  x=W - MARGIN - track_w(tag, f, 3.0), track=3.0, p=q, rise=8)
        hline(base, RULE_Y, EDGE, MARGIN, W - MARGIN, min(1.0, q * 1.4))
    b.add(fn_rail, dur=0.34, wait=0.0, at=0.0)

    ch = sp.get("chapter")
    if ch:
        label = f"{chmap.get(ch, 1):02d} · {ch}"
        cf = typo.mono_font(24, 700)
        cw = track_w(label, cf, 4.0) + 96

        def fn_chip(base, d, p):
            card(base, (MARGIN, CHIP_Y, MARGIN + cw, CHIP_Y + CHIP_H), p,
                 fill=SURF, border=EDGE, radius=CHIP_H // 2, width=2)
            if p > 0.3:
                q = (p - 0.3) / 0.7
                r = 7
                ccy = CHIP_Y + CHIP_H / 2
                ImageDraw.Draw(base).ellipse(
                    [s(MARGIN + 30 - r), s(ccy - r), s(MARGIN + 30 + r),
                     s(ccy + r)], fill=acc + (255,))
                oy, th = typo.tm(label, cf)
                ttext(base, label, cf, FG, ccy - th / 2, x=MARGIN + 54,
                      track=4.0, p=q, rise=8)
        b.add(fn_chip, dur=0.36, wait=0.0, at=0.10)

    head = sp.get("head")
    if head:
        f, lines, lh = headline_fit(head, CONTENT_W - 10, HEAD_MAX_H, 68, 46,
                                    -1.4, "grot")

        def fn_head(base, d, p):
            for i, ln in enumerate(lines):
                lp = clamp((p - i * 0.14) * 1.5)
                if lp > 0:
                    ttext(base, ln, f, FG, HEAD_Y + i * lh, x=MARGIN,
                          track=-1.4, p=lp, rise=22)
        b.add(fn_head, dur=0.5, wait=0.0, at=0.22)


def note(b, txt, acc, at=0.26):
    """The phu de duoi san dien: vach mau ben trai + chu trong the bo goc.

    Chon co chu lon nhat ma ca khoi con vua NOTE_MAX_H. Khong bao gio cat bot
    cau: phu de bi cat thi nguoi xem tat tieng se mat noi dung.
    """
    if not txt:
        return
    for size in (32, 30, 28, 26, 24):
        f = font("grot_med", size)
        lines = sk.wrap(txt, f, CONTENT_W - 96)
        lh = sk.line_height(f, 1.34)
        if lh * len(lines) + 44 <= NOTE_MAX_H:
            break
    hgt = lh * len(lines) + 44
    box = (MARGIN, NOTE_Y, W - MARGIN, NOTE_Y + hgt)

    def fn(base, d, p):
        card(base, box, min(1.0, p * 1.5), fill=SURF, border=EDGE, radius=12)
        if p > 0.15:
            bar(base, (MARGIN + 2, NOTE_Y + 12, MARGIN + 8, NOTE_Y + hgt - 12),
                acc, 1.0, radius=3)
            for i, ln in enumerate(lines):
                lp = clamp((p - 0.15 - i * 0.09) * 1.8)
                if lp > 0:
                    ttext(base, ln, f, MUTED, NOTE_Y + 22 + i * lh,
                          x=MARGIN + 34, p=lp, rise=10)
    b.add(fn, dur=0.55, wait=0.0, at=at)


def footer(b, doc, at=0.5, first=False):
    """Dong chan. Cung la do dac nhu rail: chi chay hieu ung o canh dau tien."""
    txt = (doc or {}).get("footer")
    if not txt:
        return
    # TU THU cho vua be ngang. Truoc day co chu cung 22px, nen dong chan dai
    # hon ~58 ky tu bi cat mat duoi phai MA KHONG CO GI BAO - da thay o so 98
    # (65 ky tu) va 99 (83 ky tu). Cat o dong chan la mat nua cau ket luan cua
    # ca video, va no lang le hon moi loi khac trong file nay.
    f = typo.mono_font(22, 400)
    for sz in (22, 20, 18, 16):
        f = typo.mono_font(sz, 400)
        if track_w(txt, f, 3.5) <= CONTENT_W:
            break

    def fn(base, d, p):
        ttext(base, txt, f, DIM, FOOT_Y, cx=CX, track=3.5,
              p=p if first else 1.0, rise=8)
    # Tu canh hai tro di phai xep tu MOC 0. Ve dac ngay thoi chua du: phan tu
    # nao chua toi `at` thi render.py bo qua han (p <= 0), nen dong chan se biet
    # mat 0,46s dau moi canh - dung cai sut sang ma cu tan can tranh.
    b.add(fn, dur=0.5, wait=0.0, at=at if first else 0.0)


def dissolve(b):
    """Cuoi canh: tan NOI DUNG ve nen, GIU nguyen rail va dong chan.

    Ban dau cho la mot man che truot doc co vach sang mau accent dan duong. Sai:
    moi diem cat co HAI vach (mot khi ra canh, mot khi vao canh) luot het khung
    trong ~0,56s, lai dung `expo_out` nen phong rat nhanh o doan dau. Mot vach
    sang manh keo nhanh qua vong mat 12 lan trong hai phut la nhuc mat that, va
    no khong nói thêm điều gì về nội dung.

    Cach nay thay bang mot cu tan mem, va chi tan DAI NOI DUNG: rail chu mono
    tren cung va dong chan o duoi dung yen suot video. Nho vay hai canh noi nhau
    giong nhu doi trang trong cung mot ban do - do la cu chuyen canh cua
    `video_template/6.mp4`, va la ly do no trong "chuyen nghiep" chu khong phai
    vi hieu ung phuc tap hon.

    Dung ease_in_out (khong phai expo): hai dau cham, giua nhanh - mat khong bi
    giat o thoi diem bat dau.
    """
    y0, y1 = CHIP_Y - 26, NOTE_Y + NOTE_MAX_H + 10

    def fn_out(base, d, p):
        a = ease_in_out(p)
        if a <= 0.002:
            return
        # cat dung dai noi dung tu NEN da cache roi phu len voi do mo tang dan:
        # tan ve chinh cai nen do (luoi cham + bloom), khong phai ve mau phang
        band = background().crop((0, int(s(y0)), int(s(W)), int(s(y1))))
        if a < 1.0:
            band.putalpha(int(255 * a))
        base.alpha_composite(band, (0, int(s(y0))))
    b.add(fn_out, dur=DISSOLVE, wait=0.0, at=max(0.1, b.dur - DISSOLVE))


# ============================================================== CAC LOAI CANH
def sc_probe(b, sp, acc):
    """Console that: lenh o trai, ket qua o phai, dong sai to do.

    Day la canh mo dau manh nhat cho dan mid-level: ho doc duoc ba dong nay
    nhanh hon bat ky loi giai thich nao, va tu thay ngay cho vo ly.
    """
    rows = sp["lines"]
    hh = 68
    rowh = 86
    pad = 30
    # `lenh` va `nguon` deu cong them mot hang. Chung ton dat man hinh, va do la
    # co y: mot bang so tinh chi la LOI TUYEN BO, con dong lenh go ra roi ket
    # qua chay theo sau moi la BANG CHUNG. Kenh nay lay "khong bia so" lam goc
    # nen phai cho nguoi xem duong kiem lai, khong the bat ho tin loi.
    lenh_h = 52 if sp.get("lenh") else 0
    nguon_h = 40 if sp.get("nguon") else 0
    hgt = hh + lenh_h + rowh * len(rows) + nguon_h + pad
    y0 = STAGE_CY - hgt / 2
    box = (MARGIN, y0, W - MARGIN, y0 + hgt)
    cf = typo.mono_font(sp.get("code_size", 34), 500)
    of = typo.mono_font(sp.get("code_size", 34) - 2, 700)
    bad_any = any((r.get("state") or "") == "bad" for r in rows)

    def fn_card(base, d, p):
        card(base, box, p, fill=SURF, border=EDGE, radius=14,
             lit=HOT if bad_any else None)
        if p > 0.3:
            q = (p - 0.3) / 0.7
            hline(base, y0 + hh, EDGE, MARGIN + 1, W - MARGIN - 1, q)
            mono(base, sp.get("heading", "SHELL"), (MARGIN + 30, y0 + 22),
                 MUTED, q, 24, 4.5)
            if sp.get("status"):
                # `status: 504` khong co nhay thi YAML tra ve int va track_w()
                # no ngay. Ep kieu o day chu khong bat nguoi viet nho quy tac -
                # `status: 200 OK` thi la chuoi, `status: 504` thi la so, khac
                # nhau o mot ky tu ma nguoi viet khong the doan duoc.
                st = str(sp["status"])
                f = typo.mono_font(24, 700)
                ttext(base, st, f, acc, y0 + 22,
                      x=W - MARGIN - 30 - track_w(st, f, 3.5), track=3.5, p=q,
                      rise=8)
    b.add(fn_card, dur=0.5, wait=0.34)

    # --- dong lenh: go ra tung ky tu roi moi toi ket qua
    if sp.get("lenh"):
        ly = y0 + hh + 10
        lf = typo.mono_font(28, 500)
        lenh = str(sp["lenh"])

        def fn_lenh(base, d, p):
            n = int(clamp(p / 0.72) * len(lenh))
            txt = lenh[:n]
            ttext(base, "$ " + txt, lf, FG, ly, x=MARGIN + 30, track=0.5)
            if p < 0.86 and int(p * 22) % 2 == 0:   # con tro nhap nhay
                cw = track_w("$ " + txt, lf, 0.5)
                ImageDraw.Draw(base).rectangle(
                    [s(MARGIN + 30 + cw + 3), s(ly + 2),
                     s(MARGIN + 30 + cw + 16), s(ly + 30)], fill=FG + (255,))
        b.add(fn_lenh, dur=0.9, wait=0.5)

    for i, r in enumerate(rows):
        ry = y0 + hh + lenh_h + pad / 2 + i * rowh
        state = (r.get("state") or "").lower()
        ocol = STATES.get(state, MUTED)
        is_bad = state == "bad"

        def fn(base, d, p, r=r, ry=ry, ocol=ocol, is_bad=is_bad):
            e = expo_out(p)
            cy = ry + rowh / 2
            if is_bad:
                glow(base, (MARGIN + 14, ry + 6, W - MARGIN - 14,
                            ry + rowh - 6), HOT, 44, int(52 * e))
                bar(base, (MARGIN + 14, ry + 10, MARGIN + 19, ry + rowh - 10),
                    HOT, 1.0, radius=3)
            oy, th = typo.tm(r["cmd"], cf)
            mono(base, "$", (MARGIN + 34, cy - 15), DIM, min(1.0, p * 2), 26,
                 0, 700)
            ttext(base, r["cmd"], cf, FG if not is_bad else FG, cy - th / 2,
                  x=MARGIN + 66, p=p, rise=12)
            out = r.get("out")
            if out and p > 0.45:
                q = (p - 0.45) / 0.55
                ow = track_w(out, of, 1.5)
                ttext(base, out, of, ocol, cy - typo.tm(out, of)[1] / 2,
                      x=W - MARGIN - 34 - ow, track=1.5, p=q, rise=10)
        b.add(fn, dur=0.46, wait=0.3)

    # Duong dan de nguoi xem TU CHAY LAI. Day moi la thu bien mot bang so thanh
    # mot phep do kiem chung duoc.
    if sp.get("nguon"):
        ny = y0 + hgt - 30

        def fn_nguon(base, d, p):
            mono(base, "chạy lại:  " + str(sp["nguon"]), (MARGIN + 30, ny),
                 DIM, p, 21, 2.0, 500)
        b.add(fn_nguon, dur=0.4, wait=0.2)

    if sp.get("verdict"):
        _verdict(b, sp["verdict"], box[3] + 74, HOT)


def sc_statement(b, sp, acc):
    """Mot cau dap vao mat, dat trong khung ngam, can giua.

    Can GIUA la co y: phongtoi can le trai het, nen chi rieng viec can giua da
    doi hoan toan cam giac bo cuc.
    """
    col = acc_of(sp.get("color"), acc)
    f, lines, lh = typo.headline(sp["value"], CONTENT_W - 120, 520,
                                 sp.get("size", 128), 68, -2.5, "slab_black")
    total = lh * len(lines)
    label = sp.get("label")
    sub = sp.get("sub")
    sub_h = 96 if sub else 0
    lab_h = 62 if label else 0
    blk = total + sub_h + lab_h
    y0 = STAGE_CY - blk / 2
    ytxt = y0 + lab_h
    gw = max(track_w(l, f, -2.5) for l in lines)
    fbox = (CX - gw / 2 - 54, ytxt - 40, CX + gw / 2 + 54, ytxt + total + 34)

    if label:
        def fn_l(base, d, p):
            lf = typo.mono_font(26, 700)
            ttext(base, label, lf, col, y0, cx=CX, track=5.0, p=p, rise=10)
        b.add(fn_l, dur=0.36, wait=0.22)

    def fn_g(base, d, p):
        glow(base, (CX - gw / 2, ytxt + 12, CX + gw / 2, ytxt + total - 12),
             col, 84, int(44 * expo_out(p)))
        brackets(base, fbox, col, p, 40, 4)
    b.add(fn_g, dur=0.55, wait=0.2)

    for i, ln in enumerate(lines):
        def fn(base, d, p, ln=ln, i=i):
            ttext(base, ln, f, FG, ytxt + i * lh, cx=CX, track=-2.5, p=p,
                  rise=28)
        b.add(fn, dur=0.5, wait=0.26)

    if sp.get("strike"):
        def fn_s(base, d, p):
            e = expo_out(p)
            yy = ytxt + total / 2
            ImageDraw.Draw(base).line(
                [s(CX - gw / 2 - 10), s(yy), s(CX - gw / 2 - 10 + (gw + 20) * e),
                 s(yy)], fill=HOT + (255,), width=s(7))
        b.add(fn_s, dur=0.4, wait=0.24)

    if sub:
        sf = font("grot_med", 38)
        slines = wrap_track(sub, sf, CONTENT_W - 140, 0)

        def fn_sub(base, d, p):
            hline(base, ytxt + total + 40, EDGE, CX - 120, CX + 120,
                  min(1.0, p * 2))
            for i, ln in enumerate(slines):
                lp = clamp((p - i * 0.12) * 1.6)
                if lp > 0:
                    ttext(base, ln, sf, MUTED, ytxt + total + 66 + i * 50,
                          cx=CX, p=lp, rise=14)
        b.add(fn_sub, dur=0.5, wait=0.26)


def sc_list(b, sp, acc):
    """Danh sach co so trong o vuong nho. Dong tieu diem to mau accent."""
    items = sp["items"]
    n = len(items)
    tsize = {1: 60, 2: 54, 3: 48, 4: 44}.get(n, 38)
    tf = font("grot", tsize)
    rows = []
    for it in items:
        txt = it if isinstance(it, str) else it["text"]
        meta = {} if isinstance(it, str) else it
        rows.append((wrap_track(txt, tf, CONTENT_W - 140, -1.0), meta))
    lh = sk.text_size("Ăgjqy", tf)[1] * 1.24
    heights = [lh * len(l) + 66 for l, _ in rows]
    total = sum(heights)
    y = STAGE_CY - total / 2
    ys, a = [], y
    for h_ in heights:
        ys.append(a)
        a += h_

    for i, ((lines, meta), yy) in enumerate(zip(rows, ys)):
        is_f = bool(meta.get("focus"))
        col = acc_of(meta.get("color"), acc) if is_f else EDGE_HI

        def fn(base, d, p, i=i, lines=lines, yy=yy, is_f=is_f, col=col):
            e = expo_out(p)
            nb = (MARGIN, yy + 16, MARGIN + 54, yy + 70)
            if is_f:
                glow(base, nb, col, 40, int(70 * e))
            card(base, nb, min(1.0, p * 1.6), fill=SURF if not is_f else col,
                 border=col, radius=8, width=2)
            nf = typo.mono_font(26, 700)
            oy, th = typo.tm(f"{i+1:02d}", nf)
            ttext(base, f"{i+1:02d}", nf, BG if is_f else MUTED,
                  (nb[1] + nb[3]) / 2 - th / 2, cx=(nb[0] + nb[2]) / 2,
                  track=1.5, p=min(1.0, p * 1.6), rise=8)
            for j, ln in enumerate(lines):
                lp = clamp((p - j * 0.1) * 1.5)
                if lp > 0:
                    ttext(base, ln, tf, FG if is_f else MUTED,
                          yy + 12 + j * lh, x=MARGIN + 92, track=-1.0, p=lp,
                          rise=16)
        b.add(fn, dur=0.5, wait=0.3)


def sc_rule(b, sp, acc):
    """The quy tac: so lon trong khung ngam, cau quy tac, ghi chu nho."""
    col = acc_of(sp.get("color"), acc)
    num = str(sp.get("n", "01"))
    bf, blines, blh = typo.headline(sp["body"], CONTENT_W - 150, 320, 74, 48,
                                    -1.6, "grot_black")
    sfz = font("grot_med", 32)
    slines = sk.wrap(sp.get("small", ""), sfz, CONTENT_W - 170) \
        if sp.get("small") else []
    slh = sk.line_height(sfz, 1.36)

    head_h = 118
    inner = blh * len(blines) + ((slh * len(slines) + 34) if slines else 0) + 92
    hgt = head_h + inner
    y0 = STAGE_CY - hgt / 2
    box = (MARGIN, y0, W - MARGIN, y0 + hgt)

    def fn_c(base, d, p):
        card(base, box, p, fill=SURF, border=col, radius=16, lit=col)
    b.add(fn_c, dur=0.5, wait=0.3)

    def fn_h(base, d, p):
        # khung ngoac phai NONG hon chu so, khong thi net ngoac cat qua chu
        nf = font("slab_black", 72)
        nw = track_w(num, nf, -2)
        nh = typo.tm(num, nf)[1]
        ccy = y0 + head_h / 2
        nb = (MARGIN + 28, ccy - nh / 2 - 20, MARGIN + 28 + nw + 40,
              ccy + nh / 2 + 20)
        brackets(base, nb, col, min(1.0, p * 1.8), 22, 4)
        ttext(base, num, nf, col, ccy - nh / 2, cx=(nb[0] + nb[2]) / 2,
              track=-2, p=p, rise=16)
        if p > 0.35:
            q = (p - 0.35) / 0.65
            mono(base, sp.get("kicker", "QUY TẮC"), (nb[2] + 30, ccy - 13),
                 MUTED, q, 26, 5.0)
        hline(base, y0 + head_h, EDGE, MARGIN + 1, W - MARGIN - 1,
              clamp(p * 1.2))
    b.add(fn_h, dur=0.5, wait=0.3)

    def fn_b(base, d, p):
        for i, ln in enumerate(blines):
            lp = clamp((p - i * 0.12) * 1.5)
            if lp > 0:
                ttext(base, ln, bf, FG, y0 + head_h + 40 + i * blh,
                      x=MARGIN + 34, track=-1.6, p=lp, rise=20)
    b.add(fn_b, dur=0.55, wait=0.3)

    if slines:
        ytop = y0 + head_h + 40 + blh * len(blines) + 34

        def fn_s(base, d, p):
            hline(base, ytop - 18, EDGE, MARGIN + 34, W - MARGIN - 34,
                  min(1.0, p * 2))
            for i, ln in enumerate(slines):
                lp = clamp((p - 0.18 - i * 0.1) * 1.7)
                if lp > 0:
                    ttext(base, ln, sfz, DIM, ytop + i * slh, x=MARGIN + 34,
                          p=lp, rise=12)
        b.add(fn_s, dur=0.5, wait=0.26)


def sc_counters(b, sp, acc):
    """Day o so trong khung ngam - chu ky hinh anh cua theme.

    Dung khi muon cho thay MOT gia tri khong doi qua nhieu moc thoi gian: ba o
    giong nhau canh nhau noi len dieu do nhanh hon mot cau giai thich.
    """
    items = sp["items"]
    n = len(items)
    gap = 26
    bw = (CONTENT_W - gap * (n - 1)) / n
    bh = sp.get("box_h", 260)
    y0 = STAGE_CY - bh / 2

    for i, it in enumerate(items):
        x0 = MARGIN + i * (bw + gap)
        col = acc_of(it.get("color"), acc)
        box = (x0, y0, x0 + bw, y0 + bh)
        val = str(it["value"])

        def fn(base, d, p, box=box, it=it, col=col, val=val):
            e = expo_out(p)
            glow(base, box, col, 56, int(40 * e))
            card(base, box, p, fill=SURF, border=EDGE, radius=12)
            brackets(base, (box[0] + 12, box[1] + 12, box[2] - 12,
                            box[3] - 12), col, p, 26, 3)
            if p > 0.3:
                q = (p - 0.3) / 0.7
                bcx = (box[0] + box[2]) / 2
                if it.get("top"):
                    tf = typo.mono_font(22, 700)
                    ttext(base, it["top"], tf, MUTED, box[1] + 44, cx=bcx,
                          track=3.5, p=q, rise=10)
                vf = fit_one("grot_black", val, bw - 76, sp.get("size", 66), 34)
                oy, th = typo.tm(val, vf)
                ttext(base, val, vf, col, (box[1] + box[3]) / 2 - th / 2 - 14,
                      cx=bcx, track=-1.5, p=q, rise=18)
                if it.get("label"):
                    lf = typo.mono_font(22, 500)
                    ttext(base, it["label"], lf, MUTED, box[3] - 62, cx=bcx,
                          track=3.0, p=q, rise=10)
        b.add(fn, dur=0.5, wait=0.28)

    if sp.get("verdict"):
        _verdict(b, sp["verdict"], y0 + bh + 76, HOT)


def sc_ask(b, sp, acc):
    """Canh chot: cau hoi ve chinh he thong cua nguoi xem."""
    f, lines, lh = typo.headline(sp["text"], CONTENT_W - 130, 460,
                                 sp.get("size", 104), 62, -2.2, "slab_black")
    total = lh * len(lines)
    hint = sp.get("hint")
    hgt = total + (120 if hint else 0)
    y0 = STAGE_CY - hgt / 2
    fbox = (MARGIN + 20, y0 - 56, W - MARGIN - 20, y0 + total + 46)

    def fn_f(base, d, p):
        glow(base, fbox, acc, 80, int(38 * expo_out(p)))
        brackets(base, fbox, acc, p, 46, 4)
    b.add(fn_f, dur=0.55, wait=0.26)

    for i, ln in enumerate(lines):
        def fn(base, d, p, ln=ln, i=i):
            ttext(base, ln, f, FG, y0 + i * lh, cx=CX, track=-2.2, p=p,
                  rise=26)
        b.add(fn, dur=0.52, wait=0.28)

    if hint:
        hf = typo.mono_font(30, 500)

        def fn_h(base, d, p):
            # DUOI khung ngoac, khong phai trong: dat trong thi net ngoac duoi
            # chay ngang qua chu
            ttext(base, hint, hf, acc, fbox[3] + 42, cx=CX, track=2.0, p=p,
                  rise=14)
        b.add(fn_h, dur=0.5, wait=0.26)


# ------------------------------------------------------------------- MO PHONG
def _state_at(steps, p):
    """Buoc dang co hieu luc tai thoi diem p (buoc cuoi cung da qua `at`)."""
    cur = steps[0]
    for st in steps:
        if p >= float(st.get("at", 0.0)):
            cur = st
    return cur


def _step_label(base, txt, sx, sw, by, ann_y, lcol, x1, lane_h):
    """Ten buoc: uu tien dat TRONG thanh, thu nho dan cho vua.

    Chua vua o co nho nhat thi day xuong hang nhan tran ngay duoi duong ray -
    KHONG bao gio dat len phia tren, cho do la cua ten lane.
    """
    for sz in (26, 24, 22, 20):
        tf = typo.mono_font(sz, 700)
        if track_w(txt, tf, 1.2) <= sw - 28:
            ttext(base, txt, tf, BG, by + lane_h / 2 - typo.tm(txt, tf)[1] / 2,
                  x=sx + 14, track=1.2)
            return
    tf = typo.mono_font(21, 700)
    tw = track_w(txt, tf, 1.2)
    ttext(base, txt, tf, lcol, ann_y, x=min(sx, x1 - tw), track=1.2)


def sc_gantt(b, sp, acc):
    """MO PHONG ⭐ - Gantt hai luong + DONG HO DO chay that.

    Khac `race` cua phongtoi o mot diem quyet dinh: o day co hang o so phia
    tren, va gia tri trong do DOI theo dau doc. Nguoi xem khong phai suy ra
    "vay luc nay cache dang giu gi" - no hien ra thanh chu. Chinh cho nay bien
    mot bieu do thanh mot thi nghiem.

    Lich phai LIEN MACH: bat ky khoang nao khong co gi doi la mat nguoi xem.
    """
    lanes = sp["lanes"][:2]
    readouts = sp.get("readout", [])
    ruler = sp.get("ruler", [])
    coll = sp.get("verdict_at")
    counter = sp.get("counter")
    # cau ket cua lan chay DUNG phai la mau xanh, khong phai do - neu de do het
    # thi hai lan mo phong nhin y nhau va mat het y nghia doi chieu
    vcol = acc_of(sp.get("verdict_color"), HOT)

    # --- hang o so
    ro_h = 186 if readouts else 0
    ro_y = STAGE_TOP + 6
    nro = max(1, len(readouts) + (1 if counter else 0))
    ro_gap = 22
    ro_w = (CONTENT_W - ro_gap * (nro - 1)) / nro

    # --- lane. Moi lane co BA hang: ten lane / duong ray / hang nhan tran.
    # Hang nhan tran la cho dat ten buoc khi thanh qua ngan de chua chu ben
    # trong. Thieu hang nay thi nhan buoc de len ten lane - bug da tung xay ra.
    lane_top = ro_y + ro_h + 46
    label_h, lane_h, ann_h, lane_gap = 42, 106, 34, 26
    block = label_h + lane_h + ann_h
    lanes_h = len(lanes) * block + (len(lanes) - 1) * lane_gap
    ruler_y = lane_top + lanes_h + 18
    x0, x1 = MARGIN, W - MARGIN

    def fn(base, d, p):
        dd = ImageDraw.Draw(base)
        head = x0 + (x1 - x0) * clamp(p)

        # ---------- o so: gia tri doi theo dau doc
        for i, ro in enumerate(readouts):
            bx = MARGIN + i * (ro_w + ro_gap)
            box = (bx, ro_y, bx + ro_w, ro_y + ro_h)
            st = _state_at(ro["steps"], p)
            col = STATES.get((st.get("state") or "").lower(), FG)
            fresh = clamp(1.0 - (p - float(st.get("at", 0.0))) / 0.07)
            if fresh > 0:
                glow(base, box, col, 54, int(74 * fresh))
            card(base, box, 1.0, fill=SURF, border=EDGE, radius=12)
            brackets(base, (box[0] + 10, box[1] + 10, box[2] - 10,
                            box[3] - 10), col if fresh > 0 else EDGE_HI, 1.0,
                     24, 3)
            bcx = (box[0] + box[2]) / 2
            kf = typo.mono_font(22, 700)
            ttext(base, ro["key"], kf, MUTED, box[1] + 28, cx=bcx, track=4.0)
            val = str(st.get("value", ""))
            vf = fit_one("grot_black", val, ro_w - 60, 62, 30)
            oy, th = typo.tm(val, vf)
            ttext(base, val, vf, col, (box[1] + box[3]) / 2 - th / 2 + 14,
                  cx=bcx, track=-1.5)
            if st.get("note"):
                nf = typo.mono_font(20, 500)
                ttext(base, st["note"], nf, DIM, box[3] - 40, cx=bcx,
                      track=2.5)

        # ---------- bo dem: so khach da nhin thay gia sai
        if counter:
            bx = MARGIN + len(readouts) * (ro_w + ro_gap)
            box = (bx, ro_y, bx + ro_w, ro_y + ro_h)
            start = float(counter.get("from", 0.0))
            val = 0
            if p >= start:
                val = int((p - start) * float(counter.get("rate", 40)))
            col = HOT if val else DIM
            if val:
                glow(base, box, HOT, 58, 46)
            card(base, box, 1.0, fill=SURF, border=EDGE, radius=12)
            brackets(base, (box[0] + 10, box[1] + 10, box[2] - 10,
                            box[3] - 10), col, 1.0, 24, 3)
            bcx = (box[0] + box[2]) / 2
            kf = typo.mono_font(22, 700)
            ttext(base, counter.get("key", "ĐÃ ĐỌC SAI"), kf, MUTED,
                  box[1] + 28, cx=bcx, track=4.0)
            sval = str(val)
            vf = fit_one("grot_black", sval, ro_w - 60, 78, 40)
            oy, th = typo.tm(sval, vf)
            ttext(base, sval, vf, col, (box[1] + box[3]) / 2 - th / 2 + 14,
                  cx=bcx, track=-1.5)
            if counter.get("label"):
                lf = typo.mono_font(20, 500)
                ttext(base, counter["label"], lf, DIM, box[3] - 40, cx=bcx,
                      track=2.5)

        # ---------- lane
        geom = []
        for li, lane in enumerate(lanes):
            ly = lane_top + li * (block + lane_gap)
            by = ly + label_h
            lcol = acc_of(lane.get("color"), acc)
            geom.append((lane, ly, by, lcol))
            ImageDraw.Draw(base).rounded_rectangle(
                [s(x0), s(by), s(x1), s(by + lane_h)], radius=s(10),
                fill=SURF + (255,), outline=EDGE + (255,), width=s(2))
            for step in lane.get("steps", []):
                sx = x0 + (x1 - x0) * float(step["at"])
                sw = (x1 - x0) * float(step.get("w", 0.16))
                if head < sx:
                    continue
                grow = clamp((head - sx) / max(sw, 1e-6))
                fill = HOT if step.get("bad") else lcol
                if step.get("bad") and grow > 0.2:
                    glow(base, (sx, by + 6, sx + sw * grow, by + lane_h - 6),
                         HOT, 40, 54)
                bar(base, (sx, by + 8, sx + sw * grow, by + lane_h - 8), fill,
                    1.0, radius=8, grow="none")

        # dau doc: chi quet trong vung duong ray, khong cat ngang nhan
        for _, _, by, _ in geom:
            dd.line([s(head), s(by - 14), s(head), s(by + lane_h + 14)],
                    fill=FG + (255,), width=s(3))
        dd.line([s(head), s(geom[0][2] - 14), s(head),
                 s(geom[-1][2] + lane_h + 14)], fill=EDGE_HI + (255,),
                width=s(2))

        # chu luon ve sau cung -> khong bi thanh mau de len
        for lane, ly, by, lcol in geom:
            mono(base, lane["label"], (x0 + 4, ly + 6), MUTED, 1.0, 23, 3.5)
            for step in lane.get("steps", []):
                sx = x0 + (x1 - x0) * float(step["at"])
                sw = (x1 - x0) * float(step.get("w", 0.16))
                if head < sx:
                    continue
                if clamp((head - sx) / max(sw, 1e-6)) < 0.96:
                    continue
                _step_label(base, step["text"], sx, sw, by,
                            ann_y=by + lane_h + 6, lcol=lcol, x1=x1,
                            lane_h=lane_h)

        # ---------- thuoc thoi gian
        if ruler:
            dd.line([s(x0), s(ruler_y), s(x1), s(ruler_y)],
                    fill=EDGE + (255,), width=s(2))
            for i, lab in enumerate(ruler):
                tx = x0 + (x1 - x0) * (i / max(1, len(ruler) - 1))
                dd.line([s(tx), s(ruler_y), s(tx), s(ruler_y + 12)],
                        fill=EDGE_HI + (255,), width=s(2))
                lf = typo.mono_font(20, 500)
                ttext(base, lab, lf, DIM, ruler_y + 22,
                      cx=min(max(tx, x0 + 24), x1 - 24), track=2.0)

        # ---------- cau ket khi da chay het
        if coll and p >= float(coll):
            q = clamp((p - float(coll)) / 0.10)
            cy = ruler_y + 70
            # PHAI tu thu nho: mot dong cau ket dai hon khung thi bi cat mat
            # chu cuoi, va cau ket bi cat thi ca canh mo phong mat cho chot.
            cf, lines, clh = typo.headline(sp.get("verdict", ""),
                                           CONTENT_W - 40, 96, 74, 44, -2,
                                           "slab_black")
            glow(base, (MARGIN, cy, W - MARGIN, cy + 84), vcol, 70, int(70 * q))
            for i, ln in enumerate(lines[:1]):
                ttext(base, ln, cf, vcol, cy + i * clh, cx=CX, track=-2, p=q,
                      rise=20)
    b.add(fn, dur=max(2.0, b.dur * 0.80), wait=b.dur)


def _verdict(b, txt, y, col, size=76, wait=0.3):
    """Cau ket can giua + ke ngang. Tu keo len neu sap tran vao the phu de."""
    f, lines, lh = typo.headline(txt, CONTENT_W - 40, 220, size, 48, -2.0,
                                 "slab_black")
    h = lh * len(lines)
    if y + h > NOTE_Y - 46:
        y = NOTE_Y - 46 - h

    def fn(base, d, p):
        hline(base, y - 32, EDGE, CX - 150, CX + 150, min(1.0, p * 2))
        for i, ln in enumerate(lines):
            lp = clamp((p - i * 0.12) * 1.5)
            ttext(base, ln, f, col, y + i * lh, cx=CX, track=-2.0, p=lp,
                  rise=20)
    b.add(fn, dur=0.55, wait=wait)


def sc_compare(b, sp, acc):
    """Hai ve canh nhau. Thay phan lon cho dang dung `statement`.

    Ly do ton tai: do tren ba screenplay dau tien, `statement` chiem 32% so canh
    va luon la mot khoi chu lon can giua trong khung ngoac - noi dung khac nhau
    ma hinh giong het nhau. Rat nhieu cho trong so do that ra la SO SANH hai ve
    ("local so voi production", "async so voi tien trinh", "truoc so voi sau"),
    va so sanh thi phai dat canh nhau moi thay.

    Hai ve xep DOC chu khong ngang: khung 9:16 chi rong 960px, chia doi con 460px
    moi ve - chu lon nhat vua duoc khoang 8 ky tu, khong du cho mot con so kem
    nhan. Xep doc thi moi ve duoc tron chieu ngang.
    """
    items = sp["items"][:2]
    ph = int(sp.get("box_h", 250))
    gap = 96 if sp.get("verdict") else 120
    total = ph * 2 + gap
    y0 = STAGE_CY - total / 2 - (46 if sp.get("verdict") else 0)
    boxes = []

    for i, it in enumerate(items):
        by = y0 + i * (ph + gap)
        box = (MARGIN, by, W - MARGIN, by + ph)
        boxes.append(box)
        col = acc_of(it.get("color"), OK if i == 0 else HOT)
        xau = bool(it.get("bad"))

        def fn(base, d, p, box=box, it=it, col=col, xau=xau):
            e = expo_out(p)
            glow(base, box, col, 62, int(46 * e))
            card(base, box, p, fill=SURF, border=EDGE, radius=14)
            brackets(base, (box[0] + 12, box[1] + 12, box[2] - 12, box[3] - 12),
                     col, p, 28, 3)
            if p <= 0.28:
                return
            q = (p - 0.28) / 0.72
            mono(base, it.get("label", ""), (box[0] + 30, box[1] + 26), MUTED,
                 q, 24, 4.5)
            val = str(it.get("value", ""))
            vf = fit_one("grot_black", val, CONTENT_W - 320, 92, 44)
            oy, th = typo.tm(val, vf)
            ttext(base, val, vf, col, (box[1] + box[3]) / 2 - th / 2 + 6,
                  x=box[0] + 30, track=-2, p=q, rise=20)
            if it.get("note"):
                # Ngoac goc chiem o goc duoi phai mot vung 28x28 tinh tu diem
                # inset 12, tuc x >= box[2]-40 va y >= box[3]-40. Nhan phai lui
                # ra ngoai vung do, khong thi chu cham vao ngoac va nhin nhu bi
                # cat mat mot doan.
                nf = typo.mono_font(24, 500)
                nw = track_w(it["note"], nf, 2.5)
                ttext(base, it["note"], nf, DIM, box[3] - 70,
                      x=box[2] - 56 - nw, track=2.5, p=q)
            if xau:
                # gach ngang qua gia tri: "ve nay la cai sai"
                yy = (box[1] + box[3]) / 2 + 10
                ww = track_w(val, vf, -2)
                ImageDraw.Draw(base).line(
                    [s(box[0] + 26), s(yy), s(box[0] + 36 + ww * expo_out(q)),
                     s(yy)], fill=HOT + (255,), width=s(6))
        b.add(fn, dur=0.55, wait=0.36)

    # dau noi giua hai ve - cho biet day la mot phep so sanh, khong phai hai y roi
    mid = (boxes[0][3] + boxes[1][1]) / 2

    def fn_v(base, d, p):
        e = expo_out(p)
        dd = ImageDraw.Draw(base)
        # Ke phai dung TREN chu, khong chay xuyen qua no. `mid - 16` la dinh
        # khung dong chu nen ke chi duoc keo toi mid - 34.
        y_ke = boxes[0][3] + 16
        dd.line([s(CX), s(y_ke), s(CX), s(y_ke + (mid - 34 - y_ke) * e)],
                fill=EDGE_HI + (255,), width=s(3))
        if p > 0.5 and sp.get("vs"):
            f = typo.mono_font(26, 700)
            ttext(base, sp["vs"], f, MUTED, mid - 16, cx=CX, track=5.0,
                  p=(p - 0.5) / 0.5)
    b.add(fn_v, dur=0.4, wait=0.24)

    if sp.get("verdict"):
        _verdict(b, sp["verdict"], boxes[1][3] + 74,
                 acc_of(sp.get("verdict_color"), HOT))


def sc_multiply(b, sp, acc):
    """MO PHONG ⭐ - MOT thanh NHIEU. Tra loi cau "nhan len bao nhieu".

    `gantt` tra loi "KHI NAO" - hai viec chong len nhau theo thoi gian. Nhung
    nhieu co che khong noi ve thoi gian ma ve SO LUONG bung ra: N+1 query,
    re-render, retry bao, fan-out. Ep chung vao hai lane ngang la ke sai chuyen,
    va la ly do ba screenplay dau tien nhin giong het nhau.

    Hinh dang o day: mot o NGUON o tren, ben duoi la luoi o nho day dan tung
    cai mot, kem bo dem chay len. Mat nguoi xem bam theo luoi day len - dung cai
    cam giac "no cu the ma nhan mai".

    O co TU CO lai cho vua het `count`, chu khong cat o mot con so co dinh. Cat
    roi ghi "+47 nua" la pha hong chinh cai duy nhat canh nay lam duoc: cho nguoi
    xem NHIN THAY khoi luong thay vi DOC no. Chi khi o tut duoi CH_MIN - tuc luoi
    da thanh mang mau khong dem duoc - moi cat va ghi phan con lai.
    """
    src = sp.get("source") or {}
    tong = int(sp.get("count", 20))
    cols = int(sp.get("cols", 12))

    sx0, sx1 = MARGIN, W - MARGIN
    src_h = 118
    src_y = STAGE_TOP + 6
    cnt_w = 300
    box_src = (sx0, src_y, sx1 - cnt_w - 22, src_y + src_h)
    box_cnt = (sx1 - cnt_w, src_y, sx1, src_y + src_h)

    grid_y = src_y + src_h + 74
    # Chua cho hang "+N nua" khi luoi bi cat: no ve NGAY DUOI luoi, va cau ket
    # thi bat dau o STAGE_BOTTOM - 120. Khong tru them thi hai thu cham nhau -
    # da thay o so 91 (count 1.234.568, luoi cat con ~1.040 o).
    grid_h = STAGE_BOTTOM - (182 if sp.get("verdict") else 150) - grid_y
    gap = 8
    CH_MAX, CH_MIN = 38.0, 11.0
    cw = (CONTENT_W - gap * (cols - 1)) / cols

    # So hang CAN de ve het, va so hang VE DUOC neu o co lai toi CH_MIN. Lay cai
    # nho hon. `max_chip` chi con la tran cung tuy chon cho screenplay nao muon
    # co y cat.
    rows_can = max(1, (tong + cols - 1) // cols)
    rows_vua = max(1, int((grid_h + gap) // (CH_MIN + gap)))
    rows = min(rows_can, rows_vua)
    n_ve = min(tong, rows * cols)
    if sp.get("max_chip"):
        n_ve = min(n_ve, int(sp["max_chip"]))
        rows = max(1, (n_ve + cols - 1) // cols)
    ch = min(CH_MAX, (grid_h - gap * (rows - 1)) / rows)

    def fn(base, d, p):
        dd = ImageDraw.Draw(base)
        # --- o nguon: mot cau duy nhat, xuat hien truoc
        q = clamp(p / 0.16)
        card(base, box_src, q, fill=SURF, border=EDGE, radius=12)
        if q > 0.3:
            mono(base, src.get("label", "MỘT CÂU"), (box_src[0] + 26, src_y + 26),
                 MUTED, 1.0, 22, 4.0)
            cf = typo.mono_font(30, 500)
            ttext(base, src.get("text", ""), cf, FG, src_y + 62,
                  x=box_src[0] + 26, track=0.5)

        # --- bo dem
        hien = int(clamp((p - 0.16) / 0.78) * tong)
        col = HOT if hien > cols else acc
        if hien:
            glow(base, box_cnt, col, 56, min(70, 20 + hien // 3))
        card(base, box_cnt, q, fill=SURF, border=EDGE, radius=12)
        brackets(base, (box_cnt[0] + 10, box_cnt[1] + 10, box_cnt[2] - 10,
                        box_cnt[3] - 10), col if hien else EDGE_HI, q, 24, 3)
        bcx = (box_cnt[0] + box_cnt[2]) / 2
        kf = typo.mono_font(22, 700)
        ttext(base, sp.get("counter_key", "SỐ CÂU"), kf, MUTED, src_y + 24,
              cx=bcx, track=4.0, p=q)
        # `_num_vi` chu khong `str`: cau ket cua cung canh nay in
        # "1.234.568" nen bo dem in "1234568" la hai cach viet cho cung mot
        # con so tren cung mot khung hinh.
        sv = _num_vi(hien)
        vf = fit_one("grot_black", sv, cnt_w - 60, 66, 34)
        ttext(base, sv, vf, col, src_y + 54, cx=bcx, track=-1.5, p=q)

        # --- luoi: moi o la mot lan lam lai cung mot viec
        if p <= 0.16:
            return
        gp = clamp((p - 0.16) / 0.78)
        day = int(gp * n_ve)
        cf2 = typo.mono_font(18, 500)
        for i in range(day):
            r, c = divmod(i, cols)
            x = MARGIN + c * (cw + gap)
            y = grid_y + r * (ch + gap)
            # O DAU TIEN luon mau COOL, phan con lai HOT. Day la ca y nghia cua
            # canh: mot cau hop le, so con lai deu la thua. Dung `acc` cho o dau
            # thi screenplay nao dat `accent: hot` se lam hai mau trung nhau va
            # mat sach y - da vap dung loi do.
            cc = COOL if i == 0 else HOT
            dd.rounded_rectangle([s(x), s(y), s(x + cw), s(y + ch)],
                                 radius=s(5), fill=cc + (255,))
        if tong > n_ve and gp > 0.9:
            con = tong - n_ve
            ttext(base, f"+{_num_vi(con)} nữa", cf2, HOT,
                  grid_y + rows * (ch + gap) + 12, cx=CX, track=2.0)
        if sp.get("chip") and day:
            mono(base, sp["chip"], (MARGIN, grid_y - 34), MUTED, 1.0, 22, 3.5)

        # --- cau ket
        va = sp.get("verdict_at")
        if va and p >= float(va):
            qq = clamp((p - float(va)) / 0.10)
            cy = STAGE_BOTTOM - 120
            cf3, lines, clh = typo.headline(sp.get("verdict", ""), CONTENT_W - 40,
                                            96, 74, 44, -2, "slab_black")
            vcol = acc_of(sp.get("verdict_color"), HOT)
            glow(base, (MARGIN, cy, W - MARGIN, cy + 84), vcol, 70, int(70 * qq))
            ttext(base, lines[0], cf3, vcol, cy, cx=CX, track=-2, p=qq, rise=20)
    b.add(fn, dur=max(2.0, b.dur * 0.80), wait=b.dur)


def _num_vi(v):
    """1200 -> "1.200". Tieng Viet dung cham lam dau phan cach hang nghin."""
    return f"{int(round(v)):,}".replace(",", ".")


def _stat_box(base, box, key, val, col, p, key_size=22, val_size=56):
    """O so nho co ngoac goc - dung chung cho `queue` va `topology`."""
    card(base, box, p, fill=SURF, border=EDGE, radius=12)
    brackets(base, (box[0] + 10, box[1] + 10, box[2] - 10, box[3] - 10),
             col, p, 22, 3)
    bcx = (box[0] + box[2]) / 2
    # Be ngang tru 96 chu khong tru 44: ngoac goc an vao 10 + 22 moi ben, chu
    # cham vao ngoac la nhin nhu bi cat.
    #
    # Xep NGUOC tu duoi len va deu tinh theo DAY CHU IN (`typo.tm`) chu khong
    # theo dinh khung font: "120/giay" co net thong xuong, "1.150" thi khong,
    # nen canh theo dinh la hai o cao thap khac nhau va nhan de chong len so.
    vf = fit_one("grot_black", val, box[2] - box[0] - 96, val_size, 28)
    voy, vth = typo.tm(val, vf)
    vy = box[3] - 24 - vth          # `ttext` dat dinh muc tai y, khong tru voy
    ttext(base, val, vf, col, vy, cx=bcx, track=-1.5, p=p)

    kf = typo.mono_font(key_size, 700)
    koy, kth = typo.tm(key, kf)
    ttext(base, key, kf, MUTED, vy - 14 - kth, cx=bcx, track=4.0,
          p=p)


def sc_queue(b, sp, acc):
    """MO PHONG - DO SAU HANG DOI THEO THOI GIAN. Cau hoi: "don u toi dau".

    `gantt` tra loi KHI NAO, `multiply` tra loi BAO NHIEU CAI. Con day tra loi
    BAO NHIEU THEO THOI GIAN - thu ma ca hai loai kia deu khong ke duoc: mot
    duong di len va khong bao gio xuong. Hang doi day dan, retry don lai, bo nho
    ro ri, backlog Kafka deu la hinh nay.

    Day cung la HINH DANG duy nhat trong theme khong phai hop hay thanh ngang,
    nen no pha the don dieu manh hon bat ky mau sac nao.

    `curve` la so DO DUOC, khai thang trong screenplay - khong noi suy tu mot
    cong thuc, vi cong thuc thi de vien so cho dep. Xem Y-TUONG.md.
    """
    curve = [float(x) for x in sp["curve"]]
    n = len(curve)
    cap = sp.get("capacity")
    ymax = float(sp.get("ymax") or max(max(curve), cap or 0) * 1.12)

    top = STAGE_TOP + 6
    box_h = 132          # du cho nhan mono + so co net thong xuong, xem _stat_box
    gap = 20
    bw = (CONTENT_W - gap * 2) / 3
    boxes = [(MARGIN + i * (bw + gap), top, MARGIN + i * (bw + gap) + bw,
              top + box_h) for i in range(3)]

    # Bieu do: chua nhan truc y ben trai nen phai thut vao.
    ax0, ax1 = MARGIN + 96, W - MARGIN
    # Chua 190 chu khong 168: duoi truc x con mot hang nhan moc thoi gian nua
    # roi moi toi cau ket.
    ay1 = STAGE_BOTTOM - (190 if sp.get("verdict") else 40)
    ay0 = top + box_h + 96
    ah = ay1 - ay0

    def yof(v):
        return ay1 - clamp(v / ymax) * ah

    ycap = yof(cap) if cap else None
    inb = sp.get("inbox") or {}
    outb = sp.get("outbox") or {}

    def fn(base, d, p):
        dd = ImageDraw.Draw(base)
        q = clamp(p / 0.14)
        gp = clamp((p - 0.14) / 0.76)

        # --- vi tri hien tai tren duong cong, noi suy tuyen tinh giua hai moc
        t = gp * (n - 1)
        i0 = min(n - 1, int(t))
        i1 = min(n - 1, i0 + 1)
        cur = curve[i0] + (curve[i1] - curve[i0]) * (t - i0)

        # --- ba o so: vao / dang cho / ra
        _stat_box(base, boxes[0], inb.get("label", "VÀO"),
                  str(inb.get("value", "")), acc_of(inb.get("color"), COOL), q)
        # Duoi nguong XANH, tren nguong DO. Ca canh nay chi co mot khoanh khac
        # dang nho la luc vuot nguong - de o so cung mau tu dau la xoa mat no.
        dcol = HOT if (cap and cur > cap) else COOL
        _stat_box(base, boxes[1], sp.get("depth_key", "ĐANG CHỜ"),
                  _num_vi(cur), dcol, q, val_size=60)
        if cur:
            glow(base, boxes[1], dcol, 56, min(72, 22 + int(cur / ymax * 60)))
        _stat_box(base, boxes[2], outb.get("label", "RA"),
                  str(outb.get("value", "")), acc_of(outb.get("color"), MUTED), q)

        if p <= 0.14:
            return

        # --- khung bieu do: ba ke ngang + nhan truc y
        lf = typo.mono_font(20, 500)
        for k in (0.0, 0.5, 1.0):
            gy = ay1 - k * ah
            hline(base, gy, EDGE if k else EDGE_HI, ax0, ax1, q, 2)
            lb = _num_vi(ymax * k)
            ttext(base, lb, lf, DIM, gy - 11, x=ax0 - 20 - track_w(lb, lf, 2.0),
                  track=2.0, p=q)

        # --- nguong: ke dut, ve truoc khi duong cong cham toi
        if cap:
            cf = typo.mono_font(20, 700)
            step = 22
            x = ax0
            while x < ax1:
                dd.line([s(x), s(ycap), s(min(x + 12, ax1)), s(ycap)],
                        fill=HOT + (170,), width=s(2))
                x += step
            lb = sp.get("cap_label", "NGƯỠNG")
            mono(base, f"{lb} {_num_vi(cap)}", (ax0 + 8, ycap - 42), HOT, q, 20,
                 3.0)

        # --- mien duoi duong cong. Lay mau day 4px mot de khi cat theo nguong
        # khong bi rang cua o cho duong cat qua ke dut.
        xcur = ax0 + (ax1 - ax0) * gp
        pts = []
        x = ax0
        while x < xcur:
            tt = (x - ax0) / (ax1 - ax0) * (n - 1)
            j0 = min(n - 1, int(tt))
            j1 = min(n - 1, j0 + 1)
            v = curve[j0] + (curve[j1] - curve[j0]) * (tt - j0)
            pts.append((x, yof(v)))
            x += 4
        pts.append((xcur, yof(cur)))
        if len(pts) > 2:
            lay = Image.new("RGBA", base.size, (0, 0, 0, 0))
            ld = ImageDraw.Draw(lay)
            ld.polygon([(s(a), s(bb)) for a, bb in pts]
                       + [(s(xcur), s(ay1)), (s(ax0), s(ay1))],
                       fill=COOL + (52,))
            if ycap is not None:
                # min(y, ycap) => phan nam DUOI nguong tu triet tieu thanh mot
                # dai cao 0, chi con phan vuot len tren la con dien tich.
                ld.polygon([(s(a), s(min(bb, ycap))) for a, bb in pts]
                           + [(s(xcur), s(ycap)), (s(ax0), s(ycap))],
                           fill=HOT + (96,))
            base.alpha_composite(lay)

            # duong vien: doi mau ngay tai cho cat nguong
            for k in range(len(pts) - 1):
                a, bb = pts[k]
                c, e = pts[k + 1]
                lc = HOT if (ycap is not None and (bb + e) / 2 < ycap) else COOL
                dd.line([s(a), s(bb), s(c), s(e)], fill=lc + (255,), width=s(4))
            dd.ellipse([s(xcur - 9), s(yof(cur) - 9), s(xcur + 9),
                        s(yof(cur) + 9)], fill=dcol + (255,))

        # --- moc DINH, dung yen sau khi duong cong di qua.
        #
        # O so chi hien gia tri HIEN TAI, nen khung cuoi cua mot duong cong co
        # rut xuong lai bao "9" trong khi ca canh noi ve dinh 70. Nguoi xem dung
        # hinh o giay cuoi se doc nham. Moc nay o lai de hai con so cung co mat.
        i_dinh = max(range(n), key=lambda k: curve[k])
        p_dinh = i_dinh / (n - 1)
        if gp >= p_dinh and n > 1:
            qd = clamp((gp - p_dinh) / 0.08)
            xd = ax0 + (ax1 - ax0) * p_dinh
            yd = yof(curve[i_dinh])
            dd.ellipse([s(xd - 11), s(yd - 11), s(xd + 11), s(yd + 11)],
                       outline=HOT + (255,), width=s(3))
            df = typo.mono_font(22, 700)
            lb = f"ĐỈNH {_num_vi(curve[i_dinh])}"
            ttext(base, lb, df, HOT, yd - 52,
                  cx=min(max(xd, ax0 + 80), ax1 - 80), track=3.0, p=qd)

        # --- nhan truc x
        marks = sp.get("marks") or []
        if marks:
            mf = typo.mono_font(20, 500)
            for k, mk in enumerate(marks):
                mx = ax0 + (ax1 - ax0) * (k / max(1, len(marks) - 1))
                mx = min(mx, ax1 - track_w(str(mk), mf, 2.5))
                ttext(base, str(mk), mf, DIM, ay1 + 16, x=mx, track=2.5, p=q)

        if sp.get("chip"):
            mono(base, sp["chip"], (ax0, ay0 - 36), MUTED, q, 22, 3.5)

        va = sp.get("verdict_at")
        if va and p >= float(va):
            qq = clamp((p - float(va)) / 0.10)
            cy = STAGE_BOTTOM - 120
            vf, lines, _ = typo.headline(sp.get("verdict", ""), CONTENT_W - 40,
                                         96, 74, 44, -2, "slab_black")
            vcol = acc_of(sp.get("verdict_color"), HOT)
            glow(base, (MARGIN, cy, W - MARGIN, cy + 84), vcol, 70, int(70 * qq))
            ttext(base, lines[0], vf, vcol, cy, cx=CX, track=-2, p=qq, rise=20)
    b.add(fn, dur=max(2.0, b.dur * 0.80), wait=b.dur)


def sc_topology(b, sp, acc):
    """MO PHONG - O DAU. Cac tang cua he thong, mot goi tin chay qua.

    Ba loai mo phong kia deu tra loi cau hoi ve LUONG hoac THOI GIAN. Loai nay
    tra loi cau con lai: viec do XAY RA O TANG NAO, va quan trong hon - no
    KHONG toi duoc tang nao.

    Goi tin chay tu tang `from` toi tang `to`. Tang nao no toi thi sang len theo
    mau rieng; tang nao no khong toi thi mo di va deo nhan `miss_tag`. Chinh cai
    khoang khong cham toi duoc moi la noi dung cua canh, nen dung dat `to` bang
    tang cuoi neu khong co gi bi bo sot.
    """
    nodes = sp["nodes"]
    n = len(nodes)
    i_to = int(sp.get("to", n - 1))
    i_from = int(sp.get("from", 0))

    spine_x = MARGIN + 48
    x0, x1 = MARGIN + 110, W - MARGIN
    top = STAGE_TOP + 6
    bot = STAGE_BOTTOM - (168 if sp.get("verdict") else 30)
    gap = 20
    nh = (bot - top - gap * (n - 1)) / n
    cy_of = [top + i * (nh + gap) + nh / 2 for i in range(n)]
    miss = sp.get("miss_tag", "KHÔNG TỚI")

    def fn(base, d, p):
        dd = ImageDraw.Draw(base)
        # 0 -> 0,34 the hien ra lan luot; 0,34 -> 0,86 goi tin chay
        tp = clamp((p - 0.34) / 0.52)
        y_goi = cy_of[i_from] + (cy_of[i_to] - cy_of[i_from]) * tp

        # --- song spine + doan da di qua
        dd.line([s(spine_x), s(cy_of[0]), s(spine_x), s(cy_of[-1])],
                fill=EDGE + (255,), width=s(3))
        if tp > 0:
            dd.line([s(spine_x), s(cy_of[i_from]), s(spine_x), s(y_goi)],
                    fill=acc + (255,), width=s(5))

        for i, nd in enumerate(nodes):
            q = clamp((p - i * 0.05) / 0.28)
            if q <= 0:
                continue
            y = top + i * (nh + gap)
            box = (x0, y, x1, y + nh)
            # `pos` la vi tri goi tin do bang CHI SO tang, khong phai pixel - so
            # sanh o day roi mo ra pixel de nhan `sang` doi dung luc cham sang
            # di ngang qua the.
            pos = i_from + tp * (i_to - i_from)
            trong_duong = min(i_from, i_to) <= i <= max(i_from, i_to)
            toi = i_from <= i <= pos if i_to >= i_from else pos <= i <= i_from
            col = acc_of(nd.get("color"), COOL) if trong_duong else DIM
            sang = toi and trong_duong

            card(base, box, q, fill=SURF,
                 border=EDGE_HI if sang else EDGE, radius=12,
                 lit=col if sang else None)
            dd.ellipse([s(spine_x - 11), s(cy_of[i] - 11), s(spine_x + 11),
                        s(cy_of[i] + 11)],
                       fill=(col if sang else EDGE) + (255,),
                       outline=BG + (255,), width=s(4))

            # Ten cao 40 ve tu y+20 thi net thong xuong cham day y+68; dong phu
            # phai dat duoi moc do, khong phai canh theo day the.
            nf = fit_one("grot_black", nd["name"], (x1 - x0) * 0.60, 40, 26)
            ttext(base, nd["name"], nf, FG if sang else MUTED, y + 20,
                  x=x0 + 26, track=-0.5, p=q)
            if nd.get("sub"):
                mono(base, nd["sub"], (x0 + 26, y + nh - 36),
                     MUTED if sang else DIM, q, 21, 3.0)

            # nhan ben phai: `tag` khi goi tin toi, `miss_tag` khi khong
            if not trong_duong and tp > 0.9:
                tf = typo.mono_font(21, 700)
                ttext(base, miss, tf, HOT, y + nh / 2 - 12,
                      x=x1 - 26 - track_w(miss, tf, 3.0), track=3.0)
            elif nd.get("tag") and sang:
                tf = fit_one("grot_black", str(nd["tag"]), 240, 46, 26)
                tw = track_w(str(nd["tag"]), tf, -1.0)
                ttext(base, str(nd["tag"]), tf, col, y + nh / 2 - 26,
                      x=x1 - 26 - tw, track=-1.0)

        # --- goi tin: cham sang chay doc song spine
        if 0 < tp < 1.0:
            glow(base, (spine_x - 26, y_goi - 26, spine_x + 26, y_goi + 26),
                 acc, 46, 90)
            dd.ellipse([s(spine_x - 13), s(y_goi - 13), s(spine_x + 13),
                        s(y_goi + 13)], fill=acc + (255,))
        if sp.get("packet") and 0.3 < p < 0.92:
            mono(base, sp["packet"], (MARGIN, STAGE_TOP - 34), acc, 1.0, 22, 3.5)

        va = sp.get("verdict_at")
        if va and p >= float(va):
            qq = clamp((p - float(va)) / 0.10)
            cy = STAGE_BOTTOM - 120
            vf, lines, _ = typo.headline(sp.get("verdict", ""), CONTENT_W - 40,
                                         96, 74, 44, -2, "slab_black")
            vcol = acc_of(sp.get("verdict_color"), HOT)
            glow(base, (MARGIN, cy, W - MARGIN, cy + 84), vcol, 70, int(70 * qq))
            ttext(base, lines[0], vf, vcol, cy, cx=CX, track=-2, p=qq, rise=20)
    b.add(fn, dur=max(2.0, b.dur * 0.80), wait=b.dur)



# ============================================================ MO PHONG (moi)
#
# Bon loai duoi day sinh ra tu mot lan RA SOAT 292 chu de trong `files/`. Cach
# chon khong phai theo cam giac "hinh nay dep" ma theo dem: moi chu de duoc gan
# CAU HOI ma canh mo phong cua no phai tra loi, roi dem xem cau hoi nao lap lai
# nhieu ma bon loai co san (`gantt` `multiply` `queue` `topology`) khong tra
# duoc.
#
#   BAO NHIEU O MOI MUC     ~40 chu de  ->  `cot`      (khong co loai nao lam)
#   CAI NAO CHO CAI NAO     ~25 chu de  ->  `thac`     (`gantt` chi 2 lane)
#   MOI BAN SAO GIU GI      ~12 chu de  ->  `ban_sao`  (`counters` la tinh)
#   NHIEU CAI RA MOT        ~6  chu de  ->  `gop`      (nguoc cua `multiply`)
#
# Ba loai dau deu tung bi EP vao `queue` hoac `gantt` trong ban khung tu sinh,
# va ca ba lan hinh ve deu noi mot chuyen khac loi doc - dung cai bay da ghi o
# VIET-KICH-BAN.md muc "Bay lon nhat".


def _thang(gia_tri, kieu, day=None, dinh=None):
    """Tra ve ham doi gia tri -> ti le 0..1 tren truc.

    `log` khong phai de cho dep. Mua BAM VA BI MAT co so do 824.768 lan/giay
    canh 3,0 lan/giay: tren truc tuyen tinh thi cot thu hai cao 0,0004 pixel,
    tuc bien mat. Truc log giu duoc CA HAI cot nhin thay duoc, va chenh lech
    van doc ra vi nhan tren cot la so that.

    Doi lai: truc log KHONG duoc dung khi nguoi xem se so BE CAO hai cot voi
    nhau (cot cao gap doi khong con nghia la gia tri gap doi). Nen `sc_cot` in
    them nhan `TRUC LOG` ngay canh truc de khong ai doc nham.
    """
    duong = [abs(v) for v in gia_tri if v]
    hi = float(dinh) if dinh else (max(duong) if duong else 1.0)
    if kieu == "log":
        lo = float(day) if day else (min(duong) / 12.0 if duong else 0.1)
        lo = max(lo, 1e-12)
        import math
        la, lb = math.log10(lo), math.log10(max(hi, lo * 1.0001))

        def f(v):
            if v <= 0:
                return 0.0
            return clamp((math.log10(max(v, lo)) - la) / (lb - la))
        return f, hi, lo

    def g(v):
        return clamp(v / hi) if hi else 0.0
    return g, hi, 0.0


def sc_cot(b, sp, acc):
    """MO PHONG - BAO NHIEU O MOI MUC. Cot dung canh nhau, moc len tung cai.

    Cau hoi rieng cua loai nay: mot dai luong doi theo mot BIEN KHONG PHAI THOI
    GIAN. So dong trong bang, so vong lap, tham so cau hinh, co anh, ham bam nao.
    `queue` cung ve mien nhung truc x cua no la thoi gian va no bat buoc phai di
    len - ep mot bang "1 nghin dong / 100 nghin / 5 trieu" vao do la noi sai.

    Cot moc len LAN LUOT chu khong cung luc: mat nguoi xem doc tung buoc nhay,
    va cot cuoi - cot dat nhat - roi vao dung luc loi doc noi ve no.

    Truong:
      truc      nhan doc canh truc y
      thang     `tuyen` (mac dinh) hoac `log`
      day dinh  chan duoi / dinh truc, chi dung khi muon ep khung
      cot[]     { nhan, gia, value, color, note }
                `gia` la SO (chieu cao), `value` la CHU hien tren cot
      ty_le     { a, b, nhan } - ngoac noi hai cot, ghi ti le giua chung
      nguong    { gia, nhan } - ke dut ngang, muc tran hoac muc gioi han
      ghi       chip mono nho phia tren, thuong la dieu kien do
    """
    cot = sp.get("cot") or []
    if not cot:
        return
    gia = [float(c.get("gia", 0)) for c in cot]
    kieu = str(sp.get("thang", "tuyen")).lower()
    yof01, hi, lo = _thang(gia, kieu, sp.get("day"), sp.get("dinh"))

    ax0, ax1 = MARGIN + 26, W - MARGIN
    # Hai hang nhan phia tren truc (`truc` + huy hieu log, roi `ghi`), rieng mot
    # hang cho nhan ti le, roi moi toi vung ve.
    ay0 = STAGE_TOP + 128
    # Duoi truc con hai hang: nhan cot (co the 2 dong) roi cau ket.
    ay1 = STAGE_BOTTOM - (250 if sp.get("verdict") else 150)
    ah = ay1 - ay0
    # CHUA 82% chieu cao: 18% con lai la cho cua NHAN GIA TRI ve phia tren cot.
    # De cot cao het khung thi nhan gia tri cua cot cao nhat de len nhan truc -
    # da thay dung loi do o ban thu dau tien.
    CAO = 0.82
    n = len(cot)
    slot = (ax1 - ax0) / n
    cw = min(150.0, slot * 0.60)

    def fn(base, d, p):
        dd = ImageDraw.Draw(base)
        q = clamp(p / 0.12)

        # --- truc: mot ke day, ba ke mo. Ke mo la de mat uoc luong duoc chieu
        # cao; bo chung thi cot chi con la ba khoi mau canh nhau.
        hline(base, ay1, EDGE_HI, ax0 - 20, ax1, q, 2)
        for k in (0.25, 0.5, 0.75, 1.0):
            hline(base, ay1 - k * ah, EDGE, ax0 - 20, ax1, q, 1)
        if sp.get("truc"):
            mono(base, sp["truc"], (ax0 - 20, STAGE_TOP + 8), MUTED, q, 21, 3.5)
        if kieu == "log":
            # Huy hieu nay BAT BUOC khi thang log: tren truc log thi cot cao gap
            # doi khong con nghia la gia tri gap doi, va nguoi xem quen doc bieu
            # do tuyen tinh se doc nham neu khong co dong nay.
            lb = "TRỤC LOG"
            lf = typo.mono_font(19, 700)
            ttext(base, lb, lf, GOLD, STAGE_TOP + 8,
                  x=ax1 - track_w(lb, lf, 3.0), track=3.0, p=q)
        if sp.get("ghi"):
            mono(base, sp["ghi"], (ax0 - 20, STAGE_TOP + 44), DIM, q, 21, 3.5)

        # --- cot: moc len lan luot. 0,12..0,86 chia deu cho n cot, moi cot
        # dung 0,60 phan khe cua no de moc nen co nhip nghi giua hai cot.
        khe = 0.74 / max(1, n)
        toa = []
        for i, c in enumerate(cot):
            t0 = 0.12 + i * khe
            gp = clamp((p - t0) / (khe * 0.72))
            cx = ax0 + slot * (i + 0.5)
            h = yof01(gia[i]) * ah * CAO * ease_in_out(gp)
            col = acc_of(c.get("color"), acc if i == 0 else HOT)
            toa.append((cx, ay1 - h, col, gp))
            if h < 2:
                continue
            if c.get("color") == "hot" or (i == n - 1 and gp > 0.5):
                glow(base, (cx - cw / 2, ay1 - h, cx + cw / 2, ay1), col,
                     46, int(52 * gp))
            dd.rounded_rectangle([s(cx - cw / 2), s(ay1 - h), s(cx + cw / 2),
                                 s(ay1)], radius=s(6), fill=col + (255,))

        # --- nguong: ke dut ngang. Voi cot thi nguong hay la mot TRAN - cho ma
        # gia tri bi cat cut - nen no phai ve TRUOC nhan gia tri de nhan nam
        # tren, va ve SAU cot de duong ke con nhin thay tren than cot.
        ng = sp.get("nguong")
        if ng and p > 0.16:
            qn = clamp((p - 0.16) / 0.14)
            gy = ay1 - yof01(float(ng.get("gia", 0))) * ah * CAO
            x = ax0 - 20
            while x < ax1:
                dd.line([s(x), s(gy), s(min(x + 13, ax1)), s(gy)],
                        fill=GOLD + (int(200 * qn),), width=s(2))
                x += 24
            # Nhan ngưỡng nam TREN chinh duong ke, trong mot vien co nen dac.
            # Da thu dat no phia tren duong ke va bi de len nhan gia tri cua cot
            # cham tran - ma do lai chinh la cot dang duoc noi toi. Dat duoi
            # duong ke thi de len than cot. Vien co nen dac la cach duy nhat
            # khong phu thuoc vao cot nao dang cao bao nhieu.
            lb = str(ng.get("nhan", "NGƯỠNG"))
            lf = typo.mono_font(20, 700)
            lw = track_w(lb, lf, 3.0)
            # Dat vien tren khe co KHOANG TRONG LON NHAT phia tren cot, tuc khe
            # ma cot cua no thap hon nguong nhieu nhat. Neo cung mot phia (phai
            # hoac trai) thi luon co truong hop cot cham tran nam dung o phia
            # do - va cot cham tran chinh la cot dang duoc noi toi.
            khe = min(range(n), key=lambda i: yof01(gia[i]))
            cx_ng = ax0 + slot * (khe + 0.5)
            px0 = min(max(cx_ng - lw / 2 - 12, ax0), ax1 - lw - 24)
            card(base, (px0, gy - 19, px0 + lw + 24, gy + 19), qn, fill=BG,
                 border=GOLD, radius=9, width=2)
            ttext(base, lb, lf, GOLD, gy - 11, x=px0 + 12, track=3.0, p=qn)

        # --- chu ve SAU cung: cot khong bao gio de len so
        for i, c in enumerate(cot):
            cx, ty, col, gp = toa[i]
            if gp <= 0.45:
                continue
            qv = clamp((gp - 0.45) / 0.35)
            val = str(c.get("value", _num_vi(gia[i])))
            vf = fit_one("grot_black", val, slot - 12, 52, 26)
            ttext(base, val, vf, col, ty - 46, cx=cx, track=-1.0, p=qv)
            # Co chu cua nhan phai TU THU theo so cot. `sk.wrap` ngat dong duoc
            # nhung khong cat duoc mot TU dai hon khe, va `ttext` khong clip -
            # nen o 5 cot thi nhan cua hai cot canh nhau dinh vao nhau. Da thay
            # dung loi do o so 96 truoc khi ha co chu.
            nhan = str(c.get("nhan", ""))
            for sz in (21, 19, 17, 15):
                nf = typo.mono_font(sz, 700)
                dong = sk.wrap(nhan, nf, slot - 14)[:2]
                if all(track_w(x, nf, 2.0) <= slot - 10 for x in dong):
                    break
            for j, ln in enumerate(dong):
                ttext(base, ln, nf, MUTED if j else FG, ay1 + 18 + j * 26,
                      cx=cx, track=2.0, p=qv)
            if c.get("note"):
                mf = typo.mono_font(19, 500)
                ttext(base, str(c["note"]), mf, DIM, ay1 + 74, cx=cx,
                      track=2.0, p=qv)

        # --- ngoac ti le giua hai cot. Day la cho ca canh chot lai: khong phai
        # "cot nay cao hon" ma "cao hon BAO NHIEU LAN".
        # Ngoac dat o hang RIENG phia tren vung ve, khong bam theo dinh cot: bam
        # theo dinh cot thi cot cao nhat day ngoac ra ngoai khung, con cot thap
        # thi ngoac cat ngang qua cot ben canh. Ca hai da thay o ban thu dau.
        tl = sp.get("ty_le")
        if tl and p > 0.80:
            qt = clamp((p - 0.80) / 0.12)
            ia, ib = int(tl.get("a", 0)), int(tl.get("b", n - 1))
            if 0 <= ia < n and 0 <= ib < n:
                xa, xb = toa[ia][0], toa[ib][0]
                yb = ay0 - 16
                x0b, x1b = min(xa, xb), max(xa, xb)
                dd.line([s(x0b), s(yb), s(x0b + (x1b - x0b) * qt), s(yb)],
                        fill=GOLD + (255,), width=s(3))
                for xx in (x0b, x1b):
                    dd.line([s(xx), s(yb), s(xx), s(yb + 14)],
                            fill=GOLD + (255,), width=s(3))
                tf = typo.mono_font(24, 700)
                ttext(base, str(tl.get("nhan", "")), tf, GOLD, yb - 40,
                      cx=(x0b + x1b) / 2, track=3.0, p=qt)

        va = sp.get("verdict_at")
        if va and p >= float(va):
            qq = clamp((p - float(va)) / 0.10)
            cy = STAGE_BOTTOM - 120
            vf, lines, _ = typo.headline(sp.get("verdict", ""), CONTENT_W - 40,
                                         96, 74, 44, -2, "slab_black")
            vcol = acc_of(sp.get("verdict_color"), HOT)
            glow(base, (MARGIN, cy, W - MARGIN, cy + 84), vcol, 70, int(70 * qq))
            ttext(base, lines[0], vf, vcol, cy, cx=CX, track=-2, p=qq, rise=20)
    b.add(fn, dur=max(2.0, b.dur * 0.80), wait=b.dur)


def sc_thac(b, sp, acc):
    """MO PHONG - CAI NAO CHO CAI NAO. Thac nuoc nhieu hang, dong ho chay len.

    `gantt` chi ve HAI lane (`sp["lanes"][:2]`) va dat ten buoc BEN TRONG thanh,
    vi no de doi chieu hai luong. Loai nay giai bai khac: MOT chuoi viec noi
    duoi nhau, va cai dang gia la BAC THANG - moi hang bat dau sau khi hang
    truoc xong, nen tong thoi gian la tong cua tat ca.

    Do la hinh dang cua N+1 query, cua vong lap goi API, cua chuoi TCP bat tay
    cong TLS cong request dau tien, cua waterfall trong DevTools. Ep chung vao
    hai lane thi mat dung cai phai thay: chieu cao cua bac thang.

    Dong ho `tong` chay len theo dau doc la thu bien hinh nay thanh thi nghiem -
    xem docstring dau file bench.py.

    Truong:
      hang[]  { nhan, at, w, color, bad, note }
      ruler[] nhan truc thoi gian
      tong    { key, gia, dv, nhan } - dong ho dem len tu 0 toi `gia`
      con     chip ghi phan khong ve het ("còn 147 lần nữa")
    """
    hang = sp.get("hang") or []
    if not hang:
        return
    hang = hang[:14]
    ruler = sp.get("ruler") or []
    tong = sp.get("tong") or {}

    ro_h = 132 if tong else 0
    ro_y = STAGE_TOP + 6
    gut = 268                       # mang trai cho ten hang
    tx0, tx1 = MARGIN + gut, W - MARGIN
    top = ro_y + ro_h + (46 if tong else 10)
    bot = STAGE_BOTTOM - (262 if (sp.get("verdict") and sp.get("con"))
                          else 216 if sp.get("verdict") else 96)
    n = len(hang)
    rh = min(62.0, (bot - top) / n)
    bh = max(14.0, rh - 14)

    def fn(base, d, p):
        dd = ImageDraw.Draw(base)
        q = clamp(p / 0.12)
        head = tx0 + (tx1 - tx0) * clamp((p - 0.06) / 0.80)
        gp = clamp((p - 0.06) / 0.80)

        # --- dong ho tong
        if tong:
            gia = float(tong.get("gia", 0))
            dv = str(tong.get("dv", ""))
            # `le` = so chu so thap phan. Mac dinh 2 vi dong ho thoi gian ("3,73
            # s") la ca dung nhieu nhat, nhung dong ho DEM (so lan thu, so
            # request) thi "2304,00 lan" doc ra la sai - phai dat `le: 0`.
            le = int(tong.get("le", 2))
            cur = gia * gp
            box = (MARGIN, ro_y, W - MARGIN, ro_y + ro_h)
            col = HOT if gp > 0.55 else acc
            glow(base, box, col, 54, int(20 + 46 * gp))
            hien = (_num_vi(cur) if le <= 0
                    else f"{cur:.{le}f}".replace(".", ","))
            _stat_box(base, box, tong.get("key", "TỔNG THỜI GIAN"),
                      hien + dv, col, q, val_size=64)
            # Nhan phu dat NGOAI hop, trong khe 46px giua hop va hang dau tien.
            # Trong hop khong con cho: `_stat_box` xep khoa va gia tri can giua
            # roi day xuong day, va gia tri co the rong gan het hop.
            if tong.get("nhan"):
                mono(base, str(tong["nhan"]), (MARGIN, ro_y + ro_h + 10), DIM,
                     q, 19, 3.0)

        # --- duong ray mo cho tung hang: mat thay truoc co bao nhieu bac
        for i in range(n):
            y = top + i * rh
            dd.rounded_rectangle([s(tx0), s(y + (rh - bh) / 2), s(tx1),
                                  s(y + (rh + bh) / 2)], radius=s(5),
                                 fill=SURF + (255,), outline=EDGE + (255,),
                                 width=s(1))

        # --- thanh + ten hang
        lf = typo.mono_font(21, 700)
        for i, h in enumerate(hang):
            y = top + i * rh
            by = y + (rh - bh) / 2
            at = float(h.get("at", 0.0))
            w = float(h.get("w", 0.08))
            sx = tx0 + (tx1 - tx0) * at
            sw = (tx1 - tx0) * w
            if head < sx:
                continue
            grow = clamp((head - sx) / max(sw, 1e-6))
            col = HOT if h.get("bad") else acc_of(h.get("color"), COOL)
            if h.get("bad") and grow > 0.2:
                glow(base, (sx, by, sx + sw * grow, by + bh), HOT, 36, 50)
            bar(base, (sx, by, sx + max(sw * grow, 3), by + bh), col, 1.0,
                radius=5, grow="none")
            nhan = str(h.get("nhan", ""))
            ttext(base, nhan[:30], lf, FG if grow > 0.9 else MUTED,
                  y + rh / 2 - typo.tm(nhan[:30], lf)[1] / 2, x=MARGIN,
                  track=1.5)
            # Ghi chu: dat SAU thanh neu con cho, khong thi dat BEN TRONG thanh
            # can le phai. Truoc day chi clamp vao `tx1` nen voi thanh dai gan
            # het truc thi chu bi cat mat nua sau.
            if h.get("note") and grow > 0.95:
                mf = typo.mono_font(19, 500)
                lb = str(h["note"])
                tw = track_w(lb, mf, 2.0)
                if sx + sw + 14 + tw <= tx1:
                    ttext(base, lb, mf, col, y + rh / 2 - 10,
                          x=sx + sw + 14, track=2.0)
                elif sw > tw + 28:
                    ttext(base, lb, mf, BG, y + rh / 2 - 10,
                          x=sx + sw - 14 - tw, track=2.0)

        # --- dau doc quet doc het cot thanh
        dd.line([s(head), s(top - 8), s(head), s(top + n * rh + 8)],
                fill=EDGE_HI + (255,), width=s(2))

        # --- thuoc thoi gian
        ry = top + n * rh + 20
        if ruler:
            dd.line([s(tx0), s(ry), s(tx1), s(ry)], fill=EDGE + (255,),
                    width=s(2))
            rf = typo.mono_font(20, 500)
            for i, lab in enumerate(ruler):
                rx = tx0 + (tx1 - tx0) * (i / max(1, len(ruler) - 1))
                dd.line([s(rx), s(ry), s(rx), s(ry + 10)],
                        fill=EDGE_HI + (255,), width=s(2))
                ttext(base, str(lab), rf, DIM, ry + 20,
                      cx=min(max(rx, tx0 + 24), tx1 - 24), track=2.0)
        # `con` co the dai (no la mot cau, khong phai mot nhan) nen phai ngat
        # dong - `mono()` khong ngat va khong clip, chu cu the chay ra khoi
        # khung. Da thay o so 98.
        if sp.get("con") and gp > 0.9:
            cf = typo.mono_font(21, 600)
            for j, ln in enumerate(wrap_track(str(sp["con"]), cf,
                                              CONTENT_W, 3.5)[:2]):
                mono(base, ln, (MARGIN, ry + 46 + j * 28), HOT, 1.0, 21, 3.5)

        va = sp.get("verdict_at")
        if va and p >= float(va):
            qq = clamp((p - float(va)) / 0.10)
            cy = STAGE_BOTTOM - 120
            vf, lines, _ = typo.headline(sp.get("verdict", ""), CONTENT_W - 40,
                                         96, 74, 44, -2, "slab_black")
            vcol = acc_of(sp.get("verdict_color"), HOT)
            glow(base, (MARGIN, cy, W - MARGIN, cy + 84), vcol, 70, int(70 * qq))
            ttext(base, lines[0], vf, vcol, cy, cx=CX, track=-2, p=qq, rise=20)
    b.add(fn, dur=max(2.0, b.dur * 0.80), wait=b.dur)


def sc_ban_sao(b, sp, acc):
    """MO PHONG - MOI BAN SAO DANG GIU GI. Hai den bon ban sao, moi cai mot so.

    Nhom bug lon nhat cua kho chu de moi la loai "chay dung voi MOT ban, sai
    ngay khi co hai": rate limit dem trong RAM, session trong RAM, cron chay
    tren ba instance, bo dem tu tang. Ca nhom nay co cung mot hinh dang, va
    khong loai nao co san ve duoc no:

      `counters` dung so TINH, khong co gi doi
      `gantt`    hai lane la HAI VIEC, khong phai hai BAN SAO cua cung mot viec
      `ban_sao`  N o giong het nhau, moi o mot gia tri, cong mot o SU THAT

    O `that` la cho ca canh song: ba ban sao moi cai bao 34 trong khi su that la
    102. Khong co o do thi nguoi xem chi thay ba con so nho nho, khong thay
    chuyen gi sai.

    Truong:
      nhan_chung  ten dai luong moi ban sao dang giu
      o[]         { nhan, buoc[{ at, value, state }], note }
      that        { key, value, note } - o su that, ve to hon, dat rieng
      nguong      { value, nhan } - muc dat ra, de doi chieu voi `that`
      ruler[]     nhan truc thoi gian
    """
    o = (sp.get("o") or [])[:4]
    if not o:
        return
    that = sp.get("that") or {}
    nguong = sp.get("nguong") or {}
    ruler = sp.get("ruler") or []

    top = STAGE_TOP + 44
    n = len(o)
    gap = 20
    bw = (CONTENT_W - gap * (n - 1)) / n
    bh = 244
    ty = top + bh + 86              # hang duoi: o su that + nguong
    th = 176

    def fn(base, d, p):
        dd = ImageDraw.Draw(base)
        q = clamp(p / 0.12)
        if sp.get("nhan_chung"):
            mono(base, sp["nhan_chung"], (MARGIN, top - 30), MUTED, q, 21, 3.5)

        # --- N ban sao
        for i, oo in enumerate(o):
            bx = MARGIN + i * (bw + gap)
            box = (bx, top, bx + bw, top + bh)
            st = _state_at(oo.get("buoc") or [{"at": 0.0, "value": "—"}], p)
            col = STATES.get((st.get("state") or "").lower(), acc)
            fresh = clamp(1.0 - (p - float(st.get("at", 0.0))) / 0.08)
            if fresh > 0:
                glow(base, box, col, 52, int(70 * fresh))
            card(base, box, q, fill=SURF, border=EDGE, radius=12)
            brackets(base, (box[0] + 10, box[1] + 10, box[2] - 10, box[3] - 10),
                     col if fresh > 0 else EDGE_HI, q, 22, 3)
            bcx = (bx + bx + bw) / 2
            kf = typo.mono_font(21, 700)
            ttext(base, str(oo.get("nhan", "")), kf, MUTED, top + 26, cx=bcx,
                  track=3.5, p=q)
            val = str(st.get("value", ""))
            vf = fit_one("grot_black", val, bw - 56, 78, 32)
            oy, hh = typo.tm(val, vf)
            ttext(base, val, vf, col, top + bh / 2 - hh / 2 + 10, cx=bcx,
                  track=-1.5, p=q)
            if oo.get("note"):
                mf = typo.mono_font(19, 500)
                ttext(base, str(oo["note"]), mf, DIM, top + bh - 40, cx=bcx,
                      track=2.0, p=q)

        # --- o SU THAT: rong hon, mau khac, dat duoi mot khoang ro rang de mat
        # doc nó thanh mot tang khac chu khong phai ban sao thu N+1
        if that:
            qt = clamp((p - 0.34) / 0.16)
            wr = CONTENT_W if not nguong else CONTENT_W * 0.60
            box = (MARGIN, ty, MARGIN + wr, ty + th)
            if qt > 0:
                glow(base, box, HOT, 60, int(64 * qt))
                _stat_box(base, box, str(that.get("key", "SỰ THẬT")),
                          str(that.get("value", "")), HOT, qt, val_size=80)
                # Nhan phu dat TREN hop, khong o day hop: `_stat_box` day gia
                # tri xuong day nen chu o day hop de len con so.
                if that.get("note"):
                    mono(base, str(that["note"]), (MARGIN, ty - 30), DIM, qt,
                         19, 3.0)
        if nguong:
            qn = clamp((p - 0.46) / 0.16)
            bx = MARGIN + CONTENT_W * 0.60 + gap
            box = (bx, ty, W - MARGIN, ty + th)
            if qn > 0:
                _stat_box(base, box, str(nguong.get("nhan", "NGƯỠNG")),
                          str(nguong.get("value", "")), GOLD, qn, val_size=68)

        # --- thuoc thoi gian: can co, khong thi ba o doi so ma khong ai biet
        # dang o giay thu bao nhieu
        ry = ty + th + 34
        if ruler:
            head = MARGIN + CONTENT_W * clamp((p - 0.06) / 0.80)
            dd.line([s(MARGIN), s(ry), s(W - MARGIN), s(ry)],
                    fill=EDGE + (255,), width=s(2))
            dd.line([s(MARGIN), s(ry), s(head), s(ry)], fill=acc + (255,),
                    width=s(4))
            dd.ellipse([s(head - 7), s(ry - 7), s(head + 7), s(ry + 7)],
                       fill=acc + (255,))
            rf = typo.mono_font(20, 500)
            for i, lab in enumerate(ruler):
                rx = MARGIN + CONTENT_W * (i / max(1, len(ruler) - 1))
                ttext(base, str(lab), rf, DIM, ry + 18,
                      cx=min(max(rx, MARGIN + 24), W - MARGIN - 24), track=2.0)

        va = sp.get("verdict_at")
        if va and p >= float(va):
            qq = clamp((p - float(va)) / 0.10)
            # Bam ngay sau thuoc thoi gian chu khong dinh vao day san dien: noi
            # dung cua canh nay cao co dinh nen dinh o day de lai mot khoang
            # trong lon giua thuoc va cau ket.
            cy = min(ry + 70, STAGE_BOTTOM - 96)
            vf, lines, _ = typo.headline(sp.get("verdict", ""), CONTENT_W - 40,
                                         96, 70, 42, -2, "slab_black")
            vcol = acc_of(sp.get("verdict_color"), HOT)
            glow(base, (MARGIN, cy, W - MARGIN, cy + 80), vcol, 70, int(70 * qq))
            ttext(base, lines[0], vf, vcol, cy, cx=CX, track=-2, p=qq, rise=20)
    b.add(fn, dur=max(2.0, b.dur * 0.80), wait=b.dur)


def sc_gop(b, sp, acc):
    """MO PHONG - NHIEU CAI RA MOT. Nguoc chieu voi `multiply`.

    `multiply` ke chuyen mot thanh nhieu. Co mot nhom chu de ke chuyen nguoc
    lai, va no la nhom dang so nhat: hai dau vao KHAC NHAU cho ra CUNG MOT ket
    qua. Bam trung (MD5), khoa cache trung, ID trung sau khi cat bot, hai email
    khac nhau chuan hoa thanh mot.

    Hinh dang: hai the dau vao o tren, hai mui ten chum vao mot the ket qua o
    duoi. The doi chung (`khac`) la tuy chon nhung nen co - no cho thay cung hai
    dau vao do, mot ham KHAC lai tach duoc chung ra, tuc loi khong nam o dau vao.

    Truong:
      vao[]  { nhan, value, note }  - hai (hoac ba) dau vao
      qua    ten phep bien doi, ve tren cho hai mui ten gap nhau
      ra     { nhan, value, note }  - ket qua trung nhau
      khac   { nhan, value, note }  - doi chung: ham khac thi KHONG trung
    """
    vao = (sp.get("vao") or [])[:3]
    ra = sp.get("ra") or {}
    khac = sp.get("khac")
    if not vao or not ra:
        return

    n = len(vao)
    gap = 22
    bw = (CONTENT_W - gap * (n - 1)) / n
    top = STAGE_TOP + 10
    ih = 178
    # cho hai mui ten chum lai
    my = top + ih
    mh = 116
    ry = my + mh
    rh = 214
    kh = 122

    def fn(base, d, p):
        dd = ImageDraw.Draw(base)
        # --- dau vao
        for i, v in enumerate(vao):
            qi = clamp((p - i * 0.10) / 0.16)
            bx = MARGIN + i * (bw + gap)
            box = (bx, top, bx + bw, top + ih)
            card(base, box, qi, fill=SURF, border=EDGE, radius=12)
            if qi <= 0.2:
                continue
            bcx = bx + bw / 2
            kf = typo.mono_font(21, 700)
            ttext(base, str(v.get("nhan", "")), kf, MUTED, top + 24, cx=bcx,
                  track=3.5, p=qi)
            val = str(v.get("value", ""))
            vf = typo.mono_font(28, 500)
            for j, ln in enumerate(sk.wrap(val, vf, bw - 44)[:2]):
                ttext(base, ln, vf, FG, top + 66 + j * 36, cx=bcx, track=0.5,
                      p=qi)
            if v.get("note"):
                mf = typo.mono_font(19, 500)
                ttext(base, str(v["note"]), mf, GOLD, top + ih - 36, cx=bcx,
                      track=2.0, p=qi)

        # --- hai mui ten chum vao mot diem. Chinh cho CHUM lai la noi dung.
        qa = clamp((p - 0.30) / 0.18)
        if qa > 0:
            for i in range(n):
                x = MARGIN + i * (bw + gap) + bw / 2
                y0 = top + ih + 8
                y1 = my + mh - 26
                xm = CX
                dd.line([s(x), s(y0), s(x + (xm - x) * qa),
                         s(y0 + (y1 - y0) * qa)], fill=EDGE_HI + (255,),
                        width=s(3))
            if sp.get("qua"):
                qf = typo.mono_font(26, 700)
                lb = str(sp["qua"])
                bx0 = CX - track_w(lb, qf, 4.0) / 2 - 22
                card(base, (bx0, my + 18, CX + (CX - bx0), my + 74), qa,
                     fill=BG, border=acc, radius=10)
                ttext(base, lb, qf, acc, my + 34, cx=CX, track=4.0, p=qa)

        # --- ket qua: trung nhau
        qr = clamp((p - 0.52) / 0.18)
        if qr > 0:
            box = (MARGIN, ry, W - MARGIN, ry + rh)
            glow(base, box, HOT, 66, int(72 * qr))
            card(base, box, qr, fill=SURF, border=HOT, radius=12)
            brackets(base, (box[0] + 10, box[1] + 10, box[2] - 10, box[3] - 10),
                     HOT, qr, 26, 3)
            kf = typo.mono_font(22, 700)
            ttext(base, str(ra.get("nhan", "KẾT QUẢ")), kf, MUTED, ry + 26,
                  cx=CX, track=4.0, p=qr)
            val = str(ra.get("value", ""))
            vf = fit_one("grot_black", val, CONTENT_W - 90, 72, 30)
            ttext(base, val, vf, HOT, ry + 68, cx=CX, track=-1.0, p=qr)
            # Ghi chu dat NGAY DUOI so, do bang chieu cao thuc cua so chu khong
            # dat cung o day hop - so tu co nho khi dai nen day hop khong doan
            # duoc.
            if ra.get("note"):
                mf = typo.mono_font(21, 700)
                ttext(base, str(ra["note"]), mf, HOT,
                      ry + 68 + typo.tm(val, vf)[1] + 16, cx=CX, track=3.0,
                      p=qr)

        # --- doi chung: cung hai dau vao, ham khac thi KHONG trung
        if khac:
            qk = clamp((p - 0.74) / 0.14)
            if qk > 0:
                box = (MARGIN, ry + rh + 20, W - MARGIN, ry + rh + 20 + kh)
                card(base, box, qk, fill=BG, border=OK, radius=12)
                kf = typo.mono_font(21, 700)
                ttext(base, str(khac.get("nhan", "ĐỐI CHỨNG")), kf, MUTED,
                      box[1] + 20, cx=CX, track=3.5, p=qk)
                val = str(khac.get("value", ""))
                vf = fit_one("grot_black", val, CONTENT_W - 90, 46, 26)
                ttext(base, val, vf, OK, box[1] + 56, cx=CX, track=-0.5, p=qk)

        va = sp.get("verdict_at")
        if va and p >= float(va):
            qq = clamp((p - float(va)) / 0.10)
            # Bam theo day khoi noi dung, khong dinh vao day san dien: xem chu
            # thich cung viec o `sc_ban_sao`.
            day = ry + rh + (20 + kh if khac else 0)
            cy = min(day + 42, STAGE_BOTTOM - 74)
            vf, lines, _ = typo.headline(sp.get("verdict", ""), CONTENT_W - 40,
                                         80, 64, 40, -2, "slab_black")
            vcol = acc_of(sp.get("verdict_color"), HOT)
            glow(base, (MARGIN, cy, W - MARGIN, cy + 70), vcol, 70, int(70 * qq))
            ttext(base, lines[0], vf, vcol, cy, cx=CX, track=-2, p=qq, rise=18)
    b.add(fn, dur=max(2.0, b.dur * 0.80), wait=b.dur)


def sc_intro(b, sp, acc):
    """Canh mo man: mot cau hoi truc tiep, roi ten video.

    Dung cho nhung so ma trieu chung phai KE ra moi hieu, chu khong chieu duoc
    bang mot dong shell. Vi du "danh sach o may dev load nhanh ma len production
    thi lau" - khong co lenh nao chup duoc canh do trong mot dong.

    Thuong KHONG khai `kicker` - rail tren cung da co `brand` roi, khai them la
    lap lai. Chi khai khi muon mot dong khac han rail.

    Thu tu CO CHU Y: cau hoi truoc, ten video sau. Nguoi xem gat dau voi cau hoi
    roi moi doc ten, nen ten doc thanh "dung roi, video nay noi ve cai do".
    Dao lai thi thanh mot tam bia sach.
    """
    hoi = sp.get("hoi", "")
    ten = sp.get("title") or sp.get("ten", "")
    y = STAGE_TOP + 20

    if sp.get("kicker"):
        def fn_k(base, d, p):
            mono(base, sp["kicker"], (MARGIN, y), acc, p, 24, 5.0, 700)
        b.add(fn_k, dur=0.4, wait=0.24)

    # --- cau hoi: chu vua, xuong dong, doc nhu loi noi
    hy = y + 56
    hf, hlines, hlh = typo.headline(hoi, CONTENT_W - 20, 300, 62, 38, -1.0,
                                    "grot")
    for i, ln in enumerate(hlines):
        def fn_h(base, d, p, ln=ln, i=i):
            ttext(base, ln, hf, FG, hy + i * hlh, x=MARGIN, track=-1.0, p=p,
                  rise=18)
        b.add(fn_h, dur=0.42, wait=0.20)
    hbot = hy + hlh * len(hlines)

    # --- ke ngang roi ten video, co lon nhat khung
    def fn_ke(base, d, p):
        hline(base, hbot + 26, EDGE_HI, MARGIN, MARGIN + 220, p, 3)
    b.add(fn_ke, dur=0.34, wait=0.18)

    ty = hbot + 62
    tf, tlines, tlh = typo.headline(ten, CONTENT_W - 20,
                                    STAGE_BOTTOM - ty - 120, 104, 56, -2.4,
                                    "slab_black")
    for i, ln in enumerate(tlines):
        def fn_t(base, d, p, ln=ln, i=i):
            yy = ty + i * tlh
            if i == 0:
                glow(base, (MARGIN, yy, W - MARGIN, yy + tlh), acc, 80,
                     int(56 * expo_out(p)))
            ttext(base, ln, tf, acc, yy, x=MARGIN, track=-2.4, p=p, rise=24)
        b.add(fn_t, dur=0.5, wait=0.26)

    if sp.get("sub"):
        sy = ty + tlh * len(tlines) + 22

        def fn_s(base, d, p):
            mono(base, sp["sub"], (MARGIN, sy), MUTED, p, 24, 3.0, 500)
        b.add(fn_s, dur=0.4, wait=0.2)


def _khoi_code(base, box, ve, p, lines, mau_diff, lo_mo, lh=38):
    """Ve mot khoi code trong the. Dong nao `diff: true` thi co vach mau ben
    trai va chu sang hon - do la cho DUY NHAT hai ve khac nhau."""
    dd = ImageDraw.Draw(base)
    cf = typo.mono_font(28, 500)
    x = box[0] + 34
    y0 = box[1] + 74
    cf = typo.mono_font(max(20, int(lh * 0.74)), 500)
    for i, ln in enumerate(lines):
        q = clamp((p - 0.10 - i * 0.045) / 0.30)
        if q <= 0:
            continue
        txt = ln if isinstance(ln, str) else str(ln.get("text", ""))
        khac = isinstance(ln, dict) and ln.get("diff")
        y = y0 + i * lh
        if khac:
            dd.rounded_rectangle([s(box[0] + 14), s(y - 2), s(box[0] + 20),
                                  s(y + 26)], radius=s(3),
                                 fill=mau_diff + (255,))
        col = FG if khac else MUTED
        if lo_mo:
            col = DIM
        ttext(base, txt, cf, col, y, x=x, track=0.5, p=q, rise=8)


def sc_code(b, sp, acc):
    """HAI DOAN CODE - canh chinh cua mua 3.

    Hinh dang: hai the code xep doc, dem nguoc ba giay cho nguoi xem CHON, roi
    moi lat bai. Suc manh cua dinh dang nay khong nam o code ma o cho nguoi xem
    da trot chon trong dau truoc khi biet dap an - ho vao binh luan de bao ve
    lua chon do.

    Vi vay ba moc thoi gian la bat buoc va khong duoc rut ngan:
      0    -> 0,45   hai the hien ra, code hien tung dong
      0,45 -> 0,70   dem nguoc, KHONG co gi khac dong (de mat kip doc lai)
      0,70 -> het    lat bai: ve thang sang len, ve thua mo di, hien so do

    Chi to mau dong NAO KHAC NHAU (`diff: true`). To ca doan thi mat cho nhin,
    ma ca y nghia cua canh la "hai doan gan y het, khac dung mot cho".
    """
    A, B = sp["a"], sp["b"]
    thang = str(sp.get("ket", "b")).lower()
    # Tu tinh chieu cao theo SO DONG CODE. Dat cung mot con so thi doan 3 dong
    # de lai mot mang trong, con doan 7 dong thi tran ra ngoai the.
    #   74  nhan A/B + chu chu thich
    #   38  moi dong code
    #   76  cho o so ket qua ben duoi
    n_dong = max(len(A.get("lines") or []), len(B.get("lines") or []))
    gap = 44
    lh = 38
    ph = int(sp.get("box_h", 74 + n_dong * lh + 76))
    # Hai the CONG cau ket phai lot trong san dien. Doan 6 dong lam ph = 378,
    # nhan hai cong gap la 800 trong khi san chi con 676 - cau ket de len the
    # duoi. Co dong lai thay vi de tran.
    kha_dung = STAGE_BOTTOM - 150 - STAGE_TOP
    if ph * 2 + gap > kha_dung and not sp.get("box_h"):
        ph = int((kha_dung - gap) / 2)
        lh = max(26, (ph - 150) / max(1, n_dong))
    tong = ph * 2 + gap
    y0 = STAGE_TOP + max(0, (STAGE_BOTTOM - 150 - STAGE_TOP - tong) / 2)
    hop = [(MARGIN, y0, W - MARGIN, y0 + ph),
           (MARGIN, y0 + ph + gap, W - MARGIN, y0 + ph + gap + ph)]
    dem_n = int(sp.get("dem", 3))

    def fn(base, d, p):
        dd = ImageDraw.Draw(base)
        lat = p >= 0.70
        ql = clamp((p - 0.70) / 0.16)

        for i, (ve, box) in enumerate(zip((A, B), hop)):
            nhan = str(ve.get("label", "AB"[i]))
            la_thang = (nhan.lower() == thang) or ("ab"[i] == thang)
            col = acc_of(ve.get("color"), COOL if i == 0 else VIOLET)
            if lat:
                col = OK if la_thang else HOT
            card(base, box, clamp(p / 0.16), fill=SURF, border=EDGE, radius=14,
                 lit=col if (lat and la_thang) else None)
            # Chip A / B: cho neo mat, phai co truoc ca code
            cw = 62
            dd.rounded_rectangle([s(box[0] + 24), s(box[1] + 20),
                                  s(box[0] + 24 + cw), s(box[1] + 66)],
                                 radius=s(10), fill=col + (255,))
            nf = typo.mono_font(30, 700)
            ttext(base, nhan, nf, BG, box[1] + 30,
                  cx=box[0] + 24 + cw / 2, track=0)
            if ve.get("note"):
                mono(base, ve["note"], (box[0] + 104, box[1] + 30), MUTED,
                     clamp(p / 0.20), 22, 3.0)
            _khoi_code(base, box, i, p, ve.get("lines") or [], col,
                       lat and not la_thang, lh)
            # so do, chi hien sau khi lat bai
            if lat and ve.get("value"):
                vf = fit_one("grot_black", str(ve["value"]), 300, 54, 30)
                tw = track_w(str(ve["value"]), vf, -1.0)
                glow(base, (box[2] - 60 - tw, box[3] - 76, box[2] - 20,
                            box[3] - 20), col, 48, int(60 * ql))
                ttext(base, str(ve["value"]), vf, col, box[3] - 72,
                      x=box[2] - 34 - tw, track=-1.0, p=ql, rise=14)

        # --- dem nguoc, nam giua hai the
        if 0.45 <= p < 0.70:
            gp = (p - 0.45) / 0.25
            con = dem_n - int(gp * dem_n)
            cy = (hop[0][3] + hop[1][1]) / 2
            r = 34
            dd.ellipse([s(CX - r), s(cy - r), s(CX + r), s(cy + r)],
                       fill=BG + (255,), outline=EDGE_HI + (255,), width=s(3))
            df = fit_one("grot_black", str(con), 60, 46, 30)
            oy, th = typo.tm(str(con), df)
            # `ttext` dat DINH MUC tai `y` va da tu bu `oy`, nen chi tru
            # `th / 2` la du. Tru them `oy` la day chu len 12px.
            ttext(base, str(con), df, FG, cy - th / 2, cx=CX, track=-1)
        elif p < 0.45:
            f = typo.mono_font(22, 700)
            t = sp.get("hoi", "CÁI NÀO ĐÚNG?")
            cy = (hop[0][3] + hop[1][1]) / 2
            ttext(base, t, f, MUTED, cy - 12, cx=CX, track=4.0,
                  p=clamp((p - 0.20) / 0.20))

        va = sp.get("verdict_at", 0.86)
        if sp.get("verdict") and p >= float(va):
            qq = clamp((p - float(va)) / 0.10)
            cy = STAGE_BOTTOM - 110
            vf, lines, _ = typo.headline(sp["verdict"], CONTENT_W - 40, 96, 70,
                                         42, -2, "slab_black")
            vcol = acc_of(sp.get("verdict_color"), OK)
            glow(base, (MARGIN, cy, W - MARGIN, cy + 80), vcol, 70, int(70 * qq))
            ttext(base, lines[0], vf, vcol, cy, cx=CX, track=-2, p=qq, rise=20)
    b.add(fn, dur=max(2.0, b.dur * 0.86), wait=b.dur)


BUILDERS = {
    "probe": sc_probe, "statement": sc_statement, "list": sc_list,
    "rule": sc_rule, "counters": sc_counters, "ask": sc_ask,
    "compare": sc_compare, "code": sc_code, "intro": sc_intro,
    # --- mo phong: moi cai tra loi mot cau hoi khac nhau, xem docstring
    "gantt": sc_gantt,          # KHI NAO   - hai viec chong len nhau
    "multiply": sc_multiply,    # BAO NHIEU CAI - mot thanh rat nhieu
    "queue": sc_queue,          # BAO NHIEU THEO THOI GIAN - don u, khong rut
    "topology": sc_topology,    # O DAU     - tang nao co, tang nao khong
    # --- bon loai them sau khi ra soat 292 chu de trong `files/`
    "cot": sc_cot,              # BAO NHIEU O MOI MUC - bien khong phai thoi gian
    "thac": sc_thac,            # CAI NAO CHO CAI NAO - bac thang tuan tu
    "ban_sao": sc_ban_sao,      # MOI BAN SAO GIU GI  - N instance, N gia tri
    "gop": sc_gop,              # NHIEU CAI RA MOT    - nguoc cua multiply
}


def build(sp, dur, doc=None):
    ap_he((doc or {}).get("he", "hien_truong"))
    kind = sp.get("scene")
    if kind not in BUILDERS:
        raise ValueError(f"theme bench khong co loai canh {kind!r}. "
                         f"Co: {', '.join(sorted(BUILDERS))}")
    acc = acc_of(sp.get("accent") or (doc or {}).get("accent"), HOT)
    scenes = (doc or {}).get("scenes") or []
    first = bool(scenes) and scenes[0] is sp   # so sanh dinh danh, khong so noi dung
    b = B(dur, pre=0.66)          # chua cho khung co dinh chay truoc noi dung
    chrome(b, sp, doc, acc, chapters(doc), first)
    BUILDERS[kind](b, sp, acc)
    # Dao cu ve DE LEN canh, nen phai them SAU khi canh dung xong. Truoc
    # `b.finish()` de no cung duoc chuan hoa nhip theo loi doc.
    if sp.get("prop"):
        import dao_cu
        dao_cu.them(b, sp, (MARGIN, STAGE_TOP, W - MARGIN, STAGE_BOTTOM),
                    acc, SURF, EDGE_HI, FG, DIM)
    b.finish()
    note(b, sp.get("caption"), acc, at=0.28)
    footer(b, doc, at=0.46, first=first)
    # cu tan phai them CUOI CUNG: phan tu ve theo thu tu, no can nam tren het
    dissolve(b)
    return b.els
