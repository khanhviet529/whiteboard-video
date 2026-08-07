"""Bo do dung chung cho MUA 3 - hai doan code, doan nao sai hoac cham.

    py repro/bench_python.py            # chay het, in bang
    py repro/bench_python.py in_set     # chay mot ca

Vi sao mot bo do chung chu khong 15 script roi: 15 script thi 15 lan viet lai
phan do thoi gian, va 15 cach do khac nhau thi khong so sanh duoc voi nhau. O
day moi ca chi khai HAI HAM va mot cau hoi, phan do la chung.

Hai loai ca, vi mua 3 co hai loai cau hoi:

  TOC DO    hai ham cung ket qua, khac thoi gian. In ms va so lan chenh.
  DUNG SAI  hai ham khac KET QUA. In ra ca hai ket qua de thay cai nao sai.

Do toc do bang trung vi cua nhieu lan lap, khong phai mot lan: may nay chay
Windows nen mot lan do le co the lech vai chuc phan tram vi tien trinh khac.
"""
import copy
import decimal
import gc
import io
import os
import statistics as st
import sys
import time

LAP = 7          # so lan do, lay trung vi
AM = 10_000      # co mau mac dinh

# Chong do luc may ban: xem `_hieu_chuan.py`. Da mat mot bo so vi loi nay.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _hieu_chuan import canh_bao, in_moc, kiem_may  # noqa: E402


# =============================================================== CA DO TOC DO

def ca_in_set():
    kho = list(range(AM))
    tim = list(range(0, AM, 7))

    def a():
        return sum(1 for x in tim if x in kho)          # list: quet tuyen tinh

    def b():
        t = set(kho)                                     # set: bam mot lan
        return sum(1 for x in tim if x in t)
    assert a() == b()
    return dict(loai="toc do", hoi="Tìm 1.429 giá trị trong 10.000 phần tử",
                a="x in list", b="x in set",
                ta=_do(a), tb=_do(b))


def ca_noi_chuoi():
    n = 20_000

    def a():
        s = ""
        for i in range(n):
            s += "x"                                     # moi vong tao chuoi moi
        return s

    def b():
        return "".join("x" for _ in range(n))
    assert a() == b()
    return dict(loai="toc do", hoi=f"Nối {n:,} ký tự thành một chuỗi".replace(",", "."),
                a="s += trong vòng lặp", b='"".join(...)',
                ta=_do(a), tb=_do(b))


def ca_sort_key():
    import math
    xs = [i * 7919 % 100_000 for i in range(20_000)]

    def nang(x):
        return math.sqrt(x) * math.log1p(x)              # hàm key ton kem

    def a():
        return sorted(xs, key=nang)                      # goi key moi lan so sanh?

    def b():
        cap = [(nang(x), x) for x in xs]                 # tinh truoc, sort tuple
        cap.sort()
        return [x for _, x in cap]
    assert a() == b()
    return dict(loai="toc do", hoi="Sắp xếp 20.000 phần tử bằng hàm key tốn kém",
                a="sorted(key=hàm)", b="tính trước rồi sort",
                ta=_do(a), tb=_do(b))


def ca_try_except():
    d = {i: i for i in range(1000)}
    khoa = list(range(1000)) * 20

    def a():
        n = 0
        for k in khoa:
            try:
                n += d[k]                                # khong bao gio nem
            except KeyError:
                pass
        return n

    def b():
        return sum(d.get(k, 0) for k in khoa)
    assert a() == b()
    return dict(loai="toc do", hoi="Đọc 20.000 khoá đều CÓ trong dict",
                a="try/except KeyError", b="dict.get",
                ta=_do(a), tb=_do(b))


def ca_copy():
    goc = [[i] * 20 for i in range(2000)]

    def a():
        return copy.copy(goc)

    def b():
        return copy.deepcopy(goc)
    return dict(loai="toc do", hoi="Sao chép list 2.000 phần tử, mỗi phần tử là list",
                a="copy.copy (nông)", b="copy.deepcopy (sâu)",
                ta=_do(a), tb=_do(b, 3))


# ============================================================= CA DO DUNG SAI

def ca_mac_dinh():
    def a(x, gio=[]):                                    # list dung CHUNG moi lan goi
        gio.append(x)
        return list(gio)

    def b(x, gio=None):
        gio = [] if gio is None else gio
        gio.append(x)
        return list(gio)
    ra_a = [a(i) for i in range(3)]
    ra_b = [b(i) for i in range(3)]
    return dict(loai="dung sai", hoi="Gọi hàm ba lần liên tiếp, mỗi lần một giá trị",
                a="def f(x, giỏ=[])", b="def f(x, giỏ=None)",
                ka=str(ra_a), kb=str(ra_b))


