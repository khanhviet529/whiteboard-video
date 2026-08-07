"""Bo do dung chung cho cac chu de ve DONG THOI va CACHE.

    py repro/bench_async.py              # chay het
    py repro/bench_async.py cache_dam    # chay mot ca

Phu mua 1 (so 10, 11, 12, 13, 14) va mua 2 (so 23, 24, 25, 34) trong
KE-HOACH-90.md.

Ca nao can Redis thi noi vao Redis trong WSL2 qua cau localhost; xem
CAI-DAT-WSL.md. Khong co Redis thi ca do tu bo qua chu khong lam hong ca luot.

## Hai quy tac khi them ca moi

1. `asyncio.sleep` that chu khong gia lap dong ho, nen moi lan chay lech vai
   phan tram. Kich ban phai lay so tu DUNG MOT luot chay - hai so tu hai luot
   dat canh nhau tren cung khung hinh se khong cong ra dung.

2. Moi ca phai in ca so DEM duoc (so lan goi, so ban ghi) chu khong chi thoi
   gian. So dem la thu on dinh giua cac lan chay, va no cung la thu chieu len
   canh `multiply` hay `queue` duoc.
"""
import asyncio
import os
import statistics as st
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _hieu_chuan import canh_bao, in_moc, kiem_may  # noqa: E402


def _redis():
    try:
        import redis
        r = redis.Redis(host="127.0.0.1", port=6379, socket_connect_timeout=3)
        r.ping()
        return r
    except Exception:
        return None


# ====================================================== cache dam (stampede)

async def ca_cache_dam():
    """TTL het cung luc -> tat ca request cung danh xuong database.

    Khac biet giua hai ve KHONG phai cache co hay khong, ma la co CHOT hay
    khong: mot request di nap, nhung request con lai cho ket qua cua no.
    """
    N, NAP = 200, 0.05
    dem = {"a": 0, "b": 0}

    async def nap(khoa):
        await asyncio.sleep(NAP)
        return "gia tri"

    # --- A: het han la ai cung tu di nap
    kho_a = {}

    async def doc_a(_):
        if "k" not in kho_a:
            dem["a"] += 1
            kho_a["k"] = await nap("k")
        return kho_a["k"]

    # --- B: mot chot, ai toi sau thi cho ket qua cua nguoi dau
    kho_b, chot, dang = {}, asyncio.Lock(), {}

    async def doc_b(_):
        if "k" in kho_b:
            return kho_b["k"]
        async with chot:
            if "k" not in kho_b:
                dem["b"] += 1
                kho_b["k"] = await nap("k")
        return kho_b["k"]

    t0 = time.perf_counter()
    await asyncio.gather(*(doc_a(i) for i in range(N)))
    ta = time.perf_counter() - t0
    t0 = time.perf_counter()
    await asyncio.gather(*(doc_b(i) for i in range(N)))
    tb = time.perf_counter() - t0
    return dict(loai="dem", hoi=f"{N} request cùng lúc, cache vừa hết hạn",
                a="ai cũng tự đi nạp", b="một chốt, người sau chờ",
                ka=f"{dem['a']} lần nạp, {ta * 1000:.0f} ms",
                kb=f"{dem['b']} lần nạp, {tb * 1000:.0f} ms",
                them=[f"số lần đánh xuống database chênh nhau "
                      f"{dem['a'] // max(1, dem['b'])} lần"])


# ====================================================== retry bao

