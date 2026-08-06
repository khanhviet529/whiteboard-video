"""`async` khong lam code chay song song - do that de lay so cho screenplay.

Hieu nham pho bien: them `async` vao thi code chay song song nen nhanh hon. Sai.
`async` chay tren MOT luong, cac viec DAN vao nhau chu khong chay cung luc. No
chi nhanh hon khi cac viec co CHO CHO (doc mang, doc dia, sleep) - vi luc cho thi
nhuong luot cho viec khac. Viec CPU-bound khong co cho cho nao de nhuong, nen
`async` khong giup gi.

    python repro/async_khong_phai_song_song.py

In ra bon con so, dung truc tiep lam so lieu trong video.
"""
import asyncio
import time
from concurrent.futures import ProcessPoolExecutor

N = 4                    # so viec
CPU_VONG = 4_000_000     # do nang cua viec CPU
IO_CHO = 0.5             # thoi gian cho cua viec I/O


def viec_cpu(_=None):
    """Viec that su ban CPU - khong co cho nao de nhuong luot."""
    t = 0
    for i in range(CPU_VONG):
        t += i * i
    return t


async def viec_cpu_async(_=None):
    """Boc `async` vao KHONG tao ra cho cho nao. Van chay het roi moi tra."""
    return viec_cpu()


async def viec_io_async(_=None):
    """Co cho cho that -> luc cho thi nhuong luot cho viec khac."""
    await asyncio.sleep(IO_CHO)


def viec_io(_=None):
    time.sleep(IO_CHO)


def do(ten, ham):
    t = time.perf_counter()
    ham()
    return time.perf_counter() - t, ten


async def _gather(f):
    await asyncio.gather(*(f(i) for i in range(N)))


if __name__ == "__main__":
    print(f"{N} viec, moi viec CPU cong {CPU_VONG:,} so hoac cho {IO_CHO}s\n")

    ket = []
    # --- viec CPU ---
    ket.append(do("CPU - tuan tu", lambda: [viec_cpu() for _ in range(N)]))
    ket.append(do("CPU - async", lambda: asyncio.run(_gather(viec_cpu_async))))
    with ProcessPoolExecutor(max_workers=N) as ex:
        ket.append(do("CPU - nhieu tien trinh",
                      lambda: list(ex.map(viec_cpu, range(N)))))
    # --- viec I/O ---
    ket.append(do("I/O - tuan tu", lambda: [viec_io() for _ in range(N)]))
    ket.append(do("I/O - async", lambda: asyncio.run(_gather(viec_io_async))))

    print(f"{'cach chay':26s} {'thoi gian':>10s}  {'so voi tuan tu':>15s}")
    print("-" * 56)
    goc_cpu = ket[0][0]
    goc_io = ket[3][0]
    for i, (giay, ten) in enumerate(ket):
        goc = goc_io if ten.startswith("I/O") else goc_cpu
        print(f"{ten:26s} {giay:9.2f}s  {goc / giay:14.2f}x")
    print("-" * 56)
    print(f"CPU: async nhanh hon tuan tu {goc_cpu / ket[1][0]:.2f} lan  "
          f"(nhieu tien trinh: {goc_cpu / ket[2][0]:.2f} lan)")
    print(f"I/O: async nhanh hon tuan tu {goc_io / ket[4][0]:.2f} lan")