def ca_float_tien():
    def a():
        # VONG LAP chu khong `sum([0.1]*10)`: hai cach cong cung muoi so cho hai
        # ket qua khac nhau. `sum` tra ve dung 1.0, vong lap tra ve
        # 0.9999999999999999. Da vap khi kiem lai.
        s = 0.0
        for _ in range(10):
            s += 0.1
        return repr(s)

    def b():
        s = decimal.Decimal("0")
        for _ in range(10):
            s += decimal.Decimal("0.1")
        return str(s)
    return dict(loai="dung sai", hoi="Cộng 0,1 mười lần rồi so với 1",
                a="float", b="Decimal", ka=a(), kb=b())


def ca_tien_so_sanh():
    """Bay THAT cua tien tinh bang float: PHEP SO SANH, khong phai tich luy.

    Ban dau toi dinh ke "doi soat lech vai xu moi ngay". Do thu thi cong 50.000
    giao dich that chi lech 0,00000038 dong mot ngay - khong ai phat hien ra, va
    viet nhu vay la bia trieu chung.

    Cho hong that: khach tra lam nhieu lan, he thong kiem `da_tra == tong` va
    phep so sanh tra ve False du tien da du.
    """
    import random
    rnd = random.Random(11)
    N = 100_000
    hong = 0
    vd = []
    for _ in range(N):
        tong = rnd.randrange(1_000, 500_000) / 100
        k = rnd.randint(2, 5)
        phan = [round(tong / k, 2)] * (k - 1)
        phan.append(round(tong - sum(phan), 2))
        tra = 0.0
        for x in phan:
            tra += x
        if tra != tong:
            hong += 1
            if len(vd) < 2:
                vd.append(f"{tong} tra {phan} -> {tra!r}")

    D = decimal.Decimal
    rnd = random.Random(11)
    hong_d = 0
    for _ in range(N):
        tong = rnd.randrange(1_000, 500_000) / 100
        k = rnd.randint(2, 5)
        T = D(f"{tong:.2f}")
        phan = [(T / k).quantize(D("0.01"))] * (k - 1)
        phan.append(T - sum(phan))
        if sum(phan) != T:
            hong_d += 1
    return dict(loai="dung sai",
                hoi=f"{N:,} đơn, mỗi đơn khách trả làm 2-5 lần".replace(",", "."),
                a="float, kiểm `đã_trả == tổng`",
                b="Decimal, cùng phép kiểm",
                ka=f"{hong:,} đơn báo CHƯA ĐỦ dù tiền đủ ({hong/N*100:.2f}%)".replace(",", "."),
                kb=f"{hong_d} đơn báo sai",
                them=vd + [f"0.1 + 0.2 == 0.3  ->  {0.1 + 0.2 == 0.3}",
                           f"0.1 + 0.2         ->  {0.1 + 0.2!r}"])


def ca_copy_nong():
    """`copy.copy` chi sao chep VO ngoai. So 45.

    Ca `copy` do TOC DO, ca nay do DUNG SAI - cung mot ham nhung hai cau hoi
    khac nhau, va mua 3 can ca hai loai.
    """
    # HAI ban goc RIENG. Lan dau toi viet ket qua ve B cung trong code thay vi
    # do - dung cai sai ma ca du an nay ton cong tranh.
    def thu(sao_chep):
        goc = {"ten": "don 1204", "hang": ["áo", "quần"]}
        ban = sao_chep(goc)
        ban["hang"].append("giày")
        return goc["hang"], (goc["hang"] is ban["hang"])

    ga, chung_a = thu(copy.copy)
    gb, chung_b = thu(copy.deepcopy)
    return dict(loai="dung sai",
                hoi="Sao chép một đơn hàng rồi thêm món vào BẢN SAO",
                a="copy.copy (nông)", b="copy.deepcopy (sâu)",
                ka=f"gốc thành {ga}",
                kb=f"gốc vẫn là {gb}",
                them=[f"nông:  bản sao và bản gốc dùng chung list? {chung_a}",
                      f"sâu:   bản sao và bản gốc dùng chung list? {chung_b}"])


def ca_mui_gio():
    """Timestamp khong kem mui gio: mot moc, ba cach hieu. So 16."""
    from datetime import datetime
    from zoneinfo import ZoneInfo
    # Chon moc SAT NUA DEM va sat cuoi thang. Moc 00:30 thi ba cach hieu van
    # roi vao cung mot ngay, mat het diem quan trong - da chon sai mot lan.
    tho = "2026-02-28 23:30:00"          # luu trong database, khong offset
    naive = datetime.fromisoformat(tho)
    ra = []
    for z in ("Asia/Ho_Chi_Minh", "UTC", "America/New_York"):
        t = naive.replace(tzinfo=ZoneInfo(z))
        ra.append((z, t.astimezone(ZoneInfo("Asia/Ho_Chi_Minh"))))
    ngay = {t.date().isoformat() for _, t in ra}
    return dict(loai="dung sai",
                hoi=f"Một mốc `{tho}` không kèm múi giờ, đọc ở ba nơi",
                a="hiểu là giờ Việt Nam", b="hiểu là giờ UTC",
                ka=f"{ra[0][1].strftime('%d/%m %H:%M')} giờ VN",
                kb=f"{ra[1][1].strftime('%d/%m %H:%M')} giờ VN",
                them=[f"{z:20} -> {t.strftime('%d/%m/%Y %H:%M')} giờ VN"
                      for z, t in ra]
                     + [f"cùng một mốc rơi vào {len(ngay)} NGÀY khác nhau: "
                        + ", ".join(sorted(ngay))])


