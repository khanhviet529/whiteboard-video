"""Bo do dung chung cho cac chu de can PostgreSQL that.

    py repro/bench_pg.py              # chay het, in bang
    py repro/bench_pg.py index_bo_qua # chay mot ca

Vi sao khong dung sqlite: sqlite khong co MVCC, khong co gap lock, khong co
autovacuum, khong co planner doi y theo thong ke. 15 chu de manh nhat trong
KE-HOACH-90.md nam dung o nhung cho do.

Ket noi lay tu CAI-DAT-WSL.md: PostgreSQL chay trong WSL2, script nay chay bang
Python TREN WINDOWS va noi vao qua cau localhost. Nghia la moi cau truy van co
do tre di ve THAT, khac han sqlite chay cung tien trinh. Script IN RA do tre
nen do luc bat dau moi lan chay - dung chep con so do vao kich ban, no dao
theo tai may (da thay 0,29ms va 0,64ms o hai lan chay khac nhau).

## Hieu chuan chi kiem luc BAT DAU luot

Khac `bench_python.py`, file nay KHONG kiem hieu chuan giua cac ca. Postgres
chay trong WSL tren cung CPU, va moi ca chen 200-500 nghin dong, nen sau moi ca
hieu chuan luon bao "may ban 2-3 lan" - do la tai do CHINH BO DO gay ra. Bao
nhu vay la bao nham, ma bao nham thi nguoi ta bo qua ca nhung lan bao dung.

Con so hieu chuan in o dau luot cho biet may co ranh luc bat dau khong, va do
la thu duy nhat kiem duoc o day.

## Hai dieu khac han sqlite, phai nho khi viet ca moi

1. TRANG THAI SONG QUA NHIEU LAN CHAY. Moi ca phai tu `DROP TABLE IF EXISTS` o
   dau, khong thi lan chay thu hai do tren du lieu cua lan thu nhat va ra so
   khac. sqlite `:memory:` khong co van de nay.

2. PLANNER CAN THONG KE. Sau khi nap du lieu phai `ANALYZE`, khong thi planner
   uoc luong bang mac dinh va chon sai cach chay - do la do sai chu khong phai
   phat hien ra dieu gi.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _hieu_chuan import in_moc  # noqa: E402

PG = dict(host="127.0.0.1", port=5432, dbname="bench",
          user="bench", password="bench")
# 21 chu khong 5. Voi LAP=5, ty le cua `index_bo_qua` dao 23-90 lan qua bon
# luot chay tren may ranh - khong the cong bo mot con so nao tu day. Postgres co
# bo dem trang, checkpoint va autovacuum chay nen, cong them chang loopback cua
# WSL, nen phai lay nhieu mau hon han so voi do trong tien trinh.
LAP = 21


def noi():
    try:
        import psycopg
    except ImportError:
        raise SystemExit('chua co psycopg: py -m pip install "psycopg[binary]"')
    for lan in range(2):
        try:
            return psycopg.connect(**PG, connect_timeout=5, autocommit=True)
        except Exception as e:
            if lan:
                raise SystemExit(
                    f"khong noi duoc PostgreSQL: {str(e).strip()[:120]}\n"
                    f"Chay `py repro/_kiem_ket_noi.py` de xem thieu buoc nao.")
            # WSL tu tat sau mot luc khong dung, va lan noi dau tien sau do luon
            # timeout. Tu danh thuc thay vi bat nguoi dung nho.
            import subprocess
            print("  (WSL dang ngu, danh thuc...)")
            subprocess.run(["wsl.exe", "--", "true"], capture_output=True,
                           timeout=90)
            time.sleep(3)


def do(cx, sql, tham=None, lap=LAP):
    """Trung vi cua `lap` lan chay. Bo lan dau vi no con phai nap trang."""
    t = []
    for i in range(lap + 1):
        t0 = time.perf_counter()
        cur = cx.execute(sql, tham or ())
        if cur.description:
            cur.fetchall()
        d = time.perf_counter() - t0
        if i:
            t.append(d)
    t.sort()
    return t[len(t) // 2]


def ke_hoach(cx, sql, tham=None):
    """Dong dau cua EXPLAIN - cho biet planner chon cach chay nao."""
    dong = [r[0] for r in
            cx.execute("EXPLAIN (ANALYZE, BUFFERS) " + sql, tham or ()).fetchall()]
    return dong[0].strip(), dong


def do_tre_nen(cx):
    """Do tre mot vong di ve. Moi ca in kem de nguoi doc TRU DI khi can."""
    return do(cx, "SELECT 1", lap=50)


# ============================================================ ca do

def ca_index_bo_qua(cx):
    """Bay: boc ham quanh cot lam index thanh vo dung.

    Day la ca nen tang cho so 06 va so 19 trong KE-HOACH-90.md.
    """
    cx.execute("DROP TABLE IF EXISTS t_idx")
    cx.execute("CREATE TABLE t_idx (id serial primary key, email text)")
    cx.execute("INSERT INTO t_idx (email) SELECT 'nguoi' || g || '@vi.dev' "
               "FROM generate_series(1, 200000) g")
    cx.execute("CREATE INDEX ix_email ON t_idx (email)")
    cx.execute("ANALYZE t_idx")

    a_sql = "SELECT id FROM t_idx WHERE lower(email) = %s"
    b_sql = "SELECT id FROM t_idx WHERE email = %s"
    v = "nguoi150000@vi.dev"
    ka, _ = ke_hoach(cx, a_sql, (v,))
    kb, _ = ke_hoach(cx, b_sql, (v,))
    return dict(
        loai="toc do", hoi="Tìm một email trong bảng 200.000 dòng, có index",
        a="WHERE lower(email) = ...", b="WHERE email = ...",
        ta=do(cx, a_sql, (v,)), tb=do(cx, b_sql, (v,)),
        them=[f"A chọn: {ka}", f"B chọn: {kb}"])


def ca_count_sao(cx):
    """`COUNT(*)` tren bang lon la thu cham nhat cua trang danh sach. So 09."""
    cx.execute("DROP TABLE IF EXISTS t_cnt")
    cx.execute("CREATE TABLE t_cnt (id serial primary key, tt text)")
    cx.execute("INSERT INTO t_cnt (tt) SELECT 'x' FROM generate_series(1, 500000)")
    cx.execute("ANALYZE t_cnt")
    a_sql = "SELECT count(*) FROM t_cnt"
    b_sql = "SELECT id FROM t_cnt ORDER BY id LIMIT 20"
    ka, _ = ke_hoach(cx, a_sql)
    return dict(
        loai="toc do", hoi="Bảng 500.000 dòng: đếm tổng so với lấy 20 dòng đầu",
        a="SELECT count(*)", b="SELECT ... LIMIT 20",
        ta=do(cx, a_sql), tb=do(cx, b_sql),
        them=[f"A chọn: {ka}"])


def ca_uuid_khoa_chinh(cx):
    """UUID ngau nhien lam khoa chinh: moi lan chen roi vao mot trang khac
    nhau, nen index phai tach trang lien tuc. So 17."""
    ra = {}
    for ten, cot, sinh in (
            ("uuid v4 (ngẫu nhiên)", "uuid", "gen_random_uuid()"),
            ("bigserial (tăng dần)", "bigint", "g")):
        cx.execute("DROP TABLE IF EXISTS t_key")
        cx.execute(f"CREATE TABLE t_key (id {cot} primary key, tt text)")
        t0 = time.perf_counter()
        cx.execute(f"INSERT INTO t_key (id, tt) SELECT {sinh}, 'x' "
                   f"FROM generate_series(1, 300000) g")
        ra[ten] = time.perf_counter() - t0
        ra[ten + "_size"] = cx.execute(
            "SELECT pg_relation_size('t_key_pkey')").fetchone()[0]
    a, b = "uuid v4 (ngẫu nhiên)", "bigserial (tăng dần)"
    return dict(
        loai="toc do", hoi="Chèn 300.000 dòng, khoá chính ngẫu nhiên so với tăng dần",
        a=a, b=b, ta=ra[a], tb=ra[b],
        them=[f"kích thước index: {ra[a + '_size'] / 1e6:.1f} MB "
              f"so với {ra[b + '_size'] / 1e6:.1f} MB"])


def ca_bang_phinh(cx):
    """UPDATE trong MVCC khong sua tai cho ma ghi ban moi. So 20."""
    cx.execute("DROP TABLE IF EXISTS t_bloat")
    cx.execute("CREATE TABLE t_bloat (id serial primary key, n int) "
               "WITH (autovacuum_enabled = off)")
    cx.execute("INSERT INTO t_bloat (n) SELECT 0 FROM generate_series(1, 200000)")
    truoc = cx.execute("SELECT pg_total_relation_size('t_bloat')").fetchone()[0]
    for _ in range(5):
        cx.execute("UPDATE t_bloat SET n = n + 1")
    sau = cx.execute("SELECT pg_total_relation_size('t_bloat')").fetchone()[0]
    chet, pc = cx.execute("SELECT dead_tuple_count, dead_tuple_percent "
                          "FROM pgstattuple('t_bloat')").fetchone()
    return dict(
        loai="dung sai", hoi="200.000 dòng, UPDATE toàn bảng 5 lần",
        a="dung lượng trước", b="dung lượng sau",
        ka=f"{truoc / 1e6:.1f} MB",
        kb=f"{sau / 1e6:.1f} MB  (gấp {sau / truoc:.1f} lần)",
        them=[f"bản chết còn nằm lại: {chet:,} dòng = {pc:.1f}% dung lượng"
              .replace(",", ".")])


CA = {
    "index_bo_qua": ca_index_bo_qua,
    "count_sao": ca_count_sao,
    "uuid_khoa": ca_uuid_khoa_chinh,
    "bang_phinh": ca_bang_phinh,
}


def _ms(x):
    return f"{x * 1000:.2f} ms" if x >= 0.001 else f"{x * 1e6:.0f} µs"


def main():
    cx = noi()
    nen = do_tre_nen(cx)
    print(f"PostgreSQL qua cầu localhost của WSL2. "
          f"Độ trễ nền một vòng đi về: {_ms(nen)}")
    print("(mọi số thời gian dưới đây đã bao gồm độ trễ đó)\n")
    in_moc()
    print()
    for k in (sys.argv[1:] or list(CA)):
        if k not in CA:
            print(f"khong co ca {k!r}. Co: {', '.join(CA)}")
            continue
        # KHONG kiem hieu chuan giua cac ca o day, khac han `bench_python.py`.
        #
        # Ly do: postgres chay trong WSL tren CUNG CPU, va moi ca chen 200-500
        # nghin dong. Sau moi ca thi background writer con dang xa, nen hieu
        # chuan luon bao "may ban 2-3 lan" - do la do CHINH BO DO gay ra, khong
        # phai do viec khac. Bao nhu vay la bao nham, va bao nham thi nguoi ta
        # bo qua ca nhung lan bao dung.
        #
        # Cai kiem duoc la trang thai luc BAT DAU luot, da in o `in_moc()` tren.
        r = CA[k](cx)
        print(f"=== {k} ===")
        print(f"  {r['hoi']}")
        if r["loai"] == "toc do":
            ta, tb = r["ta"], r["tb"]
            nhanh = "B" if tb < ta else "A"
            lan = (max(ta, tb) / min(ta, tb)) if min(ta, tb) else 0
            print(f"  A  {r['a']:30} {_ms(ta):>11}")
            print(f"  B  {r['b']:30} {_ms(tb):>11}")
            print(f"  -> {nhanh} nhanh hon {lan:.0f} lan")
        else:
            print(f"  A  {r['a']:30} {r['ka']}")
            print(f"  B  {r['b']:30} {r['kb']}")
        for d in r.get("them", []):
            print(f"     {d}")
        print()



if __name__ == "__main__":
    main()
