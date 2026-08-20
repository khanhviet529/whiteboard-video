"""Do chat luong audio da sinh, va quyet dinh nhan hay sinh lai.

Ly do file nay ton tai: hai loai loi dau (cau hinh troi, vi tri trong loi doc)
suy duoc tu van ban nen `lint.py` chan truoc khi sinh. Loai thu ba thi khong -
cung mot cau, hai lan sinh ra hai chat luong. Da do duoc: cung mot cau, lan nay
5,71 khoi/giay lan kia 4,71.

(Duong voicestudio CO seed, nen ghim seed thi tai lap duoc dung file cu. Nhung
dieu do khong bo duoc cong nay: seed khac nhau van cho chat luong khac nhau, va
voi 90 video thi khong ai nghe lai tung canh.)

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
VONG_TOI_DA = 3     # so vong sinh lai. Moi vong bi chan o SINH_LAI_TOI_DA cau
                    # nen mot vong chi ton ~3 phut, khong phai ca tieng. Nang tu
                    # 2 len 3 vi cuc nhieu la NGAU NHIEN: ty le mot lan sinh ra
                    # sach do duoc khoang 3/4, nen hai vong chi don duoc ~63%
                    # truong hop co ba cau xau, ba vong len ~78%.
SINH_LAI_TOI_DA = 3  # so canh sinh lai moi vong, tinh tu canh xau nhat

# --- do tho (nhieu cuc bo) -------------------------------------------------
# Do bang ty le nang luong dai 5-11kHz so voi dai 100-4000Hz trong tung cua so
# 0,25 giay. Tieng Viet binh thuong ty le nay gan nhu bang khong: do tren 11 cau
# da duyet, TRUNG VI moi cau chi 0,1-0,2%. Con cac cuc nhieu do model sinh loi
# thi vot len 242%, 339%, 638% - tach ra rat sach nen khong can ngưỡng tinh vi.
#
# Vi sao phai them tieu chi nay: cong cu chi dem LO CHET, nen mot ban co ba cuc
# nhieu ram tai van "DAT" - da xay ra dung nhu vay va nguoi nghe phat hien ra
# truoc cong do. Am xat (s, x, th) co the day mot cua so len vai chuc phan tram,
# nen de nguong o 120% cho chac: bat dung 4 cua so loi, khong bao oan cai nao.
THO_NGUONG = 120.0   # phan tram
THO_WIN = 0.25       # giay, do dai cua so do
THO_IM = 2e-3        # RMS duoi nay coi la khoang lang, khong do
THO_LF_TOI_THIEU = 0.15   # cua so phai co it nhat bay nhieu lan nang luong dai
                          # thap so voi TRUNG VI ca file moi duoc xet

# Sai lam da mac va da sua, ghi lai vi no rat de mac lai: ban dau chi lay TY LE
# hi/lo roi so voi nguong. Ty le do vo nghia khi lo gan bang khong - do duoc mot
# cua so dau cau chi co hoi tho: RMS 0,0127, LF bang 0,00x trung vi, HF chi
# 1,7e+02, nhung ty le vot len 770% va bi bao la "cuc nhieu". Trong khi mot cua
# so THAT SU nhieu o canh khac co HF 6,7e+03 - to gap 40 lan - lai chi ra 5,7%
# vi no co dai thap day du.
#
# Da tra gia cho loi nay: bao sai 4 "cuc nhieu", chay 3 vong sinh lai vo ich,
# va suyt sua van ban screenplay ma van de khong nam o do. Nen bay gio cua so
# phai VUOT nguong nang luong tuyet doi truoc, moi den luot xet ty le.

# Da thu va LOAI: tang `num_step` KHONG chua duoc cuc nhieu. Do tren cung mot
# cau, cung giong, cung style:
#     num_step  8  ->  tho_max  329%, 1 cuc nhieu
#     num_step 16  ->  tho_max 2593%, 2 cuc nhieu   (XAU HON)
# Nghia la cuc nhieu khong phai vet cua so buoc khu nhieu, no NGAU NHIEN theo
# tung lan sinh. Nen duong duy nhat la PHAT HIEN roi SINH LAI - dung tim cach
# tinh chinh tham so. Ghi lai day de nguoi sau khong thu lai lan nua (mot lan
# thu ton 15 phut may).


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


def _tho(y, sr):
    """Ty le nang luong 5-11kHz / 100-4000Hz theo tung cua so. Xem THO_NGUONG."""
    n = int(sr * THO_WIN)
    if n <= 0 or len(y) < n:
        return []
    # Luot mot: do nang luong hai dai cho moi cua so.
    cs = []
    for i in range(len(y) // n):
        seg = y[i * n:(i + 1) * n]
        if np.sqrt(float(np.mean(seg ** 2))) < THO_IM:
            continue
        Y = np.abs(np.fft.rfft(seg * np.hanning(len(seg)))) ** 2
        f = np.fft.rfftfreq(len(seg), 1 / sr)
        cs.append((float(Y[(f >= 100) & (f < 4000)].sum()),
                   float(Y[(f >= 5000) & (f < 11000)].sum())))
    if not cs:
        return []
    # Luot hai: chi xet cua so co dai thap du manh - xem THO_LF_TOI_THIEU.
    med = float(np.median([lo for lo, _ in cs])) or 1e-12
    return [hi / max(lo, 1e-12) * 100.0 for lo, hi in cs
            if lo >= med * THO_LF_TOI_THIEU]


def do(path):
    """So do cua mot file wav. Khong quyet dinh gi o day."""
    y, sr = _doc(path)
    dai = len(y) / sr if sr else 0.0
    khoi, co_am = _khoi(y, sr)
    lo = _lo_chet(y, sr)
    tho = _tho(y, sr)
    tv = float(np.median(khoi)) if khoi else 0.0
    return {
        "tho_max": max(tho) if tho else 0.0,
        "tho_dem": sum(1 for x in tho if x > THO_NGUONG),
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
    return (300.0 * m["tho_dem"]              # cuc nhieu: nghe ra ngay lap tuc
            + 100.0 * len(m["lo_nang"])
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
    n_tho = sum(m.get("tho_dem", 0) for m in cac_do)
    # Hai dieu kien DOC LAP, phai qua ca hai. Mot cuc nhieu duy nhat cung du
    # lam nguoi nghe nhan xet "giong bi nhieu", nen khong tinh binh quan theo
    # phut nhu lo chet - co la truot.
    return (ty <= LO_MOI_PHUT and n_tho == 0), ty, xau


def dong_bao_cao(m, ten):
    lo = (f"  lỗ {m['lo_dai_nhat'] * 1000:.0f}ms×{len(m['lo_nang'])}"
          if m["lo_nang"] else "")
    if m.get("tho_dem"):
        lo += f"  NHIỄU {m['tho_max']:.0f}%×{m['tho_dem']}"
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
