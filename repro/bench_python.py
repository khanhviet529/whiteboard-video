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
import statistics as st
import sys
import time

LAP = 7          # so lan do, lay trung vi
AM = 10_000      # co mau mac dinh


def _do(ham, lap=LAP):
    """Trung vi cua `lap` lan do. Tat gc de khong bi mot lan thu gom lam lech."""
    ra = []
    gc.disable()
    try:
        for _ in range(lap):
            t0 = time.perf_counter()
            ham()
            ra.append(time.perf_counter() - t0)
    finally:
        gc.enable()
    return st.median(ra)


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
    "sort_chuoi": ca_sort_js_kieu,
}


def _ms(x):
    return f"{x * 1000:.2f} ms" if x >= 0.001 else f"{x * 1e6:.0f} µs"


def main():
    ten = sys.argv[1:] or list(CA)
    for k in ten:
        if k not in CA:
            print(f"khong co ca {k!r}. Co: {', '.join(CA)}")
            continue
        r = CA[k]()
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


if __name__ == "__main__":
    main()
