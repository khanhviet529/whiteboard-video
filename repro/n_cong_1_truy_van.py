"""Do that: N+1 query khong noi ve toc do tung cau ma ve SO LUONG cau.

Chay:  py repro/n_cong_1_truy_van.py

Script nay ton tai vi kich ban n-plus-one.yaml tung ghi ba con so khong khop
nhau: 143 cau, moi cau 3ms, tong 4,2 giay. Nhan ra la 0,43 giay, con thieu gan
bon giay chua duoc giai thich. Chay that thi thay phan thieu do nam o dau.

Ba dieu script do duoc, khong suy dien:

  1. SO CAU that su gui xuong, dem bang `set_trace_callback` chu khong nham tay
  2. THOI GIAN CHAY trong database, do bang sqlite tren cung may
  3. Cach ca hai doi khi doi tu N+1 sang eager load

Mot dieu script KHONG do duoc: do tre moi lan di ve khi database nam o may khac.
sqlite chay trong cung tien trinh nen do tre bang khong. Vi vay bang cuoi in
tong thoi gian theo TUNG MUC do tre, va kich ban phai ghi ro muc no dang dung.
Do la "suy ra" chu khong phai "do duoc" - xem Y-TUONG.md, Cua 1.
"""
import random
import sqlite3
import time

SEED = 7          # co dinh de moi lan chay ra dung mot con so
N_DON = 20        # mot trang danh sach don hang
ITEM_MIN, ITEM_MAX = 3, 8


def dung_du_lieu():
    cx = sqlite3.connect(":memory:")
    cx.executescript("""
        CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT);
        CREATE TABLE products  (id INTEGER PRIMARY KEY, name TEXT);
        CREATE TABLE orders    (id INTEGER PRIMARY KEY, customer_id INTEGER);
        CREATE TABLE items     (id INTEGER PRIMARY KEY, order_id INTEGER,
                                product_id INTEGER);
        CREATE INDEX ix_items_order ON items(order_id);
    """)
    rnd = random.Random(SEED)
    cx.executemany("INSERT INTO customers VALUES (?,?)",
                   [(i, f"khach {i}") for i in range(1, 201)])
    cx.executemany("INSERT INTO products VALUES (?,?)",
                   [(i, f"hang {i}") for i in range(1, 51)])
    cx.executemany("INSERT INTO orders VALUES (?,?)",
                   [(i, rnd.randint(1, 200)) for i in range(1, 501)])
    it, k = [], 1
    for don in range(1, 501):
        for _ in range(rnd.randint(ITEM_MIN, ITEM_MAX)):
            it.append((k, don, rnd.randint(1, 50)))
            k += 1
    cx.executemany("INSERT INTO items VALUES (?,?,?)", it)
    cx.commit()
    return cx


class Dem:
    """Dem cau bang trace callback cua sqlite, khong dem bang tay.

    Dem tay la cho de sai nhat: vong lap long nhau thi rat de bo sot mot tang.
    Chinh cai bo sot do la ly do N+1 song sot qua code review.
    """

    def __init__(self, cx):
        self.cx, self.n = cx, 0

    def __enter__(self):
        self.n = 0
        self.cx.set_trace_callback(lambda _: setattr(self, "n", self.n + 1))
        self.t0 = time.perf_counter()
        return self

    def __exit__(self, *a):
        self.giay = time.perf_counter() - self.t0
        self.cx.set_trace_callback(None)


def duong_n_cong_1(cx):
    """Dung cach ORM sinh code khi khong ai noi truoc la se can gi."""
    dons = cx.execute(
        "SELECT id, customer_id FROM orders ORDER BY id LIMIT ?",
        (N_DON,)).fetchall()
    ra = []
    for don_id, kh_id in dons:
        # don.customer  -> mot cau
        ten = cx.execute("SELECT name FROM customers WHERE id=?",
                         (kh_id,)).fetchone()[0]
        # don.items     -> mot cau nua
        items = cx.execute("SELECT id, product_id FROM items WHERE order_id=?",
                           (don_id,)).fetchall()
        for _, sp_id in items:
            # item.product -> mot cau cho MOI dong hang
            cx.execute("SELECT name FROM products WHERE id=?", (sp_id,)).fetchone()
        ra.append((don_id, ten, len(items)))
    return ra


def duong_eager(cx):
    """Noi truoc nhung gi se can. Ba cau, khong phu thuoc so dong."""
    dons = cx.execute(
        "SELECT o.id, c.name FROM orders o JOIN customers c ON c.id=o.customer_id"
        " ORDER BY o.id LIMIT ?", (N_DON,)).fetchall()
    ids = [d[0] for d in dons]
    cho = ",".join("?" * len(ids))
    rows = cx.execute(
        f"SELECT i.order_id, p.name FROM items i JOIN products p"
        f" ON p.id=i.product_id WHERE i.order_id IN ({cho})", ids).fetchall()
    dem = {}
    for oid, _ in rows:
        dem[oid] = dem.get(oid, 0) + 1
    return [(oid, ten, dem.get(oid, 0)) for oid, ten in dons]


def main():
    cx = dung_du_lieu()

    with Dem(cx) as a:
        ra_a = duong_n_cong_1(cx)
    with Dem(cx) as b:
        ra_b = duong_eager(cx)

    assert sorted(ra_a) == sorted(ra_b), "hai duong phai ra cung ket qua"
    so_dong = sum(x[2] for x in ra_a)

    print(f"Mot trang {N_DON} don hang, tong {so_dong} dong hang.")
    print("Ca hai duong tra ve ket qua giong het nhau.\n")
    print(f"{'duong':22} {'so cau':>7} {'trong database':>16} {'moi cau':>10}")
    print("-" * 58)
    for ten, d in (("N+1 (ORM mac dinh)", a), ("eager load", b)):
        print(f"{ten:22} {d.n:7} {d.giay * 1000:13.1f} ms "
              f"{d.giay / d.n * 1000:9.3f} ms")

    print(f"\nSo cau gap {a.n / b.n:.0f} lan. Thoi gian trong database chi gap "
          f"{a.giay / b.giay:.1f} lan.")
    print("Chenh lech do la ca van de: database khong he cham, chi la bi hoi "
          "qua nhieu lan.\n")

    # --- phan KHONG do duoc: do tre moi lan di ve khi database o may khac.
    # sqlite chay trong cung tien trinh nen do tre bang khong. In ca bang de
    # kich ban phai chon va ghi ro mot muc, thay vi muon dau ra mot con so.
    print("sqlite nam trong cung tien trinh nen do tre di ve bang khong.")
    print("Database that nam o may khac. Cong do tre vao MOI cau:\n")
    print(f"{'do tre moi lan di ve':>22} {'N+1':>10} {'eager':>10}")
    print("-" * 46)
    for ms in (0.5, 1, 5, 15, 25):
        ta = a.giay + a.n * ms / 1000
        tb = b.giay + b.n * ms / 1000
        print(f"{ms:19g} ms {ta:9.2f}s {tb:9.2f}s")
    print("\nSo cau la thu do duoc. Do tre la tham so - kich ban dung muc nao "
          "thi phai ghi muc do len man hinh.")


if __name__ == "__main__":
    main()
