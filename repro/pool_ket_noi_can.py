"""Do that: pool ket noi can trong khi database van rong rai.

Chay:  py repro/pool_ket_noi_can.py     (mat khoang 12 giay)

Trieu chung nghe vo ly nen phai do chu khong duoc suy: API timeout hang loat
NHUNG database gan nhu khong lam gi. Ca hai ve deu dung cung mot luc, va script
nay in ra bang chung cho ca hai.

Co che: code mo transaction, GOI MOT API BEN NGOAI o giua, roi moi commit. Ket
noi bi giu suot ca cu goi do. Database chi lam viec vai mili giay dau va vai
mili giay cuoi, con o giua no ngoi khong - nhung ket noi thi khong ai duoc dung.

Pool 10 ket noi. Request thu 11 tro di khong con gi de lay, phai xep hang. Xep
hang lau hon timeout thi that bai, va no that bai o TANG UNG DUNG chu khong
phai o database - nen moi bang do cua database deu sach.

So in ra dung thang vao screenplays/pool-can.yaml, khong lam tron cho dep.

Script dung `asyncio.sleep` that chu khong mo phong dong ho, nen moi lan chay
lech vai phan tram: so timeout dao quanh 38-39, ty le hong quanh 32%. Screenplay
phai lay so tu DUNG MOT luot chay, khong nhat moi cho mot con so - hai so tu hai
luot khac nhau dat canh nhau tren cung mot khung hinh se khong cong ra dung.
Nhung con so KHONG dao: pool 10, giu ket noi 810ms, database lam viec 10ms.
"""
import asyncio
import time

POOL = 10           # so ket noi trong pool
N_REQ = 120         # so request gui toi
RATE = 40           # request moi giay
DB_MS = 5           # database that su lam viec bao lau moi lan cham vao
API_MS = 800        # cu goi API ben ngoai NAM TRONG transaction
TIMEOUT = 3.0       # request cho lau hon nay thi bo cuoc
MAU_MS = 100        # lay mau do sau hang doi bao lau mot lan


class Pool:
    """Pool ket noi, kem hai bo dem de tra loi hai cau hoi khac nhau.

    `dang_cho` tra loi "hang doi sau bao nhieu" - do la cai nguoi dung cam nhan.
    `db_ban_giay` tra loi "database co ban khong" - do la cai bang do hien thi.
    Hai con so nay di nguoc chieu nhau, va do la ca noi dung cua video.
    """

    def __init__(self, n):
        self.sem = asyncio.Semaphore(n)
        self.n = n
        self.dang_cho = 0
        self.db_ban_giay = 0.0
        self.dinh_cho = 0


async def mot_request(pool, ket_qua):
    t0 = time.perf_counter()
    pool.dang_cho += 1
    pool.dinh_cho = max(pool.dinh_cho, pool.dang_cho)
    try:
        await asyncio.wait_for(pool.sem.acquire(), timeout=TIMEOUT)
    except (asyncio.TimeoutError, TimeoutError):
        pool.dang_cho -= 1
        ket_qua.append(("timeout", time.perf_counter() - t0))
        return
    pool.dang_cho -= 1
    cho = time.perf_counter() - t0
    try:
        # BEGIN + cau SELECT dau tien: database lam viec that
        await asyncio.sleep(DB_MS / 1000)
        pool.db_ban_giay += DB_MS / 1000
        # goi API ben ngoai. Database ngoi khong, ket noi VAN BI GIU.
        await asyncio.sleep(API_MS / 1000)
        # UPDATE + COMMIT
        await asyncio.sleep(DB_MS / 1000)
        pool.db_ban_giay += DB_MS / 1000
    finally:
        pool.sem.release()
    ket_qua.append(("xong", cho))


async def lay_mau(pool, moc, dung):
    while not dung.is_set():
        moc.append(pool.dang_cho)
        await asyncio.sleep(MAU_MS / 1000)


async def chay():
    pool = Pool(POOL)
    ket_qua, moc = [], []
    dung = asyncio.Event()
    do = asyncio.create_task(lay_mau(pool, moc, dung))

    t0 = time.perf_counter()
    viec = []
    for i in range(N_REQ):
        viec.append(asyncio.create_task(mot_request(pool, ket_qua)))
        await asyncio.sleep(1 / RATE)
    await asyncio.gather(*viec)
    tong = time.perf_counter() - t0

    dung.set()
    await do
    return pool, ket_qua, moc, tong


def main():
    pool, ket_qua, moc, tong = asyncio.run(chay())

    xong = [c for k, c in ket_qua if k == "xong"]
    hong = [c for k, c in ket_qua if k == "timeout"]
    xong.sort()

    print(f"Pool {POOL} ket noi. {N_REQ} request toi trong "
          f"{N_REQ / RATE:.1f} giay ({RATE} request/giay).")
    print(f"Moi request giu ket noi {DB_MS * 2 + API_MS} ms, trong do database "
          f"chi lam viec {DB_MS * 2} ms.\n")

    print(f"{'ket qua':28} {'so luong':>9}")
    print("-" * 40)
    print(f"{'xong':28} {len(xong):9}")
    print(f"{'timeout sau ' + str(TIMEOUT) + 's':28} {len(hong):9}")
    print(f"{'ty le hong':28} {len(hong) / N_REQ * 100:8.1f}%\n")

    if xong:
        def bp(q):
            return xong[min(len(xong) - 1, int(len(xong) * q))]
        print(f"thoi gian cho ket noi:  giua {bp(0.5) * 1000:6.0f} ms   "
              f"p95 {bp(0.95) * 1000:6.0f} ms   dinh {xong[-1] * 1000:6.0f} ms")

    print(f"dinh hang doi:          {pool.dinh_cho} request cung cho mot luc\n")

    # --- ve cua trieu chung nghe vo ly: database rong rai
    ban = pool.db_ban_giay / (tong * POOL) * 100
    print(f"Tong thoi gian chay:    {tong:.1f} giay")
    print(f"Database lam viec that: {pool.db_ban_giay:.2f} giay cong don")
    print(f"=> Neu {POOL} ket noi deu co the ban ca {tong:.1f} giay thi "
          f"database moi dung {ban:.1f}% suc.")
    print("   Bang do database sach bong. Pool thi can tu giay thu nhat.\n")

    # --- chuoi so dan thang vao `curve` cua canh `queue`
    # Rut gon nhung GIU LAI MAU DINH. Lay mau deu tay thi rat de truot dinh -
    # lan dau chay ra chuoi co dinh 69 trong khi dinh that la 70, va kich ban
    # dung ca hai con so o hai cho khac nhau tren cung mot khung hinh.
    buoc = max(1, len(moc) // 12)
    curve = moc[::buoc][:13]
    if max(curve) < max(moc):
        i_that = moc.index(max(moc))
        i_gan = min(range(len(curve)),
                    key=lambda k: abs(k * buoc - i_that))
        curve[i_gan] = max(moc)
    print(f"Do sau hang doi, lay mau {MAU_MS}ms mot lan, rut gon con "
          f"{len(curve)} moc:")
    print(f"  curve: {curve}")
    print(f"  (day du {len(moc)} moc: dinh {max(moc)}, cuoi {moc[-1]})")


if __name__ == "__main__":
    main()