def ca_so_sanh_float():
    """So sanh hai so thuc bang `==`. So 49.

    CO Y tranh chu de tien - so 15 da lo phan do roi. O day dung ty le va toa
    do, de hai video khong trung nhau.
    """
    import math
    N = 100_000
    bang = gan = 0
    vd = []
    for i in range(1, N + 1):
        # chia mot cong viec thanh `k` phan bang nhau roi cong lai
        k = (i % 8) + 3
        phan = 1.0 / k
        tong = 0.0
        for _ in range(k):
            tong += phan
        if tong == 1.0:
            bang += 1
        if math.isclose(tong, 1.0):
            gan += 1
        if tong != 1.0 and len(vd) < 2:
            vd.append(f"chia 1 thành {k} phần rồi cộng lại -> {tong!r}")
    return dict(loai="dung sai",
                hoi=f"{N:,} lần chia 1 thành k phần bằng nhau rồi cộng lại"
                    .replace(",", "."),
                a="kiểm bằng `tong == 1.0`",
                b="kiểm bằng `math.isclose`",
                ka=f"{bang:,} lần đúng ({bang/N*100:.1f}%)".replace(",", "."),
                kb=f"{gan:,} lần đúng ({gan/N*100:.1f}%)".replace(",", "."),
                them=vd + [f"0.1 + 0.2 == 0.3          -> {0.1 + 0.2 == 0.3}",
                           f"math.isclose(0.1+0.2, 0.3) -> "
                           f"{math.isclose(0.1 + 0.2, 0.3)}"])


def ca_sort_js_kieu():
    """Khong phai JS - day la ban Python cua cung mot bay: so sanh chuoi."""
    xs = [10, 9, 1, 200, 30]

    def a():
        return sorted(xs, key=str)                       # so sanh nhu chuoi

    def b():
        return sorted(xs)
    return dict(loai="dung sai", hoi="Sắp xếp [10, 9, 1, 200, 30]",
                a="sorted(key=str)", b="sorted()",
                ka=str(a()), kb=str(b()))


CA = {
    "in_set": ca_in_set,
    "noi_chuoi": ca_noi_chuoi,
    "sort_key": ca_sort_key,
    "try_except": ca_try_except,
    "copy": ca_copy,
    "mac_dinh": ca_mac_dinh,
    "float_tien": ca_float_tien,
    "tien_so_sanh": ca_tien_so_sanh,
    "copy_nong": ca_copy_nong,
    "mui_gio": ca_mui_gio,
    "so_sanh_float": ca_so_sanh_float,
    "sort_chuoi": ca_sort_js_kieu,
}


def _ms(x):
    return f"{x * 1000:.2f} ms" if x >= 0.001 else f"{x * 1e6:.0f} µs"


def main():
    in_moc()
    ten = sys.argv[1:] or list(CA)
    ban = []
    for k in ten:
        if k not in CA:
            print(f"khong co ca {k!r}. Co: {', '.join(CA)}")
            continue
        r = CA[k]()
        # CHI gac ca do TOC DO. Ca DUNG SAI dung seed co dinh nen ket qua khong
        # phu thuoc tai may chut nao - bao "may ban" o do la bao nham, va nhung
        # ca do lai thuong nang CPU nen tu lam may ban. Bao nham thi nguoi ta bo
        # qua ca nhung lan bao dung.
        ranh, ty = (True, 1.0) if r["loai"] != "toc do" else kiem_may(im=True)
        if not ranh:
            ban.append(f"{k} ({ty:.2f}x)")
        print(f"\n=== {k} ===")
        print(f"  {r['hoi']}")
        if r["loai"] == "toc do":
            ta, tb = r["ta"], r["tb"]
            nhanh = "B" if tb < ta else "A"
            lan = (max(ta, tb) / min(ta, tb)) if min(ta, tb) else 0
            print(f"  A  {r['a']:26} {_ms(ta):>10}")
            print(f"  B  {r['b']:26} {_ms(tb):>10}")
            print(f"  -> {nhanh} nhanh hon {lan:.0f} lan")
        else:
            print(f"  A  {r['a']:26} -> {r['ka']}")
            print(f"  B  {r['b']:26} -> {r['kb']}")
            print(f"  -> hai ve ra KET QUA KHAC NHAU")
        for d in r.get("them", []):
            print(f"     {d}")
    if ban:
        print("\n!! MAY BAN luc do: " + ", ".join(ban))
        print("   Dung nhung so nay cho kich ban la SAI. Chay lai luc may ranh.")


if __name__ == "__main__":
    main()
