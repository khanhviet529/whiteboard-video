"""Do chat luong audio da sinh, va quyet dinh nhan hay sinh lai.

Ly do file nay ton tai: hai loai loi dau (cau hinh troi, vi tri trong loi doc)
suy duoc tu van ban nen `lint.py` chan truoc khi sinh. Loai thu ba thi khong -
model khong co seed, cung mot cau sinh hai lan ra hai chat luong. Da do duoc:
cung mot cau, lan nay 5,71 khoi/giay lan kia 4,71.

Voi mot video thi nguoi ta nghe lai duoc. Voi 90 video thi khong. Nen phai co
mot cong do BANG MAY, va cai gia phai tra la thoi gian may chu khong phai thoi
gian nguoi.

## Ban dau toi thiet ke sai, ghi lai de nguoi sau khong lam lai

Phien ban dau co bon tieu chi: lo chet, am tiet dau bi nen, nhip khoi, ty le im
lang. Chay thu tren ban `cache-stale` ma nguoi dung DA DUYET thi 13/13 canh deu
truot. Cong ma tu choi sach ban da duyet la cong vo dung.

Do lai tung tieu chi tren ba video nguoi dung DA NHAN, so voi mot ban BI CHE:

                    lo>=300ms/phut   canh co dau<0,8x   canh co nhip thap
  cache-stale nhan       1,35              6/13               4/13
  n-plus-one  nhan       1,87              5/8                0/8
  pool-can    nhan       0,73              5/9                0/9
  ban bi che             5,70               -                  -

Chi TY LE LO CHET tach duoc hai nhom. "Am tiet dau bi nen" xuat hien o 5-6 canh
cua CA BA video da duoc nhan, tuc no khong phai dau hieu loi - gia thuyet do
sinh ra tu 5 mau cua MOT cau, va no khong tong quat duoc. "Nhip thap" cung vay.

Nen cong chi gac MOT tieu chi, o muc VIDEO chu khong o muc canh. Cac so do khac
van tinh va van in ra, nhung chi de XEP HANG xem canh nao dang ngo nhat, khong
de tu choi.
"""
import os
import statistics as st
import wave

import numpy as np

# --- nguong ----------------------------------------------------------------
LO_DAI = 0.300      # lo chet tu day tro len la tai nghe ra duoc
LO_ZERO = 0.90      # ty le mau bang 0 TUYET DOI tu day tro len -> im lang CHEN
                    # VAO co y, khong phai loi. Khong phan biet duoc thi bao
                    # nham chinh nhung khoang nghi giua cau ma ta tu them.
LO_MOI_PHUT = 2.5   # nam giua: ban duoc nhan cao nhat 1,87 - ban bi che 5,70
VONG_TOI_DA = 2     # so vong sinh lai. Moi vong ton bang mot lan sinh lai cac
                    # canh xau, nen dat cao la video 10 canh chay ca tieng.
SINH_LAI_TOI_DA = 3  # so canh sinh lai moi vong, tinh tu canh xau nhat


def _doc(path):
    with wave.open(path, "rb") as w:
        sr, n, ch = w.getframerate(), w.getnframes(), w.getnchannels()
        y = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32)
    if ch > 1:
        y = y.reshape(-1, ch).mean(1)
    return y / 32768.0, sr


def _khoi(y, sr, fr=256, hop=64):
    """Cat thanh khoi am. Nguong lay theo phan vi nen khong phu thuoc muc thu."""
    n = 1 + (len(y) - fr) // hop
    if n <= 0:
        return [], 0.0
    e = np.sqrt(np.array([np.mean(y[i * hop:i * hop + fr] ** 2)
                          for i in range(n)]))
    duong = e[e > 0]
    if not len(duong):
        return [], 0.0
    on = e > float(np.percentile(duong, 35))
    ra, b = [], None
    for i, v in enumerate(on):
        if v and b is None:
            b = i
        elif not v and b is not None:
            d = (i - b) * hop / sr
            if d >= 0.040:
                ra.append(d)
            b = None
    if b is not None:
        ra.append((len(on) - b) * hop / sr)
    return ra, float(on.sum() * hop / sr)


