"""Lam video tu MOT tam anh: cho mot vung trong anh phat sang, bat roi tat.

    python src/anh_sang.py D:\\xe.jpg --vung 0.42,0.55,0.58,0.66 --nhip 1.4
    python src/anh_sang.py D:\\xe.jpg --tu-tim            # tu tim vung sang nhat
    python src/anh_sang.py D:\\xe.jpg --tu-tim --so 2 --mau 255,240,180

Ra `out/<ten-anh>-sang.mp4`, khung doc 1080x1920 (hoac giu ti le anh voi --nguyen).

## Cach lam sang, va vi sao khong dung cach hien nhien

Cach hien nhien la tang do sang ca vung do len. Nhung den xe khong hoat dong nhu
vay: cai lam mat nguoi ta thay "no dang sang" khong phai ban than bong den sang
hon, ma la QUANG SANG TOA RA quanh no. Nen o day:

  1. Cat vung can sang ra, giu lai phan sang nhat cua chinh no (nguong theo do
     sang) -> duoc mot "hat sang".
  2. Blur hat do that manh, to hon vung goc nhieu lan -> duoc quang sang.
  3. Cong quang sang vao anh theo che do SCREEN, cuong do doi theo thoi gian.

Cong theo screen chu khong phai cong thang: cong thang thi vung sang bi chay
trang bet, mat het chi tiet. Screen giu duoc net ben duoi.

## Dung lam hero cho trang web: hai thu bat buoc

1. `-movflags +faststart` - dua bang muc (moov atom) len DAU file. Khong co no
   thi trinh duyet phai tai HET file moi bat dau phat duoc. Luon bat, khong co
   ly do nao de tat.
2. `--lap` - cat thoi luong xuong dung mot so NGUYEN chu ky. Khong cat thi frame
   cuoi va frame dau lech pha nhau, va vong lap nhay mot cai moi lan quay dau.
   Do duoc tren ban 5 giay / nhip 1,6 giay: lech 3,2 muc sang o vung den.

Video khong co tieng - can thiet de trinh duyet cho autoplay.

## Nhip bat/tat

`--nhip` la so giay cho MOT lan bat-tat tron ven. Duong cong dung `sin` binh
phuong chu khong phai sin: den that co pha sang nhanh, tat cham, va nam o muc
tat lau hon muc sang - sin binh phuong cho dung dang do.
"""
import argparse
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

FPS = 30
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out")
KHUNG = (1080, 1920)     # khung doc mac dinh, giong cac video khac cua kenh


