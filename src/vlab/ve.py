"""VISUAL LAB - primitive ve trong TOA DO THE GIOI, khong trong toa do khung.

Khac biet voi `bench.py`: moi ham o day nhan mot `Cam` va tu chieu toa do. Nghia
la cung mot doi tuong, o hai nhip khac nhau, ve ra hai kich co khac nhau ma
khong can khai lai gi - va do la dieu `bench` khong lam duoc, vi o do moi canh
tu tinh bo cuc trong mot khung co dinh.

Chu cung phai co giai theo zoom, nhung KHONG theo ty le tuyen tinh: chu nho hon
18px thi khong doc duoc tren dien thoai, nen `_co_chu` chan duoi. Do la mot rang
buoc that cua dinh dang doc 9:16, khong phai mot lua chon.

Brand duoc giu bang font, net va bang mau - `style.py` va `typo.py` dung nguyen.
Cai bi bo la BO CUC CO DINH, khong phai nhan dien.
"""
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import typo  # noqa: E402
from style import clamp, font, s  # noqa: E402

# Bang mau: giu y nguyen nghia cua `bench` he `hien_truong`. Mau la ngon ngu,
# doi mau la doi nghia - nen day la thu KHONG duoc thu nghiem trong lab nay.
BG = (9, 9, 12)
SURF = (18, 18, 23)
EDGE = (50, 50, 60)
EDGE_HI = (78, 78, 92)
FG = (240, 242, 246)
MUTED = (152, 154, 164)
DIM = (96, 98, 108)
HOT = (255, 82, 48)
OK = (58, 219, 138)
COOL = (88, 168, 255)
VIOLET = (170, 132, 255)
GOLD = (250, 196, 60)

MAU = {"hot": HOT, "ok": OK, "cool": COOL, "violet": VIOLET, "gold": GOLD,
       "fg": FG, "muted": MUTED, "dim": DIM, "edge": EDGE}

# Trang thai cua doi tuong -> mau. Cung bang cua bench.
TRANG_THAI = {"thuong": None, "ok": OK, "sai": HOT, "cho": GOLD,
             "nguoi_khac": VIOLET, "tat": DIM, "moi": OK}


def mau_cua(dt, mo=1.0):
    c = TRANG_THAI.get(dt.trang_thai) or MAU.get(dt.mau, COOL)
    if mo >= 0.999:
        return c
    return tuple(int(BG[i] + (c[i] - BG[i]) * mo) for i in range(3))


def mau_cua_phu(mo):
    """DIM da tron ve nen theo do mo. Dung cho chu phu."""
    return tuple(int(BG[i] + (DIM[i] - BG[i]) * mo) for i in range(3))


def _co_chu(co, cam, nho_nhat=17):
    """Co chu sau khi ap zoom, chan duoi de con doc duoc."""
    return max(nho_nhat, int(round(co * cam.ty_le())))


def _rr(d, box, r, fill=None, outline=None, width=2):
    d.rounded_rectangle([s(box[0]), s(box[1]), s(box[2]), s(box[3])],
                        radius=s(max(1, r)),
                        fill=(fill + (255,)) if fill else None,
                        outline=(outline + (255,)) if outline else None,
                        width=s(max(1, width)))


def _dut(d, p0, p1, col, buoc=26, dai=13, width=2, alpha=200):
    """Duong ke dut trong toa do KHUNG (goi sau khi da chieu)."""
    x0, y0 = p0
    x1, y1 = p1
    L = max(1e-6, ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5)
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    t = 0.0
    while t < L:
        a = (x0 + ux * t, y0 + uy * t)
        b = (x0 + ux * min(t + dai, L), y0 + uy * min(t + dai, L))
        d.line([s(a[0]), s(a[1]), s(b[0]), s(b[1])],
               fill=col + (alpha,), width=s(max(1, width)))
        t += buoc


