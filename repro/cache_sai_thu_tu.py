"""Xoa cache TRUOC khi ghi DB de lai gia cu trong cache - dung lai bang thread that.

Khong bia so: chay N lan cho moi thu tu, dem xem bao nhieu lan cache ket thuc voi
GIA CU. Ket qua dung lam so lieu cho screenplay cache-stale.yaml.

    python repro/cache_sai_thu_tu.py

Co che: mot luong GHI va mot luong DOC chay chong len nhau.

  sai thu tu   xoa cache -> (khe ho) -> ghi DB
               luong doc chen vao dung khe ho: cache rong nen no xuong DB, doc
               duoc gia CU (vi chua ghi xong), roi nap chinh gia cu do vao cache.
               Sau do khong ai xoa lan nua -> cache giu gia cu.

  dung thu tu  ghi DB -> (khe ho) -> xoa cache
               luong doc chen vao chi co the doc duoc gia MOI, vi DB da ghi xong.
"""
import threading
import time

CU, MOI = 100_000, 120_000
KHE_HO = 0.003          # 3 mili giay, dung con so trong video
LAN = 200


def chay(dung_thu_tu):
    db = {"gia": CU}
    cache = {"gia": CU}
    doc_duoc = []

    def ghi():
        if dung_thu_tu:
            db["gia"] = MOI
            time.sleep(KHE_HO)
            cache.pop("gia", None)
        else:
            cache.pop("gia", None)
            time.sleep(KHE_HO)
            db["gia"] = MOI

    def doc():
        # cho mot chut de roi dung vao khe ho giua hai lenh cua luong ghi
        time.sleep(KHE_HO / 2)
        if "gia" in cache:
            doc_duoc.append(cache["gia"])
            return
        v = db["gia"]           # cache miss -> xuong DB
        doc_duoc.append(v)
        cache["gia"] = v        # nap lai vao cache

    t1, t2 = threading.Thread(target=ghi), threading.Thread(target=doc)
    t1.start(); t2.start(); t1.join(); t2.join()
    return cache.get("gia"), doc_duoc[0] if doc_duoc else None


for nhan, dung in (("SAI thu tu  (xoa cache truoc)", False),
                   ("DUNG thu tu (ghi DB truoc)   ", True)):
    cache_sai = doc_sai = 0
    for _ in range(LAN):
        c, d = chay(dung)
        if c == CU:
            cache_sai += 1
        if d == CU:
            doc_sai += 1
    print(f"{nhan}  cache ket thuc voi gia CU: {cache_sai:3d}/{LAN} "
          f"({cache_sai / LAN * 100:5.1f}%)   |  luot doc trung gia cu: {doc_sai:3d}")
