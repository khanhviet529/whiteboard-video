"""LIMIT/OFFSET bo sot ban ghi khi co insert dong thoi.

Khong bia gi ca: chay that tren sqlite, dem xem nguoi dung nhin thay bao nhieu
ban ghi trong tong so, va ban nao bi bo sot.

    python repro/phan_trang_bo_sot.py
"""
import sqlite3

PAGE = 5

db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE bai (id INTEGER PRIMARY KEY, ten TEXT)")
db.executemany("INSERT INTO bai (ten) VALUES (?)",
               [(f"bai-{i:02d}",) for i in range(1, 21)])
db.commit()

def trang(offset):
    return [r[0] for r in db.execute(
        "SELECT ten FROM bai ORDER BY id DESC LIMIT ? OFFSET ?", (PAGE, offset))]

print(f"20 ban ghi, moi trang {PAGE}, sap xep moi nhat truoc\n")
thay = []
p1 = trang(0)
thay += p1
print(f"trang 1 -> {p1}")

# Giua hai lan tai trang, co 3 ban ghi moi duoc them vao
db.executemany("INSERT INTO bai (ten) VALUES (?)",
               [(f"MOI-{i}",) for i in (1, 2, 3)])
db.commit()
print("   ... 3 ban ghi moi duoc insert ...")

p2 = trang(PAGE)
thay += p2
print(f"trang 2 -> {p2}")

tat_ca = [r[0] for r in db.execute("SELECT ten FROM bai ORDER BY id DESC")]
goc = [x for x in tat_ca if not x.startswith("MOI-")]
bo_sot = [x for x in goc[:PAGE * 2] if x not in thay]
lap = [x for x in set(thay) if thay.count(x) > 1]

print(f"\nnguoi dung thay {len(thay)} dong qua 2 trang")
print(f"bi BO SOT hoan toan : {bo_sot}")
print(f"bi HIEN HAI LAN     : {lap}")