def _lo_chet(y, sr):
    """Vung gan im lang GIUA cau, khong tinh im lang duoc chen vao.

    Phan biet bang ty le mau bang 0 TUYET DOI: im lang chen vao la `np.zeros`
    nen gan 100% mau bang 0, con model tu im lang thi van co nhieu nen. Khong
    phan biet thi bao nham chinh nhung khoang nghi ta tu them - da vap loi do.
    """
    fr, hop = 256, 64
    n = 1 + (len(y) - fr) // hop
    if n <= 0:
        return []
    e = np.sqrt(np.array([np.mean(y[i * hop:i * hop + fr] ** 2)
                          for i in range(n)]))
    im = e < 1e-4
    ra, b = [], None
    for i, v in enumerate(im):
        if v and b is None:
            b = i
        elif not v and b is not None:
            d = (i - b) * hop / sr
            if d >= 0.120:
                seg = y[b * hop:i * hop]
                if len(seg) and float((seg == 0).mean()) < LO_ZERO:
                    ra.append(d)
            b = None
    return ra


def do(path):
    """So do cua mot file wav. Khong quyet dinh gi o day."""
    y, sr = _doc(path)
    dai = len(y) / sr if sr else 0.0
    khoi, co_am = _khoi(y, sr)
    lo = _lo_chet(y, sr)
    tv = float(np.median(khoi)) if khoi else 0.0
    return {
        "dai": dai,
        "nhip": len(khoi) / (co_am or 1e-9),
        "im": 1.0 - (co_am / dai) if dai else 0.0,
        "khoi_dau": khoi[0] if khoi else 0.0,
        "dau_ty_le": (khoi[0] / tv) if (khoi and tv) else 0.0,
        "lo": lo,
        "lo_nang": [x for x in lo if x >= LO_DAI],
        "lo_dai_nhat": max(lo) if lo else 0.0,
    }


def diem(m):
    """Nho hon la tot hon. CHI dung de xep hang, khong de tu choi.

    Lo chet nang nhat vi do la thu duy nhat da chung minh duoc la tuong ung voi
    phan nan cua nguoi nghe. Hai thanh phan sau chi de pha the khi diem lo bang
    nhau, he so nho han han.
    """
    return (100.0 * len(m["lo_nang"])
            + 10.0 * m["lo_dai_nhat"]
            + 1.0 * max(0.0, 1.0 - (m["dau_ty_le"] or 1.0)))


def nghiem_thu(cac_do):
    """Gac o muc VIDEO. `cac_do` la danh sach so do cua tung canh.

    Tra ve (dat, ty_le_lo_moi_phut, thu_tu_canh_xau_nhat).
    """
    if not cac_do:
        return True, 0.0, []
    tong = sum(m["dai"] for m in cac_do) or 1e-9
    n_lo = sum(len(m["lo_nang"]) for m in cac_do)
    ty = n_lo / tong * 60.0
    xau = sorted(range(len(cac_do)), key=lambda i: -diem(cac_do[i]))
    xau = [i for i in xau if diem(cac_do[i]) > 0]
    return ty <= LO_MOI_PHUT, ty, xau


def dong_bao_cao(m, ten):
    lo = (f"  lỗ {m['lo_dai_nhat'] * 1000:.0f}ms×{len(m['lo_nang'])}"
          if m["lo_nang"] else "")
    return (f"    {ten:22} {m['dai']:5.1f}s  {m['nhip']:4.2f} khối/giây  "
            f"đầu {m['dau_ty_le']:4.2f}×{lo}")


def bang(cac_do, ten=None):
    """In bang de nguoi doc thay vi sao cong quyet dinh nhu vay."""
    dat, ty, xau = nghiem_thu(cac_do)
    ra = []
    for i, m in enumerate(cac_do):
        ra.append(dong_bao_cao(m, (ten[i] if ten else f"cảnh {i + 1:02d}")))
    ra.append(f"    {'—' * 30}")
    ra.append(f"    {ty:.2f} lỗ chết ≥{LO_DAI * 1000:.0f}ms mỗi phút "
              f"(ngưỡng {LO_MOI_PHUT}) → {'ĐẠT' if dat else 'TRƯỢT'}")
    if not dat and xau:
        ds = ", ".join((ten[i] if ten else f"cảnh {i + 1:02d}") for i in xau[:5])
        ra.append(f"    đáng ngờ nhất: {ds}")
    return "\n".join(ra)
