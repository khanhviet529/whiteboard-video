"""Chong do luc may dang ban. Dung chung cho moi bo do trong `repro/`.

## Vi sao co file nay

Da mat mot bo so vi loi nay: chay `bench_python.py` trong luc mot luot render
dang chiem CPU. Cung mot doan code:

    may ban   x in list 159,75 ms | x in set 1,01 ms  -> 158 lan
    may ranh  x in list  32,55 ms | x in set  317 us  -> 103 lan

Lech 5 lan, va TY LE giua hai ve cung doi nen khong chua chay duoc bang cach
chi lay ty le. Toan bo so cua mot screenplay phai bo va do lai.

## Cach lam

Chay mot viec co chi phi CO DINH (khong I/O, khong cap phat lon, khong cache)
roi so voi moc chuan. May ban thi viec do cham han.

MOC PHAI LUU RA DIA. Do lai o dau moi luot thi moc bang chinh no, nen mot luot
chay tren may DANG BAN tu dau se thay "binh thuong" va khong canh bao gi - dung
cai bay da lam hong bo so kia. Luu ra dia thi moc la lan chay NHANH NHAT tu
truoc toi nay, va moi lan sau deu so voi no.

## Dung the nao

    from _hieu_chuan import kiem_may, in_moc

    in_moc()
    ban = []
    for ten in cac_ca:
        r = chay(ten)
        ranh, ty = kiem_may(im=True)
        if not ranh:
            ban.append(f"{ten} ({ty:.2f}x)")
    canh_bao(ban)
"""
import io
import os
import time

MOC_FILE = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "build", "_moc_chuan.txt")
NGUONG_BAN = 1.35
_MOC = 0.0


def _viec_goc(lap=5):
    """Viec co chi phi co dinh. Khong dung thu vien ngoai de moc on dinh."""
    def viec():
        t = 0
        for i in range(200_000):
            t += i * i
        return t
    ra = []
    for _ in range(lap):
        t0 = time.perf_counter()
        viec()
        ra.append(time.perf_counter() - t0)
    return min(ra)


def _doc_moc():
    try:
        return float(io.open(MOC_FILE, encoding="utf-8").read().strip())
    except Exception:
        return 0.0


def kiem_may(im=False):
    """(ranh, ty_le). Goi o DAU luot va sau MOI ca.

    Sau moi ca chu khong chi o dau: mot luot render co the bat dau o giua chung,
    va nhung ca chay sau do se sai trong khi nhung ca truoc van dung.
    """
    global _MOC
    t = _viec_goc()
    if not _MOC:
        _MOC = _doc_moc()
    if not _MOC or t < _MOC:
        _MOC = t
        os.makedirs(os.path.dirname(MOC_FILE), exist_ok=True)
        io.open(MOC_FILE, "w", encoding="utf-8").write(f"{t:.6f}")
        return True, 1.0
    ty = t / _MOC
    if not im and ty >= NGUONG_BAN:
        print(f"  !! MAY DANG BAN: hieu chuan cham gap {ty:.2f} lan moc "
              f"({t * 1000:.1f}ms so voi {_MOC * 1000:.1f}ms).")
        print(f"     So do KHONG dung duoc cho kich ban. Dong bot viec khac.")
    return ty < NGUONG_BAN, ty


def in_moc():
    kiem_may()
    print(f"hieu chuan: {_MOC * 1000:.1f} ms")


def canh_bao(ban):
    if ban:
        print("\n!! MAY BAN luc do: " + ", ".join(ban))
        print("   Dung nhung so nay cho kich ban la SAI. Chay lai luc may ranh.")
        return False
    return True