# ------------------------------------------------------------------ primitive
def vung(base, dt, cam, mo=1.0, noi=True):
    """VUNG - mot ranh gioi co ten. Primitive trung tam cua nhom `so_huu`.

    Vi sao no la mot primitive rieng chu khong phai mot cai the to: the noi
    "day la mot vat", con vung noi "day la mot PHAM VI, va co thu nam trong,
    co thu nam ngoai". Bug cua ca nhom `so_huu` la mot thu di qua duong bien
    nay, nen duong bien phai la mot doi tuong ve duoc, khong phai mot cai vien.
    """
    d = ImageDraw.Draw(base)
    x0, y0 = cam.chieu(dt.x, dt.y)
    x1, y1 = cam.chieu(dt.x + dt.w, dt.y + dt.h)
    col = mau_cua(dt, mo)
    r = 22 * cam.ty_le()
    if noi:
        lay = Image.new("RGBA", base.size, (0, 0, 0, 0))
        _rr(ImageDraw.Draw(lay), (x0, y0, x1, y1), r,
            fill=col, width=0)
        lay.putalpha(lay.getchannel("A").point(lambda v: int(v * 0.07 * mo)))
        base.alpha_composite(lay)
    _dut(d, (x0, y0), (x1, y0), col, width=3 * cam.ty_le(), buoc=30 * cam.ty_le(),
         dai=15 * cam.ty_le(), alpha=int(210 * mo))
    _dut(d, (x0, y1), (x1, y1), col, width=3 * cam.ty_le(), buoc=30 * cam.ty_le(),
         dai=15 * cam.ty_le(), alpha=int(210 * mo))
    _dut(d, (x0, y0), (x0, y1), col, width=3 * cam.ty_le(), buoc=30 * cam.ty_le(),
         dai=15 * cam.ty_le(), alpha=int(210 * mo))
    _dut(d, (x1, y0), (x1, y1), col, width=3 * cam.ty_le(), buoc=30 * cam.ty_le(),
         dai=15 * cam.ty_le(), alpha=int(210 * mo))
    # NHAN DINH: ep vao phan CON NHIN THAY cua vung, khong neo cung vao goc.
    #
    # Day la mot yeu cau chi xuat hien khi co ong kinh. Trong mot san dien co
    # dinh thi goc cua mot khoi luon nam trong khung, nen neo vao goc la du. O
    # day ong kinh cat qua vung, va goc trai cua no troi ra ngoai man hinh -
    # nhan "DON CUA NGUOI KHAC" bien mat trong khi chinh cai vung do dang la
    # noi dung cua nhip. Da thay o ban thu ba.
    from style import W as FW
    nx = min(max(x0 + 22 * cam.ty_le(), 46), FW - 300)
    ny = max(y0 + 16 * cam.ty_le(), 34)
    if dt.nhan:
        f = typo.mono_font(_co_chu(26, cam), 700)
        typo.ttext(base, dt.nhan, f, col, ny, x=nx, track=4.0)
    if dt.sub:
        f2 = typo.mono_font(_co_chu(21, cam), 500)
        typo.ttext(base, dt.sub, f2, mau_cua_phu(mo), ny + 36 * max(0.7, cam.ty_le()),
                   x=nx, track=2.5)


def hang(base, dt, cam, mo=1.0):
    """HANG - mot ban ghi. Co `nhan` (id) va `sub` (chu so huu)."""
    d = ImageDraw.Draw(base)
    x0, y0 = cam.chieu(dt.x, dt.y)
    x1, y1 = cam.chieu(dt.x + dt.w, dt.y + dt.h)
    col = mau_cua(dt, mo)
    sang = dt.trang_thai in ("ok", "sai", "moi")
    _rr(d, (x0, y0, x1, y1), 10 * cam.ty_le(),
        fill=SURF if not sang else None,
        outline=col if sang else tuple(int(BG[i] + (EDGE[i] - BG[i]) * mo)
                                       for i in range(3)),
        width=(3 if sang else 2) * cam.ty_le())
    if sang:
        typo.glow(base, (x0, y0, x1, y1), col, int(52 * cam.ty_le()),
                  int(64 * mo))
    f = typo.mono_font(_co_chu(28, cam), 700)
    typo.ttext(base, dt.nhan, f, col if sang else mau_cua(dt, mo * 0.9),
               y0 + (y1 - y0) / 2 - _co_chu(28, cam) * 0.62,
               x=x0 + 20 * cam.ty_le(), track=1.5)
    if dt.sub:
        f2 = typo.mono_font(_co_chu(22, cam), 500)
        w2 = typo.track_w(dt.sub, f2, 2.0)
        typo.ttext(base, dt.sub, f2, (mau_cua_phu(mo) if not sang else col),
                   y0 + (y1 - y0) / 2 - _co_chu(22, cam) * 0.62,
                   x=x1 - 20 * cam.ty_le() - w2, track=2.0)


