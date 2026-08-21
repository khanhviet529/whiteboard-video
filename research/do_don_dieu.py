"""Do MUC DON DIEU cua mot video, bang so chu khong bang cam nhan.

    py research/do_don_dieu.py cache-stale 91-bam-khong-phai-an-danh
    py research/do_don_dieu.py --tat-ca        # moi screenplay da render stills

## Vi sao can file nay

Cau "video dang mot mau" la mot cam nhan, va ca du an nay dung tren luat "so do
hoac bo". Khong do duoc thi khong biet sua cai gi, va cung khong biet sua roi co
hon khong.

Phep do o day la phep BLUR TEST: thu moi khung hinh xuong mot luoi rat tho roi
so tung cap voi nhau. Blur manh thi chu bien mat, mau nhoe, chi con lai DANG
BONG (silhouette) - dung cai ma mat nguoi dung de nhan ra "canh nay giong canh
kia" truoc khi doc duoc bat ky chu nao.

## Doc ket qua the nao

    khac_biet_trung_binh   0..1, cang cao cang da dang. Duoi 0,20 la don dieu
    cap_giong_nhat         hai canh gan trung nhau nhat - do la cho phai sua
    dong_gop_khung         phan chenh lech den TU KHUNG CO DINH, khong tu noi dung

Cot cuoi la cot quan trong nhat va la ly do phep do nay khong dung mot con so.
`bench` ve rail, chip chuong, tieu de, the phu de va dong chan o TOA DO CO DINH
cho moi canh - nen hai canh khac han noi dung van chia nhau khoang 40% dien tich
co muc giong het nhau. Tach hai phan ra thi biet nen sua khung hay sua canh.
"""
import glob
import os
import sys

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

# Luoi tho: 12 cot x 21 hang, giu ty le 9:16. Da thu 24x42 va ket luan giong
# nhau, nhung 12x21 thi in ra man hinh doc duoc nen de doi chieu bang mat.
GW, GH = 12, 21

# Vung san dien, doc thang tu bench.py de khong lech khi ai do doi bo cuc.
from bench import H, STAGE_BOTTOM, STAGE_TOP, W  # noqa: E402


def bong(path, chi_san_dien=False):
    """Dang bong cua mot khung hinh: luoi 12x21, moi o la do sang trung binh.

    Tru nen di truoc khi thu nho: nen cua theme co luoi cham va vet bloom, va
    hai thu do GIONG NHAU o moi canh nen chung lam moi cap khung trong giong
    nhau hon thuc te. Xap xi bang cach tru phan vi 20 cua chinh khung do.
    """
    im = Image.open(path).convert("L")
    if chi_san_dien:
        im = im.crop((0, STAGE_TOP, W, STAGE_BOTTOM))
    a = np.asarray(im.resize((GW, GH), Image.BOX)).astype(np.float32)
    a -= np.percentile(a, 20)
    a = np.clip(a, 0, None)
    m = a.max()
    return a / m if m > 1e-6 else a


def khac(b1, b2):
    """Khoang cach hai dang bong, 0 la trung khop hoan toan."""
    return float(np.abs(b1 - b2).mean())


def in_bong(b):
    """Ve dang bong ra man hinh bang ky tu, de doi chieu bang mat."""
    thang = " .:-=+*#%@"
    return ["".join(thang[min(9, int(v * 9.99))] for v in hang) for hang in b]


def do_mot_video(ten, in_hinh=False):
    thu_muc = os.path.join(ROOT, "build", "stills")
    anh = sorted(glob.glob(os.path.join(thu_muc, "scene-*.png")))
    if len(anh) < 3:
        print(f"  {ten}: chi thay {len(anh)} still, can >= 3. "
              f"Chay `python src/render.py screenplays/{ten}.yaml --stills` truoc")
        return None

    day = [bong(p) for p in anh]
    san = [bong(p, chi_san_dien=True) for p in anh]
    n = len(anh)

    cap = [(khac(day[i], day[j]), khac(san[i], san[j]), i, j)
           for i in range(n) for j in range(i + 1, n)]
    tb_day = sum(c[0] for c in cap) / len(cap)
    tb_san = sum(c[1] for c in cap) / len(cap)
    cap.sort()

    print(f"\n=== {ten}  ({n} canh) ===")
    print(f"  khac biet trung binh  CA KHUNG   {tb_day:.3f}")
    print(f"                        SAN DIEN   {tb_san:.3f}")
    # San dien luon khac nhieu hon ca khung, va TY LE giua hai so cho biet khung
    # co dinh dang lam mo di bao nhieu phan da dang cua noi dung.
    if tb_san > 1e-6:
        print(f"  khung cố định làm phẳng   {(1 - tb_day / tb_san):.0%} "
              f"độ đa dạng của nội dung")
    print("  ba cặp cảnh giống nhau nhất (theo sân diễn):")
    for _, s, i, j in sorted(cap, key=lambda c: c[1])[:3]:
        ta = os.path.basename(anh[i]).replace(".png", "")
        tb = os.path.basename(anh[j]).replace(".png", "")
        print(f"      {s:.3f}  {ta:24} <-> {tb}")
    if in_hinh:
        print("\n  dang bong tung canh (san dien):")
        for k, p in enumerate(anh):
            ten_c = os.path.basename(p).replace(".png", "").replace("scene-", "")
            hang = in_bong(san[k])
            for r, dong in enumerate(hang):
                print(f"      {ten_c if r == 0 else '':24} |{dong}|")
            print()
    return tb_day, tb_san


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not args:
        raise SystemExit(__doc__)
    do_mot_video(args[0], in_hinh="--hinh" in sys.argv)


if __name__ == "__main__":
    main()