async def ca_retry_bao():
    """Retry KHONG jitter: moi client cung nhip nen chung dam vao cung mot khe.

    Do DINH DON, khong do tong so luot goi. Tong so luot la nhu nhau - moi
    client van thu lai dung ba lan du co jitter hay khong. Cai jitter doi la
    THOI DIEM: khong jitter thi ca 60 client cung tinh day trong mot khe, con
    co jitter thi chung tan ra. Lan dau toi do tong so luot va ra hai ve bang
    nhau, tuc do sai thu.
    """
    N, LAN, CHO, KHE = 60, 3, 0.10, 0.02

    async def chay(jitter):
        moc = []

        async def mot(i):
            for lan in range(LAN + 1):
                moc.append(time.perf_counter())
                await asyncio.sleep(0.002)
                if lan < LAN:
                    cho = CHO * (2 ** lan)
                    if jitter:
                        # tan deu theo chi so, khong dung random de lan chay
                        # nao cung ra dung mot ket qua
                        cho *= 0.5 + ((i * 37 % 100) / 100.0)
                    await asyncio.sleep(cho)
        t0 = time.perf_counter()
        await asyncio.gather(*(mot(i) for i in range(N)))
        # gom moc vao cac khe 20ms, lay khe dong nhat
        thung = {}
        for m in moc:
            k = int((m - t0) / KHE)
            thung[k] = thung.get(k, 0) + 1
        return len(moc), max(thung.values()), len(thung)

    ga, da, ka = await chay(False)
    gb, db, kb = await chay(True)
    return dict(loai="dem", hoi=f"{N} client, mỗi client thử lại {LAN} lần",
                a="retry đều nhịp", b="retry có jitter",
                ka=f"dồn vào {ka} khe {KHE * 1000:.0f}ms",
                kb=f"trải ra {kb} khe {KHE * 1000:.0f}ms",
                them=[f"tổng lượt gọi BẰNG NHAU ({ga}) — jitter không giảm số "
                      f"lượt mà DÀN chúng ra",
                      f"một cú bấm của người dùng nở thành {ga // N} lượt gọi",
                      f"đỉnh cả hai đều {da} lượt: lượt gọi ĐẦU TIÊN thì cả "
                      f"{N} client vẫn bắn cùng lúc, jitter chỉ đổi các lượt sau"])


# ====================================================== thieu timeout

async def ca_thieu_timeout():
    """Mot dich vu ngoai treo. Co timeout thi hong mot phan, khong thi hong het."""
    N, TREO, HAN = 50, 5.0, 0.30

    async def goi(i, treo):
        if i % 10 == 0:
            await asyncio.sleep(TREO)      # mot phan muoi so request bi treo
        else:
            await asyncio.sleep(0.02)
        return i

    async def chay(han):
        xong = hong = 0
        t0 = time.perf_counter()

        async def mot(i):
            nonlocal xong, hong
            try:
                if han:
                    await asyncio.wait_for(goi(i, True), timeout=han)
                else:
                    await asyncio.wait_for(goi(i, True), timeout=2.0)
                xong += 1
            except (asyncio.TimeoutError, TimeoutError):
                hong += 1
        await asyncio.gather(*(mot(i) for i in range(N)))
        return xong, hong, time.perf_counter() - t0

    xa, ha, ta = await chay(None)
    xb, hb, tb = await chay(HAN)
    return dict(loai="dem", hoi=f"{N} request, 1/10 gọi ra ngoài bị treo {TREO}s",
                a="timeout 2 giây", b=f"timeout {HAN} giây",
                ka=f"{xa} xong / {ha} hỏng, cả lượt {ta * 1000:.0f} ms",
                kb=f"{xb} xong / {hb} hỏng, cả lượt {tb * 1000:.0f} ms",
                them=["số hỏng bằng nhau, khác nhau ở thời gian người dùng "
                      "phải ngồi chờ"])


# ====================================================== tru tien hai lan

async def ca_tru_hai_lan():
    """Doc roi ghi ma khong khoa: hai luong cung doc mot gia tri cu."""
    N = 200

    async def chay(co_khoa):
        so_du = {"v": N}
        tru = 0
        k = asyncio.Lock()

        async def mot():
            nonlocal tru
            if co_khoa:
                async with k:
                    v = so_du["v"]
                    await asyncio.sleep(0)
                    if v > 0:
                        so_du["v"] = v - 1
                        tru += 1
            else:
                v = so_du["v"]
                await asyncio.sleep(0)      # nhuong luot -> khe ho
                if v > 0:
                    so_du["v"] = v - 1
                    tru += 1
        await asyncio.gather(*(mot() for _ in range(N)))
        return so_du["v"], tru

    da, ta_ = await chay(False)
    db, tb_ = await chay(True)
    return dict(loai="dem", hoi=f"{N} yêu cầu trừ 1, số dư ban đầu {N}",
                a="đọc rồi ghi, không khoá", b="có khoá",
                ka=f"trừ {ta_} lần, số dư còn {da}",
                kb=f"trừ {tb_} lần, số dư còn {db}",
                them=[f"bản không khoá GHI ĐÈ mất {da} lần trừ: đếm được "
                      f"{ta_} lần trừ mà số dư chỉ giảm {N - da}"])