def the(base, dt, cam, mo=1.0):
    """THE - mot khoi co nhan tren va gia tri lon. Dung cho endpoint, response."""
    d = ImageDraw.Draw(base)
    x0, y0 = cam.chieu(dt.x, dt.y)
    x1, y1 = cam.chieu(dt.x + dt.w, dt.y + dt.h)
    col = mau_cua(dt, mo)
    _rr(d, (x0, y0, x1, y1), 14 * cam.ty_le(), fill=SURF, outline=col,
        width=3 * cam.ty_le())
    if dt.trang_thai in ("sai", "ok"):
        typo.glow(base, (x0, y0, x1, y1), col, int(60 * cam.ty_le()),
                  int(58 * mo))
    if dt.nhan:
        f = typo.mono_font(_co_chu(23, cam), 700)
        typo.ttext(base, dt.nhan, f, mau_cua_phu(mo * 1.4), y0 + 18 * cam.ty_le(),
                   x=x0 + 22 * cam.ty_le(), track=3.5)
    gt = dt.thua.get("gia_tri", "")
    if gt:
        fz = _co_chu(dt.thua.get("co", 44), cam)
        f2 = typo.mono_font(fz, 700)
        typo.ttext(base, str(gt), f2, col, y0 + 54 * cam.ty_le(),
                   x=x0 + 22 * cam.ty_le(), track=0.5)


def cong(base, dt, cam, mo=1.0):
    """CONG - mot phep kiem dat TREN duong bien. Mo hoac dong.

    Doi tuong nay khong ton tai trong `bench` va do la ca diem: ban sua cua
    nhom `so_huu` gan nhu luon la "them mot phep kiem o dung cho di qua", nen
    phep kiem do phai ve duoc NHU MOT VAT dat tren duong bien.
    """
    d = ImageDraw.Draw(base)
    cx, cy = cam.chieu(*dt.tam())
    R = max(14, dt.w / 2 * cam.ty_le())
    # Mau o day la NGHIA, khong phai trang tri: cong MO nghia la khong ai canh
    # duong bien -> HOT. Cong DONG la ban sua -> OK. Dat nguoc lai (do cho cai
    # dang dong) la mot loi toi da viet ra o ban dau tien va bat duoc khi nhin
    # still: khung hinh "da sua xong" lai to do khap.
    dong = dt.trang_thai == "dong"
    col = OK if dong else HOT
    if dong:
        typo.glow(base, (cx - R, cy - R, cx + R, cy + R), col,
                  int(R * 1.4), int(70 * mo))
    d.ellipse([s(cx - R), s(cy - R), s(cx + R), s(cy + R)],
              fill=BG + (255,), outline=col + (255,),
              width=s(max(2, 4 * cam.ty_le())))
    # Then chot: gach NGANG khi dong (chan duong di), hai gach DOC he ra khi mo.
    L = R * 0.52
    if dong:
        d.line([s(cx - L), s(cy), s(cx + L), s(cy)], fill=col + (255,),
               width=s(max(2, 6 * cam.ty_le())))
    else:
        for sg in (-1, 1):
            d.line([s(cx + sg * L * 0.62), s(cy - L),
                    s(cx + sg * L * 0.62), s(cy + L)], fill=col + (255,),
                   width=s(max(2, 4 * cam.ty_le())))
    if dt.nhan:
        f = typo.mono_font(_co_chu(22, cam), 700)
        w = typo.track_w(dt.nhan, f, 3.0)
        typo.ttext(base, dt.nhan, f, col, cy + R + 16 * cam.ty_le(),
                   x=cx - w / 2, track=3.0)