def _doc_anh(path, nguyen=False):
    """Nap anh, dat vao khung doc (hoac giu nguyen ti le neu `nguyen`)."""
    im = Image.open(path).convert("RGB")
    if nguyen:
        w, h = im.size
        # ffmpeg can canh chan
        return im.crop((0, 0, w - w % 2, h - h % 2))
    W, H = KHUNG
    k = min(W / im.width, H / im.height)
    im2 = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))),
                    Image.LANCZOS)
    nen = Image.new("RGB", (W, H), (8, 8, 10))
    nen.paste(im2, ((W - im2.width) // 2, (H - im2.height) // 2))
    return nen


def tu_tim_vung(im, so=1, o=24):
    """Tim `so` vung sang nhat -> dung khi khong muon go toa do bang tay.

    Chia anh thanh luoi o vuong, tinh do sang trung binh moi o, lay cac o sang
    nhat roi gom o lien nhau lai thanh mot vung. Tho nhung dung cho den xe: den
    bao gio cung la cho sang nhat trong khung.
    """
    a = np.asarray(im.convert("L")).astype(np.float32)
    H, W = a.shape
    gy, gx = H // o, W // o
    if gy == 0 or gx == 0:
        return [(0.4, 0.4, 0.6, 0.6)]
    khoi = a[:gy * o, :gx * o].reshape(gy, o, gx, o).mean(axis=(1, 3))
    thu = sorted(((khoi[r, c], r, c) for r in range(gy) for c in range(gx)),
                 reverse=True)
    da_lay, vung = set(), []
    for _, r, c in thu:
        if len(vung) >= so:
            break
        if any(abs(r - rr) <= 2 and abs(c - cc) <= 2 for rr, cc in da_lay):
            continue          # sat mot vung da lay -> cung mot cai den
        da_lay.add((r, c))
        # no ra hai o moi phia cho quang sang co cho
        x0 = max(0, (c - 2) * o) / W
        y0 = max(0, (r - 2) * o) / H
        x1 = min(W, (c + 3) * o) / W
        y1 = min(H, (r + 3) * o) / H
        vung.append((x0, y0, x1, y1))
    return vung or [(0.4, 0.4, 0.6, 0.6)]


def _hat_sang(im, vung, nguong=170, no=3.0):
    """Tra ve mot lop RGB cung co anh, chua QUANG SANG da blur san (chua nhan
    cuong do). Tinh MOT lan roi dung cho moi frame - blur la phan dat nhat."""
    W, H = im.size
    a = np.zeros((H, W, 3), np.float32)
    src = np.asarray(im).astype(np.float32)
    for (fx0, fy0, fx1, fy1) in vung:
        x0, y0 = int(fx0 * W), int(fy0 * H)
        x1, y1 = int(fx1 * W), int(fy1 * H)
        if x1 <= x0 or y1 <= y0:
            continue
        o = src[y0:y1, x0:x1]
        lum = o.mean(axis=2)
        # chi lay phan sang hon `nguong` -> hat sang, khong phai ca cai xe
        m = np.clip((lum - nguong) / max(1.0, 255.0 - nguong), 0, 1)[..., None]
        a[y0:y1, x0:x1] = np.maximum(a[y0:y1, x0:x1], o * m)
    lop = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    r = max(8, int(min(W, H) * 0.02 * no))
    return lop.filter(ImageFilter.GaussianBlur(r))


def _ban_tat(im, vung, nguong=170, toi=0.22):
    """Ban anh voi DEN DA TAT: cac pixel sang trong vung bi keo toi han.

    Vi sao can: trong anh goc den xe DA SANG. Neu chi cong them quang sang thi
    hieu ung ra "den sang manh hon roi yeu di", khong phai "bat len roi tat".
    Muon ra bat/tat thi phai co mot ban den TAT de noi vao o day nhip.

    Chi keo toi phan VUOT nguong, va keo theo do vuot - nen vien den mo dan tu
    nhien, khong thanh mot mieng vuong toi bet.
    """
    a = np.asarray(im).astype(np.float32)
    ra = a.copy()
    H, W = a.shape[:2]
    for (fx0, fy0, fx1, fy1) in vung:
        x0, y0 = int(fx0 * W), int(fy0 * H)
        x1, y1 = int(fx1 * W), int(fy1 * H)
        if x1 <= x0 or y1 <= y0:
            continue
        o = a[y0:y1, x0:x1]
        lum = o.mean(axis=2)
        m = np.clip((lum - nguong) / max(1.0, 255.0 - nguong), 0, 1)[..., None]
        ra[y0:y1, x0:x1] = o * (1.0 - m * (1.0 - toi))
    return ra


def _cuong_do(t, nhip, kieu="nhay"):
    """0..1 theo thoi gian. Xem docstring dau file ve sin binh phuong."""
    if nhip <= 0:
        return 1.0
    p = (t % nhip) / nhip
    if kieu == "lien":            # sang lien tuc, chi thay doi nhe
        return 0.55 + 0.45 * math.sin(2 * math.pi * p) ** 2
    return math.sin(math.pi * p) ** 2


def lam_video(path, vung, giay=4.0, nhip=1.2, kieu="nhay", manh=1.6,
              mau=None, nguyen=False, ra=None, tat=True, toi=0.22,
              crf=18, lap=False, poster=False):
    import imageio_ffmpeg
    im = _doc_anh(path, nguyen)
    quang = _hat_sang(im, vung)
    if mau:
        # nhuom quang sang: nhan tung kenh: den vang thi (255,240,180)
        q = np.asarray(quang).astype(np.float32)
        t = np.array(mau, np.float32) / 255.0
        quang = Image.fromarray(np.clip(q * t, 0, 255).astype(np.uint8))
    nen = np.asarray(im).astype(np.float32)
    qa = np.asarray(quang).astype(np.float32)
    nen_tat = _ban_tat(im, vung, toi=toi) if tat else nen

    os.makedirs(OUT, exist_ok=True)
    ten = os.path.splitext(os.path.basename(path))[0]
    dich = ra or os.path.join(OUT, f"{ten}-sang.mp4")
    if lap and nhip > 0:
        # Cat xuong so NGUYEN chu ky. sin binh phuong tai pha 0 va pha 1 bang
        # nhau, nen n frame tron chu ky thi frame 0 noi lien mach voi frame n-1.
        chu_ky = max(1, int(giay / nhip))
        giay_moi = chu_ky * nhip
        if abs(giay_moi - giay) > 1e-6:
            print(f"  --lap: cat {giay}s -> {giay_moi}s ({chu_ky} chu ky tron)")
        giay = giay_moi
    n = int(round(giay * FPS))
    print(f"anh {im.size[0]}x{im.size[1]} | {len(vung)} vung sang | "
          f"{giay}s = {n} frame | nhip {nhip}s | crf {crf}")

    w = imageio_ffmpeg.write_frames(
        dich, im.size, fps=FPS, codec="libx264", pix_fmt_in="rgb24",
        macro_block_size=1, ffmpeg_log_level="error",
        output_params=["-crf", str(crf), "-pix_fmt", "yuv420p",
                       "-preset", "slow",
                       # bang muc len DAU file: khong co thi trinh duyet phai
                       # tai het file moi phat duoc
                       "-movflags", "+faststart"])
    w.send(None)
    for i in range(n):
        c0 = _cuong_do(i / FPS, nhip, kieu)      # 0..1, dung de noi tat<->sang
        c = c0 * manh                             # cuong do quang sang
        # buoc 1: noi giua ban DEN TAT va ban goc theo nhip
        khung = nen_tat + (nen - nen_tat) * c0
        # buoc 2: cong quang sang theo SCREEN. 255-(255-a)(255-b)/255 - giu net
        # ben duoi, khac han voi cong thang (cong thang thi chay trang bet).
        if c > 0.001:
            b = np.clip(qa * c, 0, 255)
            khung = 255.0 - (255.0 - khung) * (255.0 - b) / 255.0
        w.send(np.clip(khung, 0, 255).astype(np.uint8).tobytes())
    w.close()
    kb = os.path.getsize(dich) / 1024
    print(f"XONG -> {dich}  ({kb:.0f} KB, {giay:.2f}s, "
          f"{im.size[0]}x{im.size[1]})")
    if poster:
        # Anh poster = frame sang nhat. Trang web can no de hien ngay truoc khi
        # video tai xong; thieu poster thi hero la mot o den trong vai tram ms.
        c = manh
        b = np.clip(qa * c, 0, 255)
        pf = 255.0 - (255.0 - nen) * (255.0 - b) / 255.0
        pp = os.path.splitext(dich)[0] + "-poster.jpg"
        Image.fromarray(np.clip(pf, 0, 255).astype(np.uint8)).save(
            pp, quality=82, optimize=True, progressive=True)
        print(f"       poster -> {pp}  "
              f"({os.path.getsize(pp)/1024:.0f} KB)")
    return dich


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("anh")
    ap.add_argument("--vung", action="append", default=[],
                    help="x0,y0,x1,y1 theo TI LE 0..1. Lap lai duoc nhieu lan.")
    ap.add_argument("--tu-tim", action="store_true", help="tu tim vung sang nhat")
    ap.add_argument("--so", type=int, default=1, help="so vung khi --tu-tim")
    ap.add_argument("--giay", type=float, default=4.0)
    ap.add_argument("--nhip", type=float, default=1.2,
                    help="giay cho mot lan bat-tat")
    ap.add_argument("--kieu", choices=["nhay", "lien"], default="nhay")
    ap.add_argument("--manh", type=float, default=1.6)
    ap.add_argument("--mau", help="R,G,B nhuom quang sang, vd 255,240,180")
    ap.add_argument("--nguyen", action="store_true",
                    help="giu nguyen ti le anh thay vi dat vao khung doc")
    ap.add_argument("--khong-tat", action="store_true",
                    help="chi cong quang sang, khong keo toi den o day nhip")
    ap.add_argument("--toi", type=float, default=0.22,
                    help="do sang con lai khi den TAT (0=den han, 1=nhu goc)")
    ap.add_argument("--crf", type=int, default=18,
                    help="18 = net, 26-30 = nhe hon nhieu (dung cho hero web)")
    ap.add_argument("--lap", action="store_true",
                    help="cat thoi luong ve so nguyen chu ky -> lap khong nhay")
    ap.add_argument("--poster", action="store_true",
                    help="xuat kem anh poster JPG cho the <video poster=...>")
    ap.add_argument("-o", "--out")
    a = ap.parse_args()

    if not os.path.exists(a.anh):
        raise SystemExit(f"khong thay anh: {a.anh}")
    if a.tu_tim or not a.vung:
        vung = tu_tim_vung(_doc_anh(a.anh, a.nguyen), a.so)
        print("vung tu tim:", [tuple(round(v, 3) for v in x) for x in vung])
    else:
        vung = []
        for v in a.vung:
            p = [float(x) for x in v.split(",")]
            if len(p) != 4:
                raise SystemExit(f"--vung phai co 4 so: {v}")
            vung.append(tuple(p))
    mau = tuple(int(x) for x in a.mau.split(",")) if a.mau else None
    lam_video(a.anh, vung, a.giay, a.nhip, a.kieu, a.manh, mau, a.nguyen,
              a.out, tat=not a.khong_tat, toi=a.toi, crf=a.crf, lap=a.lap,
              poster=a.poster)


if __name__ == "__main__":
    main()