# ====================================================== GIL va viec CHO

def ca_gil_luong():
    """GIL khong lam luong vo dung: viec CHO van chay chong len nhau."""
    import threading
    N, CHO = 8, 0.15

    def viec():
        time.sleep(CHO)          # gia lap cho mang: nha GIL ra

    t0 = time.perf_counter()
    for _ in range(N):
        viec()
    tuan_tu = time.perf_counter() - t0

    t0 = time.perf_counter()
    ts = [threading.Thread(target=viec) for _ in range(N)]
    [t.start() for t in ts]
    [t.join() for t in ts]
    luong = time.perf_counter() - t0
    return dict(loai="toc do", hoi=f"{N} việc CHỜ, mỗi việc {CHO}s",
                a="tuần tự", b=f"{N} luồng", ta=tuan_tu, tb=luong,
                them=["GIL được nhả ra trong lúc chờ, nên luồng vẫn chồng "
                      "lên nhau được"])


# ====================================================== redis mot lenh cham

def ca_redis_lenh_cham():
    """Redis mot luong: mot lenh cham chan tat ca lenh dang xep sau no."""
    r = _redis()
    if r is None:
        return None
    r.delete("bench:lon")
    r.rpush("bench:lon", *[f"x{i}" for i in range(200_000)])
    t = []
    for _ in range(20):
        t0 = time.perf_counter()
        r.ping()
        t.append(time.perf_counter() - t0)
    nen = st.median(t)

    import threading
    ket = {}

    def cham():
        t0 = time.perf_counter()
        r2 = _redis()
        r2.lrange("bench:lon", 0, -1)          # O(N) tren 200.000 phan tu
        ket["cham"] = time.perf_counter() - t0

    th = threading.Thread(target=cham)
    th.start()
    time.sleep(0.002)
    t0 = time.perf_counter()
    r.ping()
    ket["ping"] = time.perf_counter() - t0
    th.join()
    r.delete("bench:lon")
    return dict(loai="toc do", hoi="PING lúc bình thường so với PING trong khi "
                                   "một LRANGE 200.000 phần tử đang chạy",
                a="PING lúc rảnh", b="PING lúc bị chặn",
                ta=nen, tb=ket["ping"],
                them=[f"lệnh chậm đó mất {ket['cham'] * 1000:.0f} ms"])


CA = {
    "cache_dam": ca_cache_dam,
    "retry_bao": ca_retry_bao,
    "thieu_timeout": ca_thieu_timeout,
    "tru_hai_lan": ca_tru_hai_lan,
    "gil_luong": ca_gil_luong,
    "redis_cham": ca_redis_lenh_cham,
}


def _ms(x):
    return f"{x * 1000:.2f} ms" if x >= 0.001 else f"{x * 1e6:.0f} µs"


def main():
    in_moc()
    print()
    ban = []
    for k in (sys.argv[1:] or list(CA)):
        if k not in CA:
            print(f"khong co ca {k!r}. Co: {', '.join(CA)}")
            continue
        f = CA[k]
        r = asyncio.run(f()) if asyncio.iscoroutinefunction(f) else f()
        ranh, ty = kiem_may(im=True)
        if not ranh:
            ban.append(f"{k} ({ty:.2f}x)")
        print(f"=== {k} ===" + ("" if ranh else f"   [MAY BAN {ty:.2f}x]"))
        if r is None:
            print("  (bo qua: khong noi duoc Redis, xem CAI-DAT-WSL.md)\n")
            continue
        print(f"  {r['hoi']}")
        if r["loai"] == "toc do":
            ta, tb = r["ta"], r["tb"]
            nhanh = "B" if tb < ta else "A"
            lan = (max(ta, tb) / min(ta, tb)) if min(ta, tb) else 0
            print(f"  A  {r['a']:26} {_ms(ta):>11}")
            print(f"  B  {r['b']:26} {_ms(tb):>11}")
            print(f"  -> {nhanh} nhanh hon {lan:.1f} lan")
        else:
            print(f"  A  {r['a']:26} {r['ka']}")
            print(f"  B  {r['b']:26} {r['kb']}")
        for d in r.get("them", []):
            print(f"     {d}")
        print()
    canh_bao(ban)


if __name__ == "__main__":
    main()