def goi(base, dt, cam, mo=1.0):
    """GOI TIN - mot cham tron di chuyen. `thua['duoi']` la vet duoi lai."""
    d = ImageDraw.Draw(base)
    cx, cy = cam.chieu(dt.x, dt.y)
    R = max(9, (dt.w or 30) / 2 * cam.ty_le())
    col = mau_cua(dt, mo)
    duoi = dt.thua.get("duoi")
    if duoi:
        px, py = cam.chieu(*duoi)
        _dut(d, (px, py), (cx, cy), col, buoc=22 * cam.ty_le(),
             dai=11 * cam.ty_le(), width=3 * cam.ty_le(), alpha=int(170 * mo))
    typo.glow(base, (cx - R * 2, cy - R * 2, cx + R * 2, cy + R * 2), col,
              int(R * 3), int(80 * mo))
    d.ellipse([s(cx - R), s(cy - R), s(cx + R), s(cy + R)], fill=col + (255,))
    if dt.nhan:
        f = typo.mono_font(_co_chu(23, cam), 700)
        typo.ttext(base, dt.nhan, f, col, cy - R - _co_chu(23, cam) - 10,
                   x=cx + R + 12 * cam.ty_le(), track=2.0)


def nhan_troi(base, dt, cam, mo=1.0):
    """NHAN - chu dat thang trong the gioi, khong co khung.

    Co truong nay vi mot phat hien tu do do don dieu: `bench` bat buoc moi chu
    phai nam trong mot the hoac mot khoi can giua, va do la nguon don dieu. Chu
    dat tu do trong khong gian cho ra dang bong khac han.
    """
    from style import W as FW
    x, y = cam.chieu(dt.x, dt.y)
    col = mau_cua(dt, mo)
    co = dt.thua.get("co", 40)
    role = dt.thua.get("kieu", "mono")
    # Be rong con lai tu `x` toi le phai khung. Chu troi khong co the bao quanh
    # nen KHONG co gi chan no tran ra ngoai - da thay o ban thu hai: nhan
    # "PHEP KIEM DUNG SAI CHO" bi cat mat chu dau. Phai tu thu co.
    kha_dung = max(200, FW - x - 60)
    track = 3.5 if role == "mono" else -1.5
    fz = _co_chu(co, cam)
    while fz > 20:
        f = (typo.mono_font(fz, 700) if role == "mono"
             else font("slab_black", fz))
        if typo.track_w(dt.nhan, f, track) <= kha_dung:
            break
        fz -= 2
    typo.ttext(base, dt.nhan, f, col, y, x=x, track=track,
               rise=18 if role != "mono" else 0)
    if dt.sub:
        f2 = typo.mono_font(_co_chu(22, cam), 500)
        typo.ttext(base, dt.sub, f2, mau_cua_phu(mo), y + fz * 1.25, x=x, track=2.5)


VE = {"vung": vung, "hang": hang, "the": the, "cong": cong, "goi": goi,
      "nhan": nhan_troi}


def ve_the_gioi(base, tg, cam, dang_hien, chu_y=(), boi_canh=()):
    """Ve moi doi tuong dang hien, theo dung thu tu tang.

    Doi tuong ngoai khung nhin bi bo qua han - do la co che HE LO cua mo hinh
    nay, khong phai mot phep toi uu.

    `chu_y` lam mo moi thu KHONG duoc chu y xuong 0,42. Day la cach ap luat "moi
    thoi diem dung MOT tieu diem" o tang engine, thay vi trong cay vao nguoi
    viet nho ap no o tung canh.
    """
    tang = {"vung": 0, "hang": 1, "the": 2, "cong": 3, "goi": 4, "nhan": 5}
    for dt in sorted((tg[k] for k in dang_hien if k in tg),
                     key=lambda o: tang.get(o.loai, 9)):
        if not cam.trong_khung(*dt.hop()):
            continue
        mo = dt.hien
        if chu_y and dt.id not in chu_y:
            # Ba tang: xem chu thich trong `Nhip.__init__`. `vung` luon duoc coi
            # la boi canh toi thieu - duong bien cua no la khung tham chieu cho
            # moi thu khac, mo han no di la mat diem neo.
            mo *= 0.55 if (dt.id in boi_canh or dt.loai == "vung") else 0.18
        if mo <= 0.02:
            continue
        VE[dt.loai](base, dt, cam, mo=clamp(mo))
